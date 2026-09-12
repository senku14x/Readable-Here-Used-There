"""Derive the frozen constants and evaluate gates G1-G5 from the calibration archive. Cluster = unordered pair."""
import os, json
import numpy as np
from scipy import stats as st
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "outputs")
m = json.load(open(os.path.join(OUT, "meta_calibrate.json"))); r = np.load(os.path.join(OUT, "raw_calibrate.npz"))
words = m["words"]; W = {"L48-50": (48, 50), "L51-59": (51, 59)}
cells = [c for c in m["cells"] if "excluded" not in m["cells"][c]]
pair_of = lambda c: tuple(sorted(c.split("|")[0].split("->")))


def ct(v):
    v = np.asarray(v, float); n = len(v); mu = v.mean(); h = st.t.ppf(0.975, n - 1) * v.std(ddof=1) / np.sqrt(n) if n > 1 else float("nan")
    return {"mean": float(mu), "ci": [float(mu - h), float(mu + h)], "n": int(n), "pos": int((v > 0).sum())}


def fmt(c): return f"{c['mean']:+.3f} [{c['ci'][0]:+.3f}, {c['ci'][1]:+.3f}] ({c['pos']}/{c['n']})"
def bypair(f): 
    by = {}
    for c in cells: by.setdefault(pair_of(c), []).append(f(c))
    return [float(np.mean(v)) for v in by.values()]


def margin(c, cond, inst, win):
    X, Y = m["cells"][c]["X"], m["cells"][c]["Y"]; lo, hi = W[win]
    if inst in ("J_NP", "R_CB"):
        z = r[f"{c}|{cond}|z|{inst}"][lo:hi + 1].astype(np.float32).mean(axis=(0, 1)); return float(z[words.index(Y)] - z[words.index(X)])
    if inst in ("RESID_fit", "RESID_audit"):
        col = 2 if inst == "RESID_fit" else 5; return float(r[f"{c}|{cond}|resid"][lo:hi + 1, col].mean())
    if inst == "LOGITS":
        lp = r[f"{c}|{cond}|lp"]; return float(lp[1] - lp[0])


def presY(c, cond, win):
    Y = m["cells"][c]["Y"]; lo, hi = W[win]; z = r[f"{c}|{cond}|z|J_NP"][lo:hi + 1].astype(np.float32).mean(axis=(0, 1))
    return float(z[words.index(Y)] - z[[words.index(d) for d in m["decoys"]]].mean())


INST = ["J_NP", "RESID_fit", "RESID_audit", "R_CB", "LOGITS"]
lines = [f"# trying_to_fool — calibration (run {m['run_id']}, {m['n_forwards']} forwards)", "",
         f"Cells {len(cells)} (excluded by geometry: {[c for c in m['cells'] if 'excluded' in m['cells'][c]]}); cluster = unordered pair (n = {len(set(pair_of(c) for c in cells))}).", ""]
K = {}
for win in W:
    lines.append(f"## Natural swings A_k at {win} (maintain-Y minus maintain-X, margin Y−X) and intervention shares\n")
    lines.append("| instrument | A_k (natural) | C1b source donor ≥36, share of A | C1c block-35 carrier transplant, share of A |"); lines.append("|---|---|---|---|")
    for inst in INST:
        A = ct(bypair(lambda c: margin(c, "cleanY", inst, win) - margin(c, "cleanX", inst, win)))
        s1 = ct(bypair(lambda c: (margin(c, "C1b", inst, win) - margin(c, "cleanX", inst, win)) / max(abs(A["mean"]), 1e-9)))
        s2 = ct(bypair(lambda c: (margin(c, "C1c", inst, win) - margin(c, "cleanX", inst, win)) / max(abs(A["mean"]), 1e-9)))
        K[f"{win}|A|{inst}"] = A; K[f"{win}|C1b|{inst}"] = s1; K[f"{win}|C1c|{inst}"] = s2
        lines.append(f"| {inst} | {fmt(A)} | {fmt(s1)} | {fmt(s2)} |")
    AY = ct(bypair(lambda c: presY(c, "cleanY", win) - presY(c, "cleanX", win))); K[f"{win}|A_J^Y"] = AY
    lines.append(f"\nA_J^Y (Y presence swing, J_NP): {fmt(AY)}\n")
Ab = ct(bypair(lambda c: float(r[f"{c}|cleanY|b"] - r[f"{c}|cleanX|b"]))); K["A_b"] = Ab
rho = ct(bypair(lambda c: float(r[f"{c}|rho_nat"]))); K["rho_nat"] = rho
lines.append(f"**A_b (behavioural swing from the prompt change):** {fmt(Ab)} nats. **ρ_nat (per-position ‖Δh35‖):** {fmt(rho)}.\n")
lines.append("C1b/C1c behaviour shift, share of A_b: " + ", ".join(f"{k} {fmt(ct(bypair(lambda c: float(r[f'{c}|{k}|b'] - r[f'{c}|cleanX|b']) / max(abs(Ab['mean']),1e-9))))}" for k in ("C1b", "C1c")) + "\n")
# repeat floors
rep = [c for c in cells if f"{c}|repeat|z|J_NP" in r]
lines.append("## Repeat floors (per instrument): bitwise repeat, and a one-token-longer question\n")
lines.append("| instrument | max |Δ| bitwise repeat | max |Δ| length change |"); lines.append("|---|---|---|")
for inst in INST:
    dr = max(abs(margin(c, "repeat", inst, "L48-50") - margin(c, "cleanX", inst, "L48-50")) for c in rep)
    dl = max(abs(margin(c, "lenvar", inst, "L48-50") - margin(c, "cleanX", inst, "L48-50")) for c in rep)
    K[f"floor|{inst}"] = {"repeat": dr, "length": dl}; lines.append(f"| {inst} | {dr:.2e} | {dl:.3f} |")
lines.append(f"| behaviour b | {max(abs(float(r[f'{c}|repeat|b'] - r[f'{c}|cleanX|b'])) for c in rep):.2e} | {max(abs(float(r[f'{c}|lenvar|b'] - r[f'{c}|cleanX|b'])) for c in rep):.3f} |")
lines.append(f"\nBitwise repeat identical: {all(bool(r[f'{c}|repeat_bitwise']) for c in rep)}.\n")
# random writes and steer
lines.append("## Random writes (noise floor and damage) and the naming-direction steer (unconstrained reachability), J_NP at L48-50\n")
lines.append("| radius (×ρ_nat) | random: ΔJ margin | random: ΔNLL mean / max | random: top-1 ret min | steer: ΔJ margin (share of A) | steer: ΔY presence (share of A_J^Y) | steer: ΔRESID_audit (share) | steer: Δb (share of A_b) | steer: ΔNLL max | steer realized κ min |"); lines.append("|---|---|---|---|---|---|---|---|---|---|")
AJ = K["L48-50|A|J_NP"]["mean"]; AYv = K["L48-50|A_J^Y"]["mean"]; AR = K["L48-50|A|RESID_audit"]["mean"]
for rad in (0.5, 1.0, 2.0):
    rk = [(c, k) for c in cells for k in (f"rand{rad}|s0", f"rand{rad}|s1", f"rand{rad}|s2") if f"{c}|{k}|b" in r]
    dJ = [margin(c, k, "J_NP", "L48-50") - margin(c, "cleanX", "J_NP", "L48-50") for c, k in rk]
    dn = [float(r[f"{c}|{k}|nll"] - r[f"{c}|cleanX|nll"]) for c, k in rk]; ret = [float(r[f"{c}|{k}|ret"]) for c, k in rk]
    sJ = ct(bypair(lambda c: (margin(c, f"steer{rad}", "J_NP", "L48-50") - margin(c, "cleanX", "J_NP", "L48-50")) / AJ))
    sY = ct(bypair(lambda c: (presY(c, f"steer{rad}", "L48-50") - presY(c, "cleanX", "L48-50")) / AYv))
    sR = ct(bypair(lambda c: (margin(c, f"steer{rad}", "RESID_audit", "L48-50") - margin(c, "cleanX", "RESID_audit", "L48-50")) / AR))
    sb = ct(bypair(lambda c: float(r[f"{c}|steer{rad}|b"] - r[f"{c}|cleanX|b"]) / max(abs(Ab["mean"]), 1e-9)))
    sn = max(float(r[f"{c}|steer{rad}|nll"] - r[f"{c}|cleanX|nll"]) for c in cells); kap = min(float(r[f"{c}|steer{rad}|w_kappa"]) for c in cells)
    K[f"rand{rad}"] = {"dJ_mean": float(np.mean(dJ)), "dJ_max": float(np.max(np.abs(dJ))), "dNLL_mean": float(np.mean(dn)), "dNLL_max": float(np.max(dn)), "ret_min": float(np.min(ret))}
    K[f"steer{rad}"] = {"J_share": sJ, "Y_share": sY, "RESID_audit_share": sR, "b_share": sb, "dNLL_max": sn, "kappa_min": kap}
    lines.append(f"| {rad} | {np.mean(dJ):+.3f} (max |{np.max(np.abs(dJ)):.3f}|) | {np.mean(dn):+.4f} / {np.max(dn):+.4f} | {np.min(ret):.3f} | {fmt(sJ)} | {fmt(sY)} | {fmt(sR)} | {fmt(sb)} | {sn:+.4f} | {kap:.4f} |")
# gates + frozen constants
TJ = 0.5 * AJ; TY = 0.5 * AYv
G = {"G1_audit_axis_sees_identity": K["L48-50|A|RESID_audit"]["ci"][0] > 0 and K["L48-50|A|R_CB"]["mean"] > 0,
     "G2_J_target_defined": K["L48-50|A|J_NP"]["ci"][0] > 0,
     "G3_block35_transplant_reaches_J_and_audit": K["L48-50|C1c|J_NP"]["mean"] > 0.25 and K["L48-50|C1c|RESID_audit"]["mean"] > 0.25,
     "G4_random_J_below_target": K["rand1.0"]["dJ_max"] < TJ,
     "G5_bands_exceed_floors": all(0.2 * abs(K[f"L48-50|A|{i}"]["mean"]) > K[f"floor|{i}"]["repeat"] for i in INST)}
FROZEN = {"T_J": TJ, "T_Y": TY, "eps": {i: 0.2 * abs(K[f"L48-50|A|{i}"]["mean"]) for i in INST}, "eps_b": 0.2 * abs(Ab["mean"]),
          "rho_nat": rho["mean"], "radii": [0.5 * rho["mean"], rho["mean"], 2 * rho["mean"]],
          "D_max": max(K["rand2.0"]["dNLL_mean"], 0.0, K["floor|J_NP"]["repeat"]), "top1_min": 0.95, "window": "L48-50", "gates": G,
          "steer_reaches_T_J_at": [rad for rad in (0.5, 1.0, 2.0) if K[f"steer{rad}"]["J_share"]["mean"] >= 0.5]}
lines += ["## Gates", ""] + [f"- {k}: **{'PASS' if v else 'FAIL'}**" for k, v in G.items()] + ["", "## Frozen constants", "", "```json", json.dumps(FROZEN, indent=1), "```", "",
          "## Reading", "", "(written by hand)"]
json.dump({"K": K, "frozen": FROZEN}, open(os.path.join(HERE, "frozen_constants.json"), "w"), indent=1, default=float)
open(os.path.join(HERE, "calibration.md"), "w").write("\n".join(lines)); print("\n".join(lines))
