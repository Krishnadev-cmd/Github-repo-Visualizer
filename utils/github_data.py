from github import Github, GithubException
from typing import Optional, Tuple, List, Dict, Any

class GitHubDataFetcher:
    def __init__(self, token: Optional[str] = None):
        self.github = Github(token) if token else Github()
        
    def get_repository(self, owner: str, repo_name: str):
        """
        Safely fetch repository information.
        Raises appropriate exceptions with clear messages.
        """
        try:
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            # Test access by fetching basic info
            repo.name
            return repo
        except GithubException as e:
            if e.status == 404:
                raise ValueError(f"Repository '{owner}/{repo_name}' not found. Please check the URL and try again.")
            elif e.status == 401:
                raise ValueError("Invalid GitHub token. Please check your token and try again.")
            elif e.status == 403:
                if 'rate limit' in str(e).lower():
                    raise ValueError("GitHub API rate limit exceeded. Please add a GitHub token to increase the limit.")
                else:
                    raise ValueError("Access denied. Please check your permissions and token.")
            else:
                raise ValueError(f"GitHub API error: {str(e)}")

    def get_branch_data(self, repo) -> List[Dict[str, Any]]:
        """Fetch branch information from GitHub repository"""
        try:
            return [{
                'name': branch.name,
                'commit': branch.commit.sha,
                'protected': branch.protected
            } for branch in repo.get_branches()]
        except GithubException as e:
            raise ValueError(f"Error fetching branch data: {str(e)}")

    def get_commit_data(self, repo, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch commit information from GitHub repository"""
        try:
            return [{
                'sha': commit.sha,
                'message': commit.commit.message,
                'author': commit.commit.author.name,
                'date': commit.commit.author.date.strftime('%Y-%m-%d %H:%M:%S'),
                'parents': [p.sha for p in commit.parents]
            } for commit in repo.get_commits()[:limit]]
        except GithubException as e:
            raise ValueError(f"Error fetching commit data: {str(e)}")
