"""
Utility functions shared across automation scripts.
"""

import os
import json
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import toml


def load_config() -> Dict[str, Any]:
    """Load configuration from thresholds.toml."""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'thresholds.toml')
    with open(config_path, 'r') as f:
        return toml.load(f)


def load_error_messages() -> Dict[str, Any]:
    """Load error and success messages from JSON."""
    messages_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'edge_case_responses.json')
    with open(messages_path, 'r') as f:
        return json.load(f)


def validate_discord_id(discord_id: str) -> bool:
    """
    Validate Discord user ID format.
    
    Edge cases:
    - Must be 17-19 digit numeric string
    - No whitespace or special characters
    """
    if not discord_id:
        return False
    
    # Remove any whitespace
    discord_id = discord_id.strip()
    
    # Check if it's all digits
    if not discord_id.isdigit():
        return False
    
    # Check length (Discord snowflake IDs are 17-19 digits)
    config = load_config()
    min_len = config['onboarding']['discord_id_length_min']
    max_len = config['onboarding']['discord_id_length_max']
    
    return min_len <= len(discord_id) <= max_len


def validate_wallet_address(wallet: str) -> bool:
    """
    Validate Ethereum wallet address format.
    
    Edge cases:
    - Must start with 0x
    - Must be 42 characters total (0x + 40 hex chars)
    - Only hexadecimal characters
    """
    if not wallet:
        return False
    
    wallet = wallet.strip().lower()
    
    config = load_config()
    expected_prefix = config['onboarding']['wallet_address_prefix']
    expected_length = config['onboarding']['wallet_address_length']
    
    # Check prefix
    if not wallet.startswith(expected_prefix):
        return False
    
    # Check length
    if len(wallet) != expected_length:
        return False
    
    # Check if it's valid hex (after 0x)
    hex_part = wallet[2:]
    try:
        int(hex_part, 16)
        return True
    except ValueError:
        return False


def calculate_deadline(assigned_at: str, use_business_days: bool = True) -> str:
    """
    Calculate deadline from assignment date.
    
    Args:
        assigned_at: ISO format timestamp
        use_business_days: If True, exclude weekends
        
    Returns:
        ISO format deadline timestamp
        
    Edge cases:
    - Handles leap years
    - Excludes weekends if configured
    - Handles timezone conversion
    """
    config = load_config()
    deadline_days = config['sentinel']['deadline_days']
    
    assigned = datetime.fromisoformat(assigned_at.replace('Z', '+00:00'))
    
    if use_business_days:
        # Add business days (excluding weekends)
        days_added = 0
        current = assigned
        
        while days_added < deadline_days:
            current += timedelta(days=1)
            # Skip weekends (5 = Saturday, 6 = Sunday)
            if current.weekday() < 5:
                days_added += 1
        
        deadline = current
    else:
        # Simple calendar days
        deadline = assigned + timedelta(days=deadline_days)
    
    return deadline.isoformat()


def calculate_lines_changed(additions: int, deletions: int) -> int:
    """
    Calculate total lines changed.
    
    Edge cases:
    - Cap at maximum to prevent stat inflation from mass refactors
    - Handle negative values (shouldn't happen but defensive)
    """
    total = max(0, additions) + max(0, deletions)
    
    # Cap at 1000 for stats purposes
    return min(total, 1000)


def should_count_pr(labels: List[str], lines_changed: int, merged_to_branch: str) -> bool:
    """
    Determine if PR should count toward promotion.
    
    Edge cases:
    - Exclude automated PRs (dependencies, renovate)
    - Exclude trivial changes (< threshold lines)
    - Only count merges to main branches
    """
    config = load_config()
    
    # Check if merged to allowed branch
    allowed_branches = config['quality_gates']['allowed_merge_branches']
    if merged_to_branch not in allowed_branches:
        return False
    
    # Check for excluded labels
    excluded_labels = config['quality_gates']['exclude_pr_labels']
    if any(label in labels for label in excluded_labels):
        return False
    
    # Check minimum lines
    min_lines = config['quality_gates']['min_lines_for_count']
    if lines_changed < min_lines:
        return False
    
    return True


def retry_with_backoff(func, max_retries: int = 3, backoff_seconds: List[int] = [1, 2, 4]):
    """
    Retry a function with exponential backoff.
    
    Edge cases:
    - Network timeouts
    - Rate limits
    - Temporary API outages
    """
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            wait_time = backoff_seconds[min(attempt, len(backoff_seconds) - 1)]
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
            time.sleep(wait_time)


def sanitize_filename(username: str) -> str:
    """
    Sanitize GitHub username for use in filename.
    
    Edge cases:
    - Special characters
    - Case sensitivity
    - URL encoding
    """
    # Convert to lowercase
    username = username.lower()
    
    # Replace any non-alphanumeric characters (except dash and underscore)
    username = re.sub(r'[^a-z0-9_-]', '_', username)
    
    return username


def parse_discord_wallet_comment(comment_body: str) -> Optional[Dict[str, str]]:
    """
    Extract Discord ID and wallet address from PR comment.
    
    Supported formats:
    - Discord: 123456789012345678 | Wallet: 0x...
    - discord_id: 123456789012345678, wallet: 0x...
    - Just the IDs on separate lines
    
    Edge cases:
    - Multiple formats
    - Extra whitespace
    - Multiple IDs in comment (take first valid)
    - Case insensitive
    """
    if not comment_body:
        return None
    
    result = {}
    
    # Pattern 1: Discord: ID | Wallet: address
    pattern1 = r'discord[:\s]+(\d{17,19})'
    match = re.search(pattern1, comment_body, re.IGNORECASE)
    if match:
        result['discord_id'] = match.group(1)
    
    # Pattern 2: Wallet address
    pattern2 = r'(?:wallet|address)[:\s]+(0x[a-fA-F0-9]{40})'
    match = re.search(pattern2, comment_body, re.IGNORECASE)
    if match:
        result['wallet_address'] = match.group(1)
    
    # If both found, validate
    if 'discord_id' in result and 'wallet_address' in result:
        if validate_discord_id(result['discord_id']) and validate_wallet_address(result['wallet_address']):
            return result
    
    return None


def format_github_issue_url(repo_name: str, issue_number: int) -> str:
    """Format GitHub issue URL."""
    return f"https://github.com/{repo_name}/issues/{issue_number}"


def format_github_pr_url(repo_name: str, pr_number: int) -> str:
    """Format GitHub PR URL."""
    return f"https://github.com/{repo_name}/pull/{pr_number}"


def get_time_remaining(deadline: str) -> Dict[str, Any]:
    """
    Calculate time remaining until deadline.
    
    Returns:
        Dict with hours_remaining, days_remaining, is_overdue
    """
    now = datetime.utcnow()
    deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
    
    delta = deadline_dt - now
    
    return {
        'hours_remaining': max(0, int(delta.total_seconds() / 3600)),
        'days_remaining': max(0, delta.days),
        'is_overdue': delta.total_seconds() < 0,
        'delta_seconds': delta.total_seconds()
    }


def write_output_file(filename: str, data: Dict[str, Any]):
    """Write data to JSON output file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)


def is_business_day(date: datetime) -> bool:
    """Check if date is a business day (Monday-Friday)."""
    return date.weekday() < 5


def get_next_business_day(date: datetime) -> datetime:
    """Get next business day from given date."""
    next_day = date + timedelta(days=1)
    while not is_business_day(next_day):
        next_day += timedelta(days=1)
    return next_day
