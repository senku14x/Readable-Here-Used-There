"""Non-destructive audit of committed H3 selection_to_behavior outputs.

Writes only under H3/audits/selection_to_behavior/outputs/.
Does NOT modify H3/outputs or H3/results.

Usage from repo root:
    python H3/audits/selection_to_behavior/recompute_saved.py pilot
    python H3/audits/selection_to_behavior/recompute_saved.py evaluate

Checks:
- expected/missing/duplicate condition keys;
- correct cluster unit (average rotations/carriers inside triple first);
- direct E_B/E_C, random controls, ceilings and specificity;
- BtoA/CtoA crossed specificity matrix (diagonal and off-diagonal pulls);
- answer-class counts from saved greedy strings;
- documents that raw answer logits were not saved, so max-vs-logsumexp rescoring
  cannot be reconstructed from the existing NPZ alone.
"""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "common", "scripts"))
import stats as S

stage = sys.argv[1] if len(sys.argv) > 1 else "pilot"
assert stage in ("pilot", "evaluate")
SRC = os.path.join(ROOT, "H3", "outputs", "selection_to_behavior")
OUT = os.path.join(HERE, "outputs")
os.makedirs(OUT, exist_ok=True)
meta = json.load(open(os.path.join(SRC, f"meta_{stage}.json")))
z = np.load(os.path.join(SRC, f"raw_{stage}.npz"), allow_pickle=False)
cells = list(meta["cells"])
letters = meta["letters"]


def lsc(tag):
    v = z[f"{tag}|lsc"].astype(np.float64)
    return {L: float(v[i]) for i, L in enumerate(letters)}


def q(tag, target_word, a_word, asg):
    s = lsc(tag)
    return s[asg[target_word]] - s[asg[a_word]]


def triple_id(cell):
    return int(cell.split("|")[0][1:])


def aggregate_by_triple(values):
    by = {}
    for c, v in values.items():
        by.setdefault(triple_id(c), []).append(float(v))
    return {str(t): float(np.mean(v)) for t, v in sorted(by.items())}


def cluster(values):
    by = aggregate_by_triple(values)
    return {"per_triple": by, "cluster_t": S.cluster_t(list(by.values()))}

# Completeness: every pilot cell must have all primary rows. Evaluate also needs swaps.
primary_arms = ["cleanA", "cleanB", "cleanC", "BtoA", "CtoA", "randA"]
missing = []
for c in cells:
    for a in primary_arms:
        for suffix in ("lsc", "greedy", "z", "nll", "top1"):
            k = f"{c}|{a}|noswap|{suffix}"
            if k not in z.files:
                missing.append(k)
    if stage == "evaluate":
        for a in primary_arms:
            for j in range(3):
                for suffix in ("lsc", "greedy", "z", "nll", "top1"):
                    k = f"{c}|{a}|swap{j}|{suffix}"
                    if k not in z.files:
                        missing.append(k)

# Current endpoint and crossed specificity matrix.
E = {"BtoA": {"B": {}, "C": {}}, "CtoA": {"B": {}, "C": {}}, "randA": {"B": {}, "C": {}}}
ceil = {"B": {}, "C": {}}
for c in cells:
    cm = meta["cells"][c]; wA, wB, wC = cm["words"]; asg = cm["assign"]
    cleanA_B = q(f"{c}|cleanA|noswap", wB, wA, asg)
    cleanA_C = q(f"{c}|cleanA|noswap", wC, wA, asg)
    for arm in E:
        E[arm]["B"][c] = q(f"{c}|{arm}|noswap", wB, wA, asg) - cleanA_B
        E[arm]["C"][c] = q(f"{c}|{arm}|noswap", wC, wA, asg) - cleanA_C
    ceil["B"][c] = q(f"{c}|cleanB|noswap", wB, wA, asg) - cleanA_B
    ceil["C"][c] = q(f"{c}|cleanC|noswap", wC, wA, asg) - cleanA_C

summary = {
    "stage": stage,
    "raw_sha_from_manifest": json.load(open(os.path.join(SRC, f"manifest_{stage}.json")))["raw_sha256"],
    "n_cells": len(cells),
    "n_triples": len(set(triple_id(c) for c in cells)),
    "missing_expected_keys": missing,
    "note_scoring": "raw_pilot/evaluate.npz stores only eight max-over-surface-form letter scores, not the candidate raw logits. Correct deduplicated logsumexp rescoring cannot be reconstructed from this artifact.",
    "crossed_specificity": {},
    "ceilings": {k: cluster(v) for k, v in ceil.items()},
}
for arm in E:
    summary["crossed_specificity"][arm] = {target: cluster(vals) for target, vals in E[arm].items()}

# Intended diagonal and current-random specificity, correctly clustered.
summary["primary"] = {
    "E_B": summary["crossed_specificity"]["BtoA"]["B"],
    "E_C": summary["crossed_specificity"]["CtoA"]["C"],
    "rand_on_B_margin": summary["crossed_specificity"]["randA"]["B"],
    "rand_on_C_margin": summary["crossed_specificity"]["randA"]["C"],
}
for D, arm, target in (("B", "BtoA", "B"), ("C", "CtoA", "C")):
    diff = {c: E[arm][target][c] - E["randA"][target][c] for c in cells}
    summary["primary"][f"E_{D}_minus_current_rand"] = cluster(diff)

# Ratio of means after aggregation to the actual inferential unit.
for D, arm, target in (("B", "BtoA", "B"), ("C", "CtoA", "C")):
    num = list(aggregate_by_triple(E[arm][target]).values())
    den = list(aggregate_by_triple(ceil[target]).values())
    summary["primary"][f"restore_{D}_ratio"] = S.ratio_of_means(num, den)

# Descriptive classification. This intentionally does not pretend cell counts are independent clusters.
classes = {a: {"A": 0, "target": 0, "other_assigned": 0, "unassigned_or_nonletter": 0} for a in primary_arms}
for c in cells:
    cm = meta["cells"][c]; wA, wB, wC = cm["words"]; asg = cm["assign"]
    l2w = {L: w for w, L in asg.items()}
    for arm, tgt in (("cleanA", wA), ("cleanB", wB), ("cleanC", wC), ("BtoA", wB), ("CtoA", wC), ("randA", wB)):
        g = str(z[f"{c}|{arm}|noswap|greedy"])
        ow = l2w.get(g)
        if ow is None:
            classes[arm]["unassigned_or_nonletter"] += 1
        elif ow == wA:
            classes[arm]["A"] += 1
        elif ow == tgt:
            classes[arm]["target"] += 1
        else:
            classes[arm]["other_assigned"] += 1
summary["answer_class_noswap"] = classes

path = os.path.join(OUT, f"recompute_saved_{stage}.json")
json.dump(summary, open(path, "w"), indent=1)
print(json.dumps(summary, indent=1))
print(f"\nWrote {path}")
