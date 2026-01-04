"""n
Issue Router - Route issues to Apprentices or Sentinels based on labels.

Routing logic:
- good-first-issue (no triage-needed) → Apprentices Discord channel
- triage-needed → Skip (needs maintainer review first)
- Other issues → Assign to available Sentinel
"""

import argparse
import sys
import os
import json
from typing import Dict, Any

sys.path.append(os.path.dirname(__file__))
from utils import load_config, write_output_file


def should_route_to_apprentices(labels: list) -> Dict[str, Any]:
    """
    Determine if issue should go to Apprentices channel.
    
    Criteria:
    - Has "good-first-issue" label
    - Does NOT have "triage-needed" label
    
    Edge cases:
    - Multiple labels
    - Label case sensitivity
    - Missing labels
    """
    # Normalize labels to lowercase
    labels_lower = [label.lower() for label in labels]
    
    has_good_first_issue = 'good-first-issue' in labels_lower or 'good first issue' in labels_lower
    has_triage_needed = 'triage-needed' in labels_lower or 'triage needed' in labels_lower
    
    if has_good_first_issue and not has_triage_needed:
        return {
            'route_to': 'apprentices',
            'reason': 'Good first issue without triage needed'
        }
    elif has_triage_needed:
        return {
            'route_to': 'skip',
            'reason': 'Needs triage first'
        }
    else:
        return {
            'route_to': 'sentinel',
            'reason': 'Regular issue for Sentinel assignment'
        }


def main():
    parser = argparse.ArgumentParser(description='Route issues to appropriate audience')
    parser.add_argument('--action', choices=['route', 'escalate_to_knights'], default='route')
    parser.add_argument('--issue-labels', help='Issue labels (JSON array)')
    parser.add_argument('--repo-name', help='Repository name')
    parser.add_argument('--issue-number', type=int, help='Issue number')
    parser.add_argument('--github-token', help='GitHub token')
    parser.add_argument('--output-file', default='output.json')
    
    args = parser.parse_args()
    
    try:
        if args.action == 'route':
            labels = json.loads(args.issue_labels) if args.issue_labels else []
            result = should_route_to_apprentices(labels)
            write_output_file(args.output_file, result)
            print(f"Route decision: {result}")
        
        elif args.action == 'escalate_to_knights':
            from github import Github
            g = Github(args.github_token)
            repo = g.get_repo(args.repo_name)
            issue = repo.get_issue(args.issue_number)
            
            # Add label
            issue.add_to_labels('needs-knight-attention')
            
            # Add comment
            comment = """⚠️ **No Sentinels Available**

This issue has been escalated to Knights for manual assignment as no Sentinels are currently available.

@knights - Please review and assign."""
            
            issue.create_comment(comment)
            print(f"✓ Escalated issue #{args.issue_number} to Knights")
        
    except Exception as e:
        print(f"Error: {e}")
        write_output_file(args.output_file, {'error': str(e)})
        sys.exit(1)


if __name__ == '__main__':
    main()
