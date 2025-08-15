import json
import glob
import os
from collections import Counter


def safe_len_recent_tweets(user_obj: dict) -> int:
    recent = user_obj.get("recent_tweets", [])
    if isinstance(recent, list):
        return len(recent)
    return 0


def analyze_file(path: str) -> None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        print(f"FILE: {path}\n  error loading json: {exc}")
        return

    if not isinstance(data, list):
        return

    distribution: Counter[int] = Counter()
    anomalies = []

    for user in data:
        if not isinstance(user, dict):
            continue
        cnt = safe_len_recent_tweets(user)
        distribution[cnt] += 1
        if cnt != 50:
            anomalies.append((user.get("username") or user.get("url"), cnt))

    total_users = sum(distribution.values())
    eq50 = distribution.get(50, 0)

    print(f"FILE: {path}")
    print(f"  users: {total_users}, ==50: {eq50}, !=50: {total_users - eq50}")
    print("  count distribution:")
    for k in sorted(distribution):
        print(f"    {k}: {distribution[k]}")
    if anomalies:
        print("  first not-50 examples:")
        for name, c in anomalies[:20]:
            print(f"    {name}: {c}")


def main() -> None:
    paths = sorted(glob.glob(os.path.join("results", "*.json")))
    if not paths:
        print("No JSON files found under results/.")
        return
    for p in paths:
        analyze_file(p)


if __name__ == "__main__":
    main()


