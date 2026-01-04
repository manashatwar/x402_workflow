"""n
Sentinel Assigner - Find and assign issues to available Sentinels.

Logic:
- Finds Sentinels with capacity (< max_concurrent assignments)
- Excludes blocked Sentinels
- Randomly selects from available pool for fair distribution
- Calculates 5-day deadline from assignment
"""

import argparse
import sys
import os
import random
import toml
from typing import Dict, Any, Optional

sys.path.append(os.path.dirname(__file__))
from utils import load_config, write_output_file, calculate_deadline
from github import Github


def find_available_sentinel(gist_pat: str, max_concurrent: int = 1) -> Optional[Dict[str, Any]]:
    """
    Find a random available Sentinel from the registry.
    Returns Sentinel username, Discord ID, and assignment details.
    
    Selection criteria:
    - current_role = "Sentinel"
    - Total assignments (auto + manual) < max_concurrent
    - status.blocked = false
    
    Edge cases:
    - No Sentinels available → returns None
    - All Sentinels at capacity → returns None
    - Corrupted TOML files → skipped
    """
    import subprocess
    import tempfile
    
    try:
        # Clone Gist
        config = load_config()
        gist_url = config['gist']['registry_url']
        repo_dir = os.path.join(tempfile.gettempdir(), 'aossie_gist_repo')
        
        if os.path.exists(repo_dir):
            subprocess.run(['git', '-C', repo_dir, 'pull'], 
                          check=True, capture_output=True)
        else:
            auth_url = gist_url.replace('https://', f'https://{gist_pat}@')
            subprocess.run(['git', 'clone', auth_url, repo_dir], 
                          check=True, capture_output=True)
        
        # Find all TOML files
        available_sentinels = []
        
        for filename in os.listdir(repo_dir):
            if filename.startswith('contributor__') and filename.endswith('.toml'):
                filepath = os.path.join(repo_dir, filename)
                
                try:
                    with open(filepath, 'r') as f:
                        data = toml.load(f)
                    
                    status = data.get('status', {})
                    current_role = status.get('current_role', '')
                    blocked = status.get('blocked', False)
                    
                    # Count total assignments (auto + manual)
                    auto_assignments = len(data.get('assignments', []))
                    manual_assignments = len(data.get('manual_assignments', []))
                    total_assignments = auto_assignments + manual_assignments
                    
                    if current_role == 'Sentinel' and total_assignments < max_concurrent and not blocked:
                        available_sentinels.append({
                            'username': data['github']['login'],
                            'discord_id': data.get('discord', {}).get('user_id', ''),
                            'issues_resolved': data.get('stats', {}).get('issues_resolved', 0),
                            'current_load': total_assignments
                        })
                
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
                    continue
        
        if not available_sentinels:
            return None
        
        # Random selection
        selected = random.choice(available_sentinels)
        
        return {
            'found': True,
            'sentinel_username': selected['username'],
            'discord_id': selected['discord_id']
        }
    
    except Exception as e:
        print(f"Error finding Sentinel: {e}")
        return None


def assign_issue_to_sentinel(repo_name: str, issue_number: int, 
                             sentinel_username: str, github_token: str):
    """
    Assign GitHub issue to Sentinel.
    
    Edge cases:
    - Issue already assigned
    - Sentinel user not found
    - Permission errors
    """
    try:
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        issue = repo.get_issue(issue_number)
        
        # Assign to Sentinel
        issue.add_to_assignees(sentinel_username)
        
        print(f"✓ Assigned issue #{issue_number} to {sentinel_username}")
    
    except Exception as e:
        print(f"Error assigning issue: {e}")
        raise


def add_deadline_label(repo_name: str, issue_number: int, github_token: str):
    """
    Add deadline label to issue.
    
    Label format: "sentinel-deadline: YYYY-MM-DD"
    """
    try:
        from datetime import datetime, timedelta
        config = load_config()
        deadline_days = config['sentinel']['deadline_days']
        
        deadline_date = datetime.utcnow() + timedelta(days=deadline_days)
        deadline_str = deadline_date.strftime('%Y-%m-%d')
        
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        issue = repo.get_issue(issue_number)
        
        # Add label
        label_name = f"sentinel-deadline: {deadline_str}"
        issue.add_to_labels(label_name)
        
        print(f"✓ Added deadline label: {label_name}")
    
    except Exception as e:
        print(f"Error adding deadline label: {e}")


def main():
    parser = argparse.ArgumentParser(description='Assign issues to Sentinels')
    parser.add_argument('--action', required=True,
                       choices=['find_available', 'assign_issue', 'add_deadline_label'])
    parser.add_argument('--gist-pat', help='Gist PAT')
    parser.add_argument('--max-concurrent', type=int, default=1, help='Max concurrent assignments per Sentinel')
    parser.add_argument('--repo-name', help='Repository name')
    parser.add_argument('--issue-number', type=int, help='Issue number')
    parser.add_argument('--sentinel-username', help='Sentinel username')
    parser.add_argument('--github-token', help='GitHub token')
    parser.add_argument('--output-file', default='output.json')
    
    args = parser.parse_args()
    
    try:
        if args.action == 'find_available':
            result = find_available_sentinel(args.gist_pat, args.max_concurrent)
            if result:
                write_output_file(args.output_file, result)
            else:
                write_output_file(args.output_file, {'found': False})
            print(f"Result: {result}")
        
        elif args.action == 'assign_issue':
            assign_issue_to_sentinel(args.repo_name, args.issue_number,
                                    args.sentinel_username, args.github_token)
        
        elif args.action == 'add_deadline_label':
            add_deadline_label(args.repo_name, args.issue_number, args.github_token)
        
        print("✓ Sentinel assignment operation completed")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
