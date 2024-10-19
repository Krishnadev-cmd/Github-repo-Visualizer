from urllib.parse import urlparse
import re

def validate_github_url(url):
    """
    Validate GitHub repository URL and extract owner/repo.
    Returns (owner, repo_name) tuple if valid, raises ValueError if not.
    """
    if not url:
        raise ValueError("Please enter a GitHub repository URL")
        
    # Clean the URL
    url = url.strip().rstrip('/')
    
    # Parse URL
    parsed = urlparse(url)
    
    # Check if it's a GitHub URL
    if parsed.netloc != 'github.com':
        raise ValueError("Please enter a valid GitHub URL (https://github.com/owner/repo)")
    
    # Extract path components
    path_parts = [p for p in parsed.path.split('/') if p]
    
    # Check if we have owner/repo format
    if len(path_parts) < 2:
        raise ValueError("URL must be in format: https://github.com/owner/repo")
        
    owner, repo_name = path_parts[0], path_parts[1]
    
    # Validate owner and repo names
    if not re.match(r'^[\w.-]+$', owner) or not re.match(r'^[\w.-]+$', repo_name):
        raise ValueError("Invalid repository owner or name format")
        
    return owner, repo_name