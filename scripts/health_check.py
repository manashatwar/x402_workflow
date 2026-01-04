"""
Health check - Monitor Sentinel assignments and enforce deadlines.
"""

import argparse
import sys
import os
import toml
import json
import subprocess
import tempfile
from datetime import datetime
from typing import Dict, Any, List

sys.path.append(os.path.dirname(__file__))
from utils import load_config, get_time_remaining, write_output_file
from github import Github


class HealthChecker:
    def __init__(self, gist_pat: str, github_token: str):
        self.gist_pat = gist_pat
        self.github_token = github_token
        self.config = load_config()
        self.github = Github(github_token)
        self.repo_dir = None
        
        self.freed_count = 0
        self.reassigned_count = 0
        self.escalated_count = 0
        self.warnings_sent = 0
    
    def clone_gist(self):
        """Clone Gist repository."""
        gist_url = self.config['gist']['registry_url']
        self.repo_dir = os.path.join(tempfile.gettempdir(), 'aossie_gist_repo')
        
        if os.path.exists(self.repo_dir):
            subprocess.run(['git', '-C', self.repo_dir, 'pull'], 
                          check=True, capture_output=True)
        else:
            auth_url = gist_url.replace('https://', f'https://{self.gist_pat}@')
            subprocess.run(['git', 'clone', auth_url, self.repo_dir], 
                          check=True, capture_output=True)
    
    def get_all_sentinels(self) -> List[Dict[str, Any]]:
        """Get all Sentinels with active auto-assignments (ignores manual assignments)."""
        sentinels = []
        
        for filename in os.listdir(self.repo_dir):
            if filename.startswith('contributor__') and filename.endswith('.toml'):
                filepath = os.path.join(self.repo_dir, filename)
                
                try:
                    with open(filepath, 'r') as f:
                        data = toml.load(f)
                    
                    # Only process Sentinels with auto-assignments (not manual)
                    assignments = data.get('assignments', [])
                    
                    if len(assignments) > 0:
                        sentinels.append({
                            'username': data['github']['login'],
                            'filepath': filepath,
                            'data': data
                        })
                
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
        
        return sentinels
    
    def check_issue_status(self, issue_url: str) -> Dict[str, Any]:
        """
        Check GitHub issue status.
        
        Returns:
            Dict with 'open', 'closed', 'has_time_taken_label'
        """
        try:
            # Parse issue_url: "owner/repo#123"
            parts = issue_url.split('#')
            repo_name = parts[0]
            issue_number = int(parts[1])
            
            repo = self.github.get_repo(repo_name)
            issue = repo.get_issue(issue_number)
            
            # Check for time-taken label
            labels = [label.name.lower() for label in issue.labels]
            has_time_taken = 'time-taken' in labels
            
            return {
                'open': issue.state == 'open',
                'closed': issue.state == 'closed',
                'has_time_taken_label': has_time_taken,
                'issue': issue
            }
        
        except Exception as e:
            print(f"Error checking issue {issue_url}: {e}")
            return {
                'open': False,
                'closed': False,
                'has_time_taken_label': False,
                'error': str(e)
            }
    
    def free_sentinel(self, sentinel: Dict[str, Any], assignment: Dict[str, Any]):
        """Free Sentinel from a specific assignment."""
        data = sentinel['data']
        
        # Remove from assignments array
        if 'assignments' in data:
            data['assignments'] = [a for a in data['assignments'] 
                                  if a.get('issue_url') != assignment.get('issue_url')]
        
        # Update assigned status based on total remaining assignments
        total_assignments = len(data.get('assignments', [])) + len(data.get('manual_assignments', []))
        data['status']['assigned'] = total_assignments > 0
        
        # Update stats
        stats = data.get('stats', {})
        stats['issues_resolved'] = stats.get('issues_resolved', 0) + 1
        data['stats'] = stats
        
        # Write back
        with open(sentinel['filepath'], 'w') as f:
            toml.dump(data, f)
        
        self.freed_count += 1
        print(f"✓ Freed Sentinel {sentinel['username']} from {assignment.get('issue_url', '')}")
    
    def reassign_issue(self, sentinel: Dict[str, Any], assignment: Dict[str, Any]):
        """Reassign overdue issue to another Sentinel."""
        data = sentinel['data']
        issue_url = assignment.get('issue_url', '')
        
        # Update stale count
        stats = data.get('stats', {})
        stats['issues_stale'] = stats.get('issues_stale', 0) + 1
        data['stats'] = stats
        
        # Remove from assignments array
        if 'assignments' in data:
            data['assignments'] = [a for a in data['assignments'] 
                                  if a.get('issue_url') != issue_url]
        
        # Update assigned status
        total_assignments = len(data.get('assignments', [])) + len(data.get('manual_assignments', []))
        data['status']['assigned'] = total_assignments > 0
        
        with open(sentinel['filepath'], 'w') as f:
            toml.dump(data, f)
        
        self.reassigned_count += 1
        print(f"✓ Reassigned issue {issue_url} from {sentinel['username']}")
    
    def process_sentinel(self, sentinel: Dict[str, Any]):
        """
        Process single Sentinel health check for all auto-assignments.
        Skips manual_assignments (no deadline tracking).
        
        Edge cases:
        - Issue closed by someone else
        - Knight added "time-taken" label (skip deadline check)
        - Issue deleted/transferred
        - Sentinel went inactive
        """
        username = sentinel['username']
        data = sentinel['data']
        assignments = data.get('assignments', [])
        
        if not assignments:
            return
        
        print(f"Checking Sentinel {username} - {len(assignments)} auto-assignment(s)")
        
        # Process each assignment
        for assignment in assignments[:]:
            issue_url = assignment.get('issue_url', '')
            deadline = assignment.get('deadline', '')
            knight_override = assignment.get('knight_override', False)
            
            print(f"  Checking Issue: {issue_url}")
            
            # Check issue status
            issue_status = self.check_issue_status(issue_url)
            
            # Handle Knight override (time-taken label)
            if issue_status.get('has_time_taken_label', False):
                if not knight_override:
                    # Mark as overridden, skip deadline tracking
                    assignment['knight_override'] = True
                    with open(sentinel['filepath'], 'w') as f:
                        toml.dump(data, f)
                    print(f"    ⏸️  Knight override detected - deadline tracking paused")
                continue
            
            # If issue is closed, free Sentinel
            if issue_status.get('closed', False):
                self.free_sentinel(sentinel, assignment)
                continue
            
            # Check deadline
            time_info = get_time_remaining(deadline)
            
            if time_info['is_overdue']:
                # Deadline passed - reassign
                print(f"    ⏰ Deadline passed by {abs(time_info['hours_remaining'])} hours")
                self.reassign_issue(sentinel, assignment)
            
            elif time_info['hours_remaining'] <= 72:
                # Send warning (3 days before deadline)
                print(f"    ⚠️  Warning: {time_info['hours_remaining']} hours remaining")
                self.send_deadline_warning(sentinel, issue_status.get('issue'), time_info)
                self.warnings_sent += 1
    
    def send_deadline_warning(self, sentinel: Dict[str, Any], issue, time_info: Dict[str, Any]):
        """Send deadline approaching warning (3 days before)."""
        try:
            if issue:
                days_remaining = time_info['hours_remaining'] // 24
                hours_remaining = time_info['hours_remaining'] % 24
                
                time_msg = f"{days_remaining} day(s)"
                if hours_remaining > 0:
                    time_msg += f" and {hours_remaining} hour(s)"
                
                comment = f"""⏰ **Deadline Reminder**

@{sentinel['username']}, this issue has {time_msg} remaining until deadline.

Need help? Add `help-wanted` label or reach out in Discord.
Unexpected complexity? Ask a Knight to add `time-taken` label for extended time."""
                
                issue.create_comment(comment)
        
        except Exception as e:
            print(f"Error sending warning: {e}")
    
    def run_health_check(self) -> Dict[str, Any]:
        """
        Run complete health check on all Sentinels.
        
        Returns:
            Summary report
        """
        self.clone_gist()
        sentinels = self.get_all_sentinels()
        
        print(f"Found {len(sentinels)} assigned Sentinels")
        
        for sentinel in sentinels:
            try:
                self.process_sentinel(sentinel)
            except Exception as e:
                print(f"Error processing {sentinel['username']}: {e}")
        
        # Commit all changes
        if self.freed_count > 0 or self.reassigned_count > 0:
            subprocess.run(['git', '-C', self.repo_dir, 'add', '.'], check=True)
            subprocess.run(['git', '-C', self.repo_dir, 'commit', '-m',
                           f'Health check: freed {self.freed_count}, reassigned {self.reassigned_count}'],
                          check=True)
            subprocess.run(['git', '-C', self.repo_dir, 'push'], check=True)
        
        return {
            'sentinels_freed': self.freed_count,
            'issues_reassigned': self.reassigned_count,
            'issues_escalated': self.escalated_count,
            'warnings_sent': self.warnings_sent,
            'total_checked': len(sentinels)
        }


def main():
    parser = argparse.ArgumentParser(description='Sentinel health check')
    parser.add_argument('--gist-pat', required=True, help='Gist PAT')
    parser.add_argument('--github-token', required=True, help='GitHub token')
    parser.add_argument('--repo-name', help='Specific repo to check (optional)')
    parser.add_argument('--output-file', default='health_report.json')
    
    args = parser.parse_args()
    
    try:
        checker = HealthChecker(args.gist_pat, args.github_token)
        report = checker.run_health_check()
        
        write_output_file(args.output_file, report)
        
        print("\n" + "="*50)
        print("HEALTH CHECK REPORT")
        print("="*50)
        print(f"Sentinels freed: {report['sentinels_freed']}")
        print(f"Issues reassigned: {report['issues_reassigned']}")
        print(f"Issues escalated: {report['issues_escalated']}")
        print(f"Warnings sent: {report['warnings_sent']}")
        print(f"Total checked: {report['total_checked']}")
        print("="*50)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
