from datetime import datetime, timezone, timedelta
from collections import defaultdict
from typing import Dict, Any, List
from tqdm import tqdm

# We expect a PyGithub Github instance
def fetch_profile_bundle(gh, username: str) -> Dict[str, Any]:
    user = gh.get_user(username)

    # Basic profile info
    profile = {
        "login": user.login,
        "name": user.name,
        "followers": user.followers,
        "following": user.following,
        "public_repos": user.public_repos,
        "created_at": user.created_at.replace(tzinfo=timezone.utc) if user.created_at.tzinfo is None else user.created_at,
    }

    # Repos: limit to 20 most recently updated to stay fast
    repos = list(user.get_repos(sort="updated")[:20])

    repo_info = []
    all_commits = []  # (created_at, message) tuples
    languages_counter = defaultdict(int)

    for r in tqdm(repos, desc="repos", leave=False):
        try:
            repo_info.append({
                "name": r.name,
                "fork": r.fork,
                "stargazers_count": r.stargazers_count,
                "created_at": r.created_at,
                "pushed_at": r.pushed_at,
            })
        except Exception:
            continue

        # Languages (approx) — sum across repos
        try:
            langs = r.get_languages() or {}
            for k, v in langs.items():
                languages_counter[k] += v
        except Exception:
            pass

        # Commits: cap to ~50 recent from default branch
        try:
            default_branch = r.default_branch or "main"
            commits = r.get_commits(sha=default_branch)[:50]
            for c in commits:
                try:
                    dt = c.commit.author.date
                    msg = (c.commit.message or "").strip()
                    all_commits.append((dt, msg))
                except Exception:
                    continue
        except Exception:
            continue

    # Public events (for collaboration ratio proxy) – cap to 100
    collab_events = 0
    try:
        events = user.get_public_events()[:100]
        for e in events:
            t = e.type or ""
            if t in ("IssuesEvent", "PullRequestEvent", "PullRequestReviewCommentEvent", "IssueCommentEvent"):
                collab_events += 1
    except Exception:
        pass

    bundle = {
        "profile": profile,
        "repo_info": repo_info,
        "commit_samples": all_commits,
        "languages_counter": dict(languages_counter),
        "collab_events": collab_events,
    }
    return bundle
