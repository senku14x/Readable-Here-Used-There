"""Score the constrained-attack audit (design_spec.md Amendment 2). Cluster = unordered pair (n = 16). Writes attack_results.md."""
import os, json
import numpy as np
from scipy import stats as st
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "outputs")
K = json.load(open(os.path.join(OUT, "bank_constants.json")))
mb = json.load(open(os.path.join(OUT, "meta_bank.json"))); rb = np.load(os.path.join(OUT, "raw_bank.npz"))
ma = json.load(open(os.path.join(OUT, "meta_audit.json"))); ra = np.load(os.path.join(OUT, "raw_audit.npz"))
ms = json.load(open(os.path.join(OUT, "meta_search.json"))); rs = np.load(os.path.join(OUT, "raw_search.npz"))
INST = [("J_NP", "m_J_NP"), ("R_CB", "m_R_CB"), ("RESID_fit", "m_RESID_fit"), ("RESID_audit", "m_RESID_audit"), ("LOGITS", "m_LOGITS")]
A = {"J_NP": K["A_J_NP"], "R_CB": K["A_R_CB"], "RESID_fit": K["A_RESID_fit"], "RESID_audit": K["A_RESID_audit"], "LOGITS": K["A_LOGITS"]}


def ct(v):
    v = np.asarray(v, float); n = len(v); mu = v.mean(); h = st.t.ppf(0.975, n - 1) * v.std(ddof=1) / np.sqrt(n) if n > 1 else float("nan")
    return f"{mu:+.3f} [{mu - h:+.3f}, {mu + h:+.3f}] ({int((v > 0).sum())}/{n})"


def bypair(cells, f):
    by = {}
    for b in cells: by.setdefault(tuple(sorted((ma["cells"][b]["X"], ma["cells"][b]["Y"]))), []).append(f(b))
    return np.array([np.mean(v) for v in by.values()])


aud = [b for b, c in ma["cells"].items() if c["audit"]]; fit = [b for b, c in ma["cells"].items() if not c["audit"]]
rad = 1.0
lines = [f"# trying_to_fool — constrained forge search, audit (search run {ms['run_id']}, audit run {ma['run_id']})", "",
         f"16 bank pairs, one direction each; δ fitted on C0/C1 (seed-A codes) for {ms['steps']} Adam steps at radius 1.0·ρ_nat = {K['rho_nat']:.2f}; audited on C2/C3 (seed-B codes). Cluster = unordered pair (n = 16). Shares are Δ/A_k with A_k the natural Y−X swing of each instrument at L51–59 (bank stage). Targets: T_J = {K['T_J']:.2f} (½A_J), T_Y = {K['T_Y']:.2f}; bands ε_k = 0.2·A_k; ε_b = {K['eps_b']:.2f} nats.", ""]
for label, cells in (("Held-out carriers C2/C3, fresh codes (the audit)", aud), ("Fitting carriers C0/C1 (in-sample reference)", fit)):
    lines.append(f"## {label}\n"); lines.append("| instrument | attack δ: share of A_k | naming steer at the same norm: share of A_k |"); lines.append("|---|---|---|")
    for inst, key in INST:
        att = bypair(cells, lambda b: (ra[f"{b}|attack{rad}|{key}"] - ra[f"{b}|cleanX|{key}"]) / A[inst])
        stm = bypair(cells, lambda b: (ra[f"{b}|steerm{rad}|{key}"] - ra[f"{b}|cleanX|{key}"]) / A[inst])
        lines.append(f"| {inst} | {ct(att)} | {ct(stm)} |")
    sy = bypair(cells, lambda b: (ra[f"{b}|attack{rad}|sY_J_NP"] - ra[f"{b}|cleanX|sY_J_NP"]) / K["A_J_Y"]); sy2 = bypair(cells, lambda b: (ra[f"{b}|steerm{rad}|sY_J_NP"] - ra[f"{b}|cleanX|sY_J_NP"]) / K["A_J_Y"])
    lines.append(f"| Y presence (J_NP), share of A_J^Y | {ct(sy)} | {ct(sy2)} |")
    bb = bypair(cells, lambda b: (ra[f"{b}|attack{rad}|b"] - ra[f"{b}|cleanX|b"]) / K["A_b"]); bb2 = bypair(cells, lambda b: (ra[f"{b}|steerm{rad}|b"] - ra[f"{b}|cleanX|b"]) / K["A_b"])
    lines.append(f"| behaviour b, share of A_b | {ct(bb)} | {ct(bb2)} |")
    sel = bypair(cells, lambda b: ((ra[f"{b}|attack{rad}|m_J_NP"] - ra[f"{b}|cleanX|m_J_NP"]) / A["J_NP"]) / max(abs((ra[f"{b}|attack{rad}|m_RESID_audit"] - ra[f"{b}|cleanX|m_RESID_audit"]) / A["RESID_audit"]), 1e-6))
    sel2 = bypair(cells, lambda b: ((ra[f"{b}|steerm{rad}|m_J_NP"] - ra[f"{b}|cleanX|m_J_NP"]) / A["J_NP"]) / max(abs((ra[f"{b}|steerm{rad}|m_RESID_audit"] - ra[f"{b}|cleanX|m_RESID_audit"]) / A["RESID_audit"]), 1e-6))
    lines.append(f"\nSelectivity ratio (J share) / |audit-axis share|, per pair then averaged: attack {ct(sel)}; steer {ct(sel2)}; median attack {np.median(sel):.2f}, steer {np.median(sel2):.2f}.")
    rk = [int(ra[f"{b}|attack{rad}|rankY"]) for b in cells]; rk0 = [int(ra[f"{b}|cleanX|rankY"]) for b in cells]; rk2 = [int(ra[f"{b}|steerm{rad}|rankY"]) for b in cells]
    lines.append(f"Y's best full-vocabulary rank in L51–59 (median over cells): clean {int(np.median(rk0))}, attack {int(np.median(rk))}, steer {int(np.median(rk2))}.")
    dn = [float(ra[f"{b}|attack{rad}|nll"] - ra[f"{b}|cleanX|nll"]) for b in cells]; ret = [float(ra[f"{b}|attack{rad}|ret"]) for b in cells]
    lines.append(f"Damage: ΔNLL mean {np.mean(dn):+.4f}, max {max(dn):+.4f}; top-1 retention min {min(ret):.3f}. Realized write ρ {np.mean([float(ra[f'{b}|attack{rad}|w_rho']) for b in cells]):.3f}, κ {np.mean([float(ra[f'{b}|attack{rad}|w_kappa']) for b in cells]):.4f}. cos(δ, naming direction) mean {np.mean([ma['cells'][b]['cos_delta_steer'] for b in cells]):+.3f}.")
    # outcome labels per pair (audit carriers averaged within pair)
    if cells is aud:
        labels = {}
        by = {}
        for b in cells: by.setdefault(tuple(sorted((ma["cells"][b]["X"], ma["cells"][b]["Y"]))), []).append(b)
        for pr, bs in by.items():
            dJ = np.mean([ra[f"{b}|attack{rad}|m_J_NP"] - ra[f"{b}|cleanX|m_J_NP"] for b in bs]); dY = np.mean([ra[f"{b}|attack{rad}|sY_J_NP"] - ra[f"{b}|cleanX|sY_J_NP"] for b in bs])
            dA = np.mean([ra[f"{b}|attack{rad}|m_RESID_audit"] - ra[f"{b}|cleanX|m_RESID_audit"] for b in bs]); dR = np.mean([ra[f"{b}|attack{rad}|m_R_CB"] - ra[f"{b}|cleanX|m_R_CB"] for b in bs])
            db = np.mean([ra[f"{b}|attack{rad}|b"] - ra[f"{b}|cleanX|b"] for b in bs]); dnl = max(float(ra[f"{b}|attack{rad}|nll"] - ra[f"{b}|cleanX|nll"]) for b in bs); rt = min(float(ra[f"{b}|attack{rad}|ret"]) for b in bs)
            reached = dJ >= K["T_J"] and dY >= K["T_Y"]; audit_in = abs(dA) <= K["eps"]["RESID_audit"] and abs(dR) <= K["eps"]["R_CB"]; b_in = abs(db) <= K["eps_b"]; dmg_ok = dnl <= 0.02 and rt >= 0.95
            lab = "(iv) not reached / damage" if not (reached and dmg_ok) else ("(i) forge with audit inside bands" if (audit_in and b_in) else ("(iii) readouts and behaviour move" if not b_in else "(ii) J and audit instruments move together"))
            labels[pr] = (lab, dJ / A["J_NP"], dY / K["A_J_Y"], dA / A["RESID_audit"], dR / A["R_CB"], db / K["A_b"], dnl)
        lines.append("\n### Outcome per pair (audit carriers)\n"); lines.append("| pair | label | ΔJ/A_J | ΔY/A_J^Y | Δaudit/A | ΔR_CB/A | Δb/A_b | ΔNLL max |"); lines.append("|---|---|---|---|---|---|---|---|")
        for pr, (lab, *v) in labels.items(): lines.append(f"| {pr[0]}–{pr[1]} | {lab} | {v[0]:+.2f} | {v[1]:+.2f} | {v[2]:+.2f} | {v[3]:+.2f} | {v[4]:+.2f} | {v[5]:+.4f} |")
        from collections import Counter; cnt = Counter(l for l, *_ in labels.values()); lines.append("\nCounts: " + ", ".join(f"{k}: {v}" for k, v in sorted(cnt.items())))
    lines.append("")
# search curves summary
lines.append("## Search curves (fitting carriers; final step)\n"); lines.append("| pair | obj | ΔJ/A_J | ΔY/A_J^Y | Δfit-axis/A | Δb/A_b | ΔNLL |"); lines.append("|---|---|---|---|---|---|---|")
for key, c in ms["cells"].items():
    f = c["final"]; lines.append(f"| {key} | {f['obj']:+.2f} | {f['mJ']/A['J_NP']:+.2f} | {f['sY']/K['A_J_Y']:+.2f} | {f['mP']/A['RESID_fit']:+.2f} | {f['b']/K['A_b']:+.2f} | {f['dnll']:+.4f} |")
open(os.path.join(HERE, "attack_results.md"), "w").write("\n".join(lines) + "\n"); print("\n".join(lines))
