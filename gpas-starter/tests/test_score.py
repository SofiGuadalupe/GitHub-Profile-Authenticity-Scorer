from gpas.score import compute_score

def test_score_bounds():
    s, _ = compute_score({
        "forks_ratio": 0.0,
        "original_repos": 10,
        "commit_burst_index": 0.1,
        "msg_uniqueness": 0.9,
        "stars_spike_z": 0.0,
        "heatmap_entropy": 0.8,
        "collab_ratio": 0.4,
        "lang_diversity": 0.5,
    })
    assert 0 <= s <= 100
