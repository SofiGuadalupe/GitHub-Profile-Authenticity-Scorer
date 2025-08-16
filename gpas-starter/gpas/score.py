from typing import Dict, Tuple, List

def compute_score(f: Dict[str, float]) -> Tuple[int, List[str]]:
    score = 100
    reasons: List[str] = []

    def penalize(cond: bool, pts: int, msg: str):
        nonlocal score
        if cond:
            score -= pts
            reasons.append(f"-{pts} {msg}")

    penalize(f.get("forks_ratio", 0) > 0.85 and f.get("original_repos", 0) < 3, 15, "Mostly forks, very few original repos")
    penalize(f.get("commit_burst_index", 0) > 0.9, 10, "Highly bursty commit pattern (many commits in one day)")
    penalize(f.get("msg_uniqueness", 1) < 0.4, 10, "Low variety in commit messages")
    penalize(f.get("stars_spike_z", 0) > 3, 10, "Unnatural star spike vs repo age")
    penalize(f.get("heatmap_entropy", 1) < 0.2, 10, "Contribution timing entropy is too low")
    penalize(f.get("collab_ratio", 1) < 0.05, 10, "Very low collaboration activity (issues/PR/reviews)")
    penalize(f.get("lang_diversity", 1) < 0.2, 10, "Very low language diversity")

    score = max(0, min(100, int(round(score))))
    return score, reasons

def explain_score(reasons): 
    return reasons
