import sys
import pandas as pd
from pathlib import Path

CUSTOM_DIR = Path("data/raw/custom")


def check_keystroke(session_id):
    path = CUSTOM_DIR / f"keystroke_{session_id}.csv"
    df = pd.read_csv(path)
    print(f"\n=== Keystroke: {path.name} ===")
    print("Events:", len(df))

    issues = []

    # 1. Missing values
    if df.isna().any().any():
        issues.append("missing values present")

    # 2. Time monotonic
    if not df["timestamp"].is_monotonic_increasing:
        issues.append("timestamps not sorted")

    # 3. down/up pairing per key_id
    downs = (df["event"] == "down").sum()
    ups = (df["event"] == "up").sum()
    print(f"down: {downs} | up: {ups}")
    if downs != ups:
        issues.append(f"down/up mismatch ({downs} vs {ups})")

    # 4. Dwell times: pair each down with the next up of the same key_id
    dwell = []
    pending = {}
    for _, r in df.iterrows():
        k = r["key_id"]
        if r["event"] == "down":
            pending[k] = r["timestamp"]
        elif r["event"] == "up" and k in pending:
            dwell.append(r["timestamp"] - pending.pop(k))
    dwell = pd.Series(dwell)
    print(f"Dwell times computed: {len(dwell)}")
    print(f"Dwell mean: {dwell.mean():.4f}s | min: {dwell.min():.4f}s | max: {dwell.max():.4f}s")
    if (dwell <= 0).any():
        issues.append("non-positive dwell times")
    if dwell.max() > 5:
        issues.append("dwell time > 5s (held key?)")

    print("Categories:", df["key_category"].value_counts().to_dict())
    print("Issues:", issues or "none")
    return issues


def check_mouse(session_id):
    path = CUSTOM_DIR / f"mouse_{session_id}.csv"
    df = pd.read_csv(path)
    print(f"\n=== Mouse: {path.name} ===")
    print("Events:", len(df))
    print("Event types:", df["event"].value_counts().to_dict())

    issues = []

    # 1. Missing values in core columns
    if df[["timestamp", "x", "y"]].isna().any().any():
        issues.append("missing values in timestamp/x/y")

    # 2. Time monotonic
    if not df["timestamp"].is_monotonic_increasing:
        issues.append("timestamps not sorted")

    # 3. Move thinning: gaps between consecutive moves
    moves = df[df["event"] == "move"]
    gaps = moves["timestamp"].diff().dropna()
    tiny = (gaps < 0.009).sum()  # allow small tolerance below 10 ms
    print(f"Moves: {len(moves)} | min gap: {gaps.min():.4f}s | median gap: {gaps.median():.4f}s")
    if tiny > 0:
        issues.append(f"{tiny} move gaps < 9 ms (thinning issue)")

    # 4. Coordinate sanity
    print(f"x range: {df['x'].min()}..{df['x'].max()} | "
          f"y range: {df['y'].min()}..{df['y'].max()}")
    if (df["x"] < 0).any() or (df["y"] < 0).any():
        issues.append("negative coordinates")
    if (df["x"] > 20000).any() or (df["y"] > 20000).any():
        issues.append("coordinates too large")

    print("Issues:", issues or "none")
    return issues


if __name__ == "__main__":
    session_id = sys.argv[1] if len(sys.argv) > 1 else "pilon01"
    k_issues = check_keystroke(session_id)
    m_issues = check_mouse(session_id)

    print("\n=== Summary ===")
    total = len(k_issues) + len(m_issues)
    if total == 0:
        print("All checks passed. Data looks clean.")
    else:
        print(f"{total} issue(s) found. See above.")