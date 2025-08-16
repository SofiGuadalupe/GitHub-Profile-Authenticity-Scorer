# GPAS — GitHub Profile Authenticity Scorer

A tiny, explainable **algorithm-based** tool that scores a GitHub profile’s likely authenticity (0–100) from public signals.  
**Educational only. Signals ≠ proof. Use responsibly.**

## Quickstart
```bash
# 1) Create a virtual env (optional) and install
pip install -e .

# 2) Export a GitHub token (recommended to avoid low rate limits)
# Settings → Developer settings → Personal access tokens (fine-grained or classic)
export GITHUB_TOKEN=ghp_your_token_here

# 3) Run
gpas <github_username>
# Example
gpas torvalds
gpas torvalds --json
```

## What it checks (v0.1.0)
- **Forks ratio & originals** — mostly forks + very few originals → suspicious.
- **Commit burstiness** — lots of commits in tiny time windows.
- **Commit message variety** — too many identical/boilerplate messages.
- **Star spikes vs age** — sudden unusual star growth on young repos.
- **Heatmap entropy (proxy)** — contribution times overly uniform or clumped.
- **Collaboration ratio (approx.)** — issues/PR/reviews vs own commits.
- **Language diversity** — single-language spam across many forks.

*Planned:* code duplication across repos and ML anomaly model.

## Score (explainable)
Each rule can deduct points, with a human-readable explanation.
The final score is clamped to `[0, 100]`.

```text
-15 Mostly forks, very few originals
-10 Highly bursty commit pattern
-10 Low variety in commit messages
-10 Unnatural star spike vs repo age
-10 Contribution timing entropy is too low
-10 Very low collaboration activity
-10 Very low language diversity
```

## Install (editable dev) & Run
```bash
pip install -e .
gpas <username>
```

## Notes
- This uses conservative API limits: up to 20 repos and ~50 commits per repo, plus ~100 recent public events.
- Provide `GITHUB_TOKEN` to reduce rate limiting.
- **Ethics:** Do not harass individuals. Treat this as a research/learning tool.

## License
MIT
