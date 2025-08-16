import json
import argparse
from gpas.api import get_client
from gpas.extract import fetch_profile_bundle
from gpas.features import compute_features
from gpas.score import compute_score, explain_score

def main():
    p = argparse.ArgumentParser(description="GitHub Profile Authenticity Scorer")
    p.add_argument("username", help="GitHub username to analyze")
    p.add_argument("--json", action="store_true", help="Output JSON")
    args = p.parse_args()

    gh = get_client()
    bundle = fetch_profile_bundle(gh, args.username)
    feats = compute_features(bundle)
    score, parts = compute_score(feats)
    expl = explain_score(parts)

    output = {
        "user": args.username,
        "score": score,
        "features": feats,
        "explanations": expl,
    }

    if args.json:
        print(json.dumps(output, indent=2, default=str))
    else:
        print(f"User: {args.username}")
        print(f"Authenticity score: {score}/100")
        print("\nSignals:")
        for k, v in feats.items():
            print(f"  - {k}: {v}")
        print("\nWhy:")
        for e in expl:
            print(f"  {e}")
