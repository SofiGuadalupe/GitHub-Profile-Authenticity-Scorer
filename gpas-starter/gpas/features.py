import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple

def _normalize_msg(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^\w\s]", "", s)  # drop punctuation
    return s

def _shannon_entropy(probs: List[float]) -> float:
    eps = 1e-9
    return -sum(p * math.log2(p + eps) for p in probs if p > 0)

def compute_features(bundle: Dict[str, Any]) -> Dict[str, Any]:
    prof = bundle["profile"]
    repos = bundle["repo_info"]
    commits: List[Tuple[datetime, str]] = bundle["commit_samples"]
    langs_counter: Dict[str, int] = bundle["languages_counter"]
    collab_events = bundle.get("collab_events", 0)

    followers = prof.get("followers", 0)
    following = prof.get("following", 0)

    # Forks ratio & originals
    total = len(repos) or 1
    forks = sum(1 for r in repos if r.get("fork"))
    originals = total - forks
    forks_ratio = forks / total

    # Commit message uniqueness
    msgs = [_normalize_msg(m) for _, m in commits if m]
    total_msgs = len(msgs) or 1
    uniq_msgs = len(set(msgs))
    msg_uniqueness = uniq_msgs / total_msgs

    # Burstiness (max day share)
    day_bucket = Counter()
    hour_bucket = Counter()
    for dt, _ in commits:
        if not isinstance(dt, datetime):
            continue
        d = dt.date().isoformat()
        day_bucket[d] += 1
        hour_bucket[dt.hour] += 1
    commit_total = sum(day_bucket.values()) or 1
    commit_burst_index = (max(day_bucket.values()) / commit_total) if day_bucket else 0.0

    # Heatmap entropy proxy – hour-of-day distribution (0..24)
    total_hours = sum(hour_bucket.values()) or 1
    probs = [hour_bucket.get(h, 0) / total_hours for h in range(24)]
    heatmap_entropy_raw = _shannon_entropy(probs)
    # Normalize entropy to [0,1] approx (max entropy for 24 bins = log2(24) ≈ 4.585)
    heatmap_entropy = heatmap_entropy_raw / math.log2(24)

    # Stars spike zscore (stars normalized by age days)
    def _age_days(dt: datetime) -> float:
        if not isinstance(dt, datetime):
            return 0.0
        now = datetime.now(dt.tzinfo or timezone.utc)
        return max(1.0, (now - dt).days)
    rates = []
    for r in repos:
        stars = r.get("stargazers_count", 0) or 0
        age = _age_days(r.get("created_at"))
        rates.append(stars / age)
    stars_spike_z = 0.0
    if rates:
        mu = sum(rates)/len(rates)
        var = sum((x - mu)**2 for x in rates)/len(rates)
        sd = var**0.5
        if sd > 0:
            stars_spike_z = max((x - mu)/sd for x in rates)

    # Language diversity (unique langs / total langs observed)
    total_lang_tokens = sum(langs_counter.values()) or 1
    unique_langs = len([k for k, v in langs_counter.items() if v > 0])
    lang_diversity = unique_langs / max(1, unique_langs + (total_lang_tokens > 0))

    # Collaboration ratio: collab events vs commits
    collab_ratio = collab_events / max(1, collab_events + commit_total)

    feats = {
        "followers": followers,
        "following": following,
        "forks_ratio": forks_ratio,
        "original_repos": originals,
        "msg_uniqueness": round(msg_uniqueness, 4),
        "commit_burst_index": round(commit_burst_index, 4),
        "heatmap_entropy": round(heatmap_entropy, 4),
        "stars_spike_z": round(stars_spike_z, 3),
        "lang_diversity": round(lang_diversity, 4),
        "collab_ratio": round(collab_ratio, 4),
        "commit_count_sampled": commit_total,
        "repo_count_sampled": len(repos),
        "unique_languages": unique_langs,
    }
    return feats
