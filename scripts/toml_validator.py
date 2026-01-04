"""
TOML validator - Validate PR quality and TOML schema.
"""

import argparse
import json
import sys
import os
from typing import Dict, Any, List

sys.path.append(os.path.dirname(__file__))
from utils import load_config, should_count_pr, write_output_file


def validate_pr_quality(lines_changed: int, labels: List[str], 
                        merged_to_branch: str = 'main') -> Dict[str, Any]:
    """
    Validate if PR meets quality standards.
    
    Edge cases:
    - Automated dependency updates
    - Trivial changes (whitespace only)
    - Merges to non-default branches
    - Bot-generated PRs
    """
    counts = should_count_pr(labels, lines_changed, merged_to_branch)
    
    return {
        'counts_toward_promotion': counts,
        'lines_changed': lines_changed,
        'reason': 'Meets quality standards' if counts else 'Does not meet quality standards'
    }


def validate_toml_schema(toml_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate TOML data against schema.
    
    Required fields:
    - schema_version
    - github.login
    - stats.total_prs
    - status.assigned
    - status.current_role
    """
    errors = []
    
    # Check required fields
    if 'schema_version' not in toml_data:
        errors.append("Missing schema_version")
    
    if 'github' not in toml_data or 'login' not in toml_data.get('github', {}):
        errors.append("Missing github.login")
    
    if 'stats' not in toml_data:
        errors.append("Missing stats section")
    
    if 'status' not in toml_data:
        errors.append("Missing status section")
    
    # Validate status fields
    status = toml_data.get('status', {})
    if 'assigned' not in status:
        errors.append("Missing status.assigned")
    
    if 'current_role' not in status:
        errors.append("Missing status.current_role")
    elif status['current_role'] not in ['Apprentice', 'Sentinel']:
        errors.append(f"Invalid role: {status['current_role']}")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def main():
    parser = argparse.ArgumentParser(description='Validate PR quality and TOML schema')
    parser.add_argument('--action', choices=['validate_pr_quality', 'validate_schema'], 
                       required=True)
    parser.add_argument('--lines-changed', type=int, help='Total lines changed (additions + deletions)')
    parser.add_argument('--labels', help='PR labels (JSON array string)')
    parser.add_argument('--merged-to-branch', default='main', help='Branch PR was merged to')
    parser.add_argument('--toml-file', help='Path to TOML file to validate')
    parser.add_argument('--output-file', default='output.json')
    
    args = parser.parse_args()
    
    try:
        if args.action == 'validate_pr_quality':
            labels = json.loads(args.labels) if args.labels else []
            result = validate_pr_quality(args.lines_changed, labels, 
                                        args.merged_to_branch)
        
        elif args.action == 'validate_schema':
            import toml
            with open(args.toml_file, 'r') as f:
                toml_data = toml.load(f)
            result = validate_toml_schema(toml_data)
        
        write_output_file(args.output_file, result)
        print(f"Validation result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
        write_output_file(args.output_file, {'error': str(e), 'valid': False})
        sys.exit(1)


if __name__ == '__main__':
    main()
