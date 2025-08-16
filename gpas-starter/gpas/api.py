import os
from github import Github, Auth

def get_client():
    token = os.getenv("GITHUB_TOKEN")
    if token:
        auth = Auth.Token(token)
        return Github(auth=auth, per_page=100)
    # unauthenticated client (heavy rate limits)
    return Github(per_page=100)
