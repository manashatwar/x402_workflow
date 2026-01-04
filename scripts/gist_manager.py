"""n
Gist Manager - CRUD operations for contributor TOML files in Gist.

Actions:
- create: Create new contributor entry (onboarding)
- update_pr: Add new PR to existing contributor
- promote_to_sentinel: Update role from Apprentice to Sentinel
- add_manual_assignment: Track manually assigned issues
- add_auto_assignment: Track auto-assigned issues (Sentinel)
"""

import argparse
import sys
import os
import subprocess
import toml
from datetime import datetime
from typing import Dict, Any

sys.path.append(os.path.dirname(__file__))
from utils import (
    load_config, sanitize_filename, calculate_deadline,
    calculate_lines_changed, write_output_file
)


class GistManager:
    """
    Manages contributor TOML files stored in a GitHub Gist.
    Handles cloning, updating, and committing changes.
    """
    def __init__(self, gist_pat: str):
        self.gist_pat = gist_pat
        self.config = load_config()
        self.gist_url = self.config['gist']['registry_url']
        self.repo_dir = None
    
    def clone_repo(self):
        """Clone or pull latest from Gist repository to temp directory."""
        import tempfile
        
        self.repo_dir = os.path.join(tempfile.gettempdir(), 'aossie_gist_repo')
        
        if os.path.exists(self.repo_dir):
            subprocess.run(['git', '-C', self.repo_dir, 'pull'], 
                          check=True, capture_output=True)
        else:
            auth_url = self.gist_url.replace('https://', f'https://{self.gist_pat}@')
            subprocess.run(['git', 'clone', auth_url, self.repo_dir], 
                          check=True, capture_output=True)
    
    def get_toml_path(self, username: str) -> str:
        """Get path to user's TOML file."""
        pattern = self.config['gist']['contributor_file_pattern']
        sanitized = sanitize_filename(username)
        filename = pattern.replace('{username}', sanitized)
        return os.path.join(self.repo_dir, filename)
    
    def create_contributor(self, username: str, discord_id: str, wallet: str,
                          repo_name: str, pr_number: int, lines_changed: int = 0,
                          discord_verified: bool = True) -> bool:
        """
        Create new contributor TOML file.
        
        Parameters:
            discord_verified: Set to False if Discord role assignment failed
        
        Edge cases:
        - File already exists (skip)
        - Invalid data
        - Git push conflicts
        """
        try:
            self.clone_repo()
            filepath = self.get_toml_path(username)
            
            if os.path.exists(filepath):
                print(f"Contributor {username} already exists")
                return False
            
            # Create initial TOML structure
            data = {
                'schema_version': self.config['gist']['schema_version'],
                'github': {
                    'login': username
                },
                'discord': {
                    'user_id': discord_id,
                    'verified': discord_verified
                },
                'wallet': {
                    'address': wallet,
                    'verified': False
                },
                'stats': {
                    'total_prs': 1,
                    'avg_lines_changed': 0,
                    'issues_resolved': 0,
                    'issues_stale': 0
                },
                'status': {
                    'assigned': False,
                    'current_role': 'Apprentice',
                    'blocked': False
                },
                'assignments': [],
                'manual_assignments': [],
                'prs': [
                    {
                        'repo': repo_name,
                        'pr_number': pr_number,
                        'lines_changed': lines_changed,
                        'labels': ['first-time-contributor']
                    }
                ]
            }
            
            # Write TOML file
            with open(filepath, 'w') as f:
                toml.dump(data, f)
            
            # Git commit and push
            subprocess.run(['git', '-C', self.repo_dir, 'add', filepath], check=True)
            subprocess.run(['git', '-C', self.repo_dir, 'commit', '-m', 
                           f'Add contributor: {username}'], check=True)
            subprocess.run(['git', '-C', self.repo_dir, 'push'], check=True)
            
            print(f"✓ Created contributor: {username}")
            return True
        
        except Exception as e:
            print(f"✗ Error creating contributor: {e}")
            return False
    
    def update_pr_stats(self, username: str, repo_name: str, pr_number: int,
                       lines_changed: int, labels: list,
                       counts_toward_promotion: bool) -> bool:
        """
        Add PR to contributor's history and update stats.
        
        Edge cases:
        - Duplicate PR entry
        - TOML file corrupted
        - Concurrent updates
        """
        try:
            self.clone_repo()
            filepath = self.get_toml_path(username)
            
            if not os.path.exists(filepath):
                print(f"Contributor {username} not found")
                return False
            
            with open(filepath, 'r') as f:
                data = toml.load(f)
            
            # Check for duplicate
            existing_pr = [pr for pr in data.get('prs', []) 
                          if pr['repo'] == repo_name and pr['pr_number'] == pr_number]
            if existing_pr:
                print(f"PR #{pr_number} already recorded")
                return False
            
            # Add new PR entry
            new_pr = {
                'repo': repo_name,
                'pr_number': pr_number,
                'lines_changed': lines_changed,
                'labels': labels
            }
            
            if 'prs' not in data:
                data['prs'] = []
            data['prs'].append(new_pr)
            
            # Update stats
            stats = data.get('stats', {})
            stats['total_prs'] = stats.get('total_prs', 0) + 1
            
            # Recalculate avg lines
            all_lines = [pr['lines_changed'] for pr in data['prs']]
            stats['avg_lines_changed'] = sum(all_lines) // len(all_lines) if all_lines else 0
            
            data['stats'] = stats
            
            # Write back
            with open(filepath, 'w') as f:
                toml.dump(data, f)
            
            # Git commit and push
            subprocess.run(['git', '-C', self.repo_dir, 'add', filepath], check=True)
            subprocess.run(['git', '-C', self.repo_dir, 'commit', '-m',
                           f'Update {username}: PR #{pr_number}'], check=True)
            subprocess.run(['git', '-C', self.repo_dir, 'push'], check=True)
            
            print(f"✓ Updated stats for {username}")
            return True
        
        except Exception as e:
            print(f"✗ Error updating PR stats: {e}")
            return False
    
    def promote_to_sentinel(self, username: str) -> bool:
        """Promote Apprentice to Sentinel."""
        try:
            self.clone_repo()
            filepath = self.get_toml_path(username)
            
            with open(filepath, 'r') as f:
                data = toml.load(f)
            
            data['status']['current_role'] = 'Sentinel'
            
            with open(filepath, 'w') as f:
                toml.dump(data, f)
            
            subprocess.run(['git', '-C', self.repo_dir, 'add', filepath], check=True)
            subprocess.run(['git', '-C', self.repo_dir, 'commit', '-m',
                           f'Promote {username} to Sentinel'], check=True)
            subprocess.run(['git', '-C', self.repo_dir, 'push'], check=True)
            
            print(f"✓ Promoted {username} to Sentinel")
            return True
        
        except Exception as e:
            print(f"✗ Error promoting: {e}")
            return False
    
    def assign_issue_to_sentinel(self, username: str, repo_name: str, 
                                issue_number: int, assigned_at: str) -> bool:
        """Add auto-assignment to Sentinel (with deadline tracking)."""
        try:
            self.clone_repo()
            filepath = self.get_toml_path(username)
            
            with open(filepath, 'r') as f:
                data = toml.load(f)
            
            deadline = calculate_deadline(assigned_at)
            
            # Initialize arrays if not present
            if 'assignments' not in data:
                data['assignments'] = []
            if 'manual_assignments' not in data:
                data['manual_assignments'] = []
            
            # Add to assignments array
            new_assignment = {
                'issue_url': f"{repo_name}#{issue_number}",
                'assigned_at': assigned_at,
                'deadline': deadline,
                'knight_override': False
            }
            data['assignments'].append(new_assignment)
            
            # Update assigned status
            total_assignments = len(data['assignments']) + len(data['manual_assignments'])
            data['status']['assigned'] = total_assignments > 0
            
            with open(filepath, 'w') as f:
                toml.dump(data, f)
            
            subprocess.run(['git', '-C', self.repo_dir, 'add', filepath], check=True)
            subprocess.run(['git', '-C', self.repo_dir, 'commit', '-m',
                           f'Assign issue {repo_name}#{issue_number} to {username}'], check=True)
            subprocess.run(['git', '-C', self.repo_dir, 'push'], check=True)
            
            print(f"✓ Assigned issue to {username}")
            return True
        
        except Exception as e:
            print(f"✗ Error assigning issue: {e}")
            return False
    
    def add_manual_assignment(self, username: str, repo_name: str,
                            issue_number: int, assigned_at: str) -> bool:
        """Add manual assignment (no deadline tracking)."""
        try:
            self.clone_repo()
            filepath = self.get_toml_path(username)
            
            with open(filepath, 'r') as f:
                data = toml.load(f)
            
            # Initialize arrays if not present
            if 'assignments' not in data:
                data['assignments'] = []
            if 'manual_assignments' not in data:
                data['manual_assignments'] = []
            
            # Add to manual_assignments array
            new_assignment = {
                'issue_url': f"{repo_name}#{issue_number}",
                'assigned_at': assigned_at
            }
            data['manual_assignments'].append(new_assignment)
            
            # Update assigned status
            total_assignments = len(data['assignments']) + len(data['manual_assignments'])
            data['status']['assigned'] = total_assignments > 0
            
            with open(filepath, 'w') as f:
                toml.dump(data, f)
            
            subprocess.run(['git', '-C', self.repo_dir, 'add', filepath], check=True)
            subprocess.run(['git', '-C', self.repo_dir, 'commit', '-m',
                           f'Manual assign issue {repo_name}#{issue_number} to {username}'], check=True)
            subprocess.run(['git', '-C', self.repo_dir, 'push'], check=True)
            
            print(f"✓ Added manual assignment to {username}")
            return True
        
        except Exception as e:
            print(f"✗ Error adding manual assignment: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description='Manage contributor TOML files in Gist')
    parser.add_argument('--action', required=True,
                       choices=['create', 'update_pr', 'promote_to_sentinel',
                               'assign_issue_to_sentinel', 'add_manual_assignment'])
    parser.add_argument('--gist-pat', required=True, help='Gist PAT')
    parser.add_argument('--username', help='GitHub username')
    parser.add_argument('--discord-id', help='Discord user ID')
    parser.add_argument('--discord-verified', type=str, default='true',
                       help='Discord verification status (true/false)')
    parser.add_argument('--wallet', help='Wallet address')
    parser.add_argument('--repo-name', help='Repository name')
    parser.add_argument('--pr-number', type=int, help='PR number')
    parser.add_argument('--issue-number', type=int, help='Issue number')
    parser.add_argument('--assigned-at', help='Issue assigned timestamp')
    parser.add_argument('--lines-changed', type=int, help='Lines changed')
    parser.add_argument('--labels', help='PR labels (JSON)')
    parser.add_argument('--counts-toward-promotion', help='Does PR count?', default='true')
    
    args = parser.parse_args()
    
    try:
        manager = GistManager(args.gist_pat)
        
        if args.action == 'create':
            lines = args.lines_changed if args.lines_changed else 0
            discord_verified = getattr(args, 'discord_verified', 'true').lower() == 'true'
            manager.create_contributor(args.username, args.discord_id, args.wallet,
                                      args.repo_name, args.pr_number, lines, discord_verified)
        
        elif args.action == 'update_pr':
            import json
            labels = json.loads(args.labels) if args.labels else []
            counts = args.counts_toward_promotion.lower() == 'true'
            manager.update_pr_stats(args.username, args.repo_name, args.pr_number,
                                   args.lines_changed, labels, counts)
        
        elif args.action == 'promote_to_sentinel':
            manager.promote_to_sentinel(args.username)
        
        elif args.action == 'assign_issue_to_sentinel':
            manager.assign_issue_to_sentinel(args.username, args.repo_name,
                                            args.issue_number, args.assigned_at)
        
        elif args.action == 'add_manual_assignment':
            manager.add_manual_assignment(args.username, args.repo_name,
                                         args.issue_number, args.assigned_at)
        
        print("✓ Gist operation completed")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
