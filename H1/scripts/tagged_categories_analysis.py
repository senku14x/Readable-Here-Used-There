"""Analysis for H1 tagged_categories (single scoring pass). Reads H1/outputs/tagged_categories/raw_<stage>.npz.

Does the tagged instruction select category-*associated content* (unshown members) or only the literal label token?

Stage `gate`  : member-instrument positive control. maintain / mention / absent on 8 eligible categories.
                Endpoint = member aggregate s_bar(c) = mean over the 4 unshown members of (z_w - mean z_decoys), and label
                presence. Contrasts maintain-absent (the gate), maintain-mention, mention-absent; cluster = category (n=8);
                both windows; sign counts; per-member distribution and max-member; PASS/FAIL per §4 of the design spec.
Stage `select`: tagged triples, arms A/B/C point at slots 0/1/2, ctrl points at none; source slot j replaced from block 36 by
                the partner-triple category. Transfer C_j = m_j(swap j) - m_j(clean); m_j = s_bar(donor_j) - s_bar(source_j)
                on members (primary), on the label, on RESID_P (category pair axis, p_pair), and on LOGITS. Relevance indexed
                by category identity. S = pointed - unpointed; Q = unpointed - control; U = pointed - control. TWO clusterings:
                triple (n=8, the design unit) and category (n=6, identity level). P0(pure, ti 0-1) vs mixed(ti 2-7) confusion.
                Readout-only rows (mammals, vegetables): S_nat on members (natural selectivity, no replacement).

Template: tagged_selection_analysis.py (same S/Q/U machinery). Usage: tagged_categories_analysis.py gate|select
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common", "scripts"))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import registry as R
import stats as S

STAGE = sys.argv[1] if len(sys.argv) > 1 else "select"
assert STAGE in ("gate", "select")
OUT = os.path.join(R.out_dir("H1", "outputs"), "tagged_categories")
RES = os.path.join(R.out_dir("H1", "results")); FIG = os.path.join(RES, "figures"); os.makedirs(FIG, exist_ok=True)
META = json.load(open(os.path.join(OUT, f"meta_{STAGE}.json")))
Z = np.load(os.path.join(OUT, f"raw_{STAGE}.npz"))
CELLS = META["cells"]
COLS = META["columns"]; CIX = {w: i for i, w in enumerate(COLS)}
MEMBERS = META["members"]; ELIGIBLE = META["eligible"]; PRIMARY = META["primary"]; RO = META["readout_only"]
CARRIERS = META["carriers"]; TAGS = ["A", "B", "C"]
TRIPLES = [tuple(t) for t in META["triples"]]; RO_TRIPLES = [tuple(t) for t in META["ro_triples"]]
RANK_LAYERS = META["rank_layers"]                    # 24..59
WINDOWS = {"L48-50": [48, 49, 50], "L51-59": list(range(51, 60))}
DEC = [CIX[w] for w in COLS[40:48]]                  # decoys anchor..bridge (= FIT_WORDS[:8])
MEMCOL = {c: [CIX[w] for w in MEMBERS[c]] for c in ELIGIBLE}
LABCOL = {c: CIX[c] for c in ELIGIBLE}               # category name lives in COLS[32:40]
SUPER = {**{c: "animal" for c in ("birds", "fish", "insects", "mammals")},
         **{c: "artifact" for c in ("tools", "vehicles", "furniture")}, "vegetables": "plant"}
assert len(DEC) == 8 and not (set(DEC) & set(sum(MEMCOL.values(), [])))


# ---- readouts on a z-array [nlayers, npos, 48] (already window-sliced) ----
def sbar(z, c):    # member aggregate presence: mean_members (z_w - mean z_decoys), then over positions & layers
    return float((z[:, :, MEMCOL[c]].mean(-1) - z[:, :, DEC].mean(-1)).mean())


def slab(z, c):    # label presence
    return float((z[:, :, LABCOL[c]] - z[:, :, DEC].mean(-1)).mean())


def zwin(sub, win):
    return Z[f"{sub}|z"].astype(np.float32)[win]


# ---- pair margins m_j = s_bar(Y) - s_bar(X) for a given sub-forward tag ----
def marg(sub, X, Y, j, win, inst, endpoint):
    if inst == "J_NP":
        z = zwin(sub, win)
        return (sbar(z, Y) - sbar(z, X)) if endpoint == "member" else (slab(z, Y) - slab(z, X))
    if inst == "LOGITS":                              # model output log-probs, layer-independent
        lp = Z[f"{sub}|lp"]
        if endpoint == "member":
            return float(lp[:, MEMCOL[Y]].mean(-1).mean() - lp[:, MEMCOL[X]].mean(-1).mean())
        return float(lp[:, LABCOL[Y]].mean() - lp[:, LABCOL[X]].mean())
    if inst == "RESID_P":                             # category pair axis (donor - source), member centroids
        return float(Z[f"{sub}|p_pair{j}"][win].mean())
    raise ValueError(inst)


def C(base, j, win, inst, endpoint):                  # transfer of slot j: m_j(swap j) - m_j(clean)
    cell = CELLS[base]; X = cell["cats"][j]; Y = cell["donor"][str(j)]
    return marg(f"{base}|swap{j}", X, Y, j, win, inst, endpoint) - marg(f"{base}|clean", X, Y, j, win, inst, endpoint)


def presence_clean(base, c, win):                     # natural member-aggregate presence on the clean forward
    return sbar(zwin(f"{base}|clean", win), c)


def cs(e):
    return "n/a" if e is None else f"{e['mean']:+.4f} [{e['ci'][0]:+.4f}, {e['ci'][1]:+.4f}] ({e.get('signs_pos', 0)}/{e['n']} >0)"


# =====================================================================================
if STAGE == "gate":
    ENDPTS = [("J_NP", "member"), ("J_NP", "label"), ("LOGITS", "member"), ("LOGITS", "label")]
    tables = {"eligible": ELIGIBLE, "members": MEMBERS}

    def gpres(sub, c, win, inst, endpoint):
        if inst == "J_NP":
            z = zwin(sub, win); return sbar(z, c) if endpoint == "member" else slab(z, c)
        lp = Z[f"{sub}|lp"]; cols = MEMCOL[c] if endpoint == "member" else [LABCOL[c]]
        return float(lp[:, cols].mean(-1).mean() - lp[:, DEC].mean(-1).mean())

    for inst, endpoint in ENDPTS:
        for wname, win in ([("out", None)] if inst == "LOGITS" else list(WINDOWS.items())):
            w = win if win is not None else [0]      # LOGITS ignores layers; dummy
            key = f"{inst}|{endpoint}" + ("" if inst == "LOGITS" else f"|{wname}")
            if key in tables:
                continue
            rows = {"maintain": [], "mention": [], "absent": [], "maint_abs": [], "maint_ment": [], "ment_abs": []}
            per_member = {c: [] for c in ELIGIBLE}; maxmem = []
            for c in ELIGIBLE:
                vm, vn, va = [], [], []
                pm = []                               # per-member maintain-absent, averaged over carriers
                for ck in CARRIERS:
                    sm = gpres(f"gate|{ck}|{c}|maintain", c, w, inst, endpoint)
                    sn = gpres(f"gate|{ck}|{c}|mention", c, w, inst, endpoint)
                    sa = gpres(f"gate|{ck}|{c}|absent", c, w, inst, endpoint)
                    vm.append(sm); vn.append(sn); va.append(sa)
                    if inst == "J_NP" and endpoint == "member":
                        zmt = zwin(f"gate|{ck}|{c}|maintain", w); zab = zwin(f"gate|{ck}|{c}|absent", w)
                        pm.append([float((zmt[:, :, CIX[mw]] - zmt[:, :, DEC].mean(-1)).mean()
                                         - (zab[:, :, CIX[mw]] - zab[:, :, DEC].mean(-1)).mean()) for mw in MEMBERS[c]])
                rows["maintain"].append(np.mean(vm)); rows["mention"].append(np.mean(vn)); rows["absent"].append(np.mean(va))
                rows["maint_abs"].append(np.mean(vm) - np.mean(va)); rows["maint_ment"].append(np.mean(vm) - np.mean(vn))
                rows["ment_abs"].append(np.mean(vn) - np.mean(va))
                if pm:
                    pmm = np.mean(pm, axis=0); per_member[c] = {mw: float(v) for mw, v in zip(MEMBERS[c], pmm)}
                    maxmem.append(float(pmm.max()))
            T = {k: S.cluster_t(v) for k, v in rows.items()}
            g = T["maint_abs"]; T["PASS"] = bool(g["ci"][0] > 0 and g.get("signs_pos", 0) >= 6)
            if per_member and per_member[ELIGIBLE[0]]:
                T["per_member_maint_abs"] = per_member; T["maxmember_maint_abs"] = S.cluster_t(maxmem)
            tables[key] = T

    # Holm across the two J_NP member windows for the gate contrast
    gp = [S.paired_p(tables[f"J_NP|member|{wn}"]["maint_abs"]["per_cluster"]) for wn in WINDOWS]
    tables["holm_gate_JNP_member"] = {wn: float(a) for wn, (a) in zip(WINDOWS, S.holm(gp))}
    json.dump(tables, open(os.path.join(RES, "tagged_categories_gate_tables.json"), "w"), indent=1, default=float)

    rep = [f"# H1 · tagged_categories — GATE (member-instrument positive control) — run {META['run_id']}\n",
           "## 1. Question and setup\n",
           f"Before reading the selection stage: can the member instrument even *see* a maintained category's unshown members? "
           f"For each eligible category ({', '.join(ELIGIBLE)}) score the 4 unshown members' aggregate s_bar(c)=mean_members(z_w - mean z_decoys) "
           f"and the label, under maintain / mention / absent, carriers {CARRIERS}, interior carrier positions, windows L48-50 and L51-59. "
           f"Decoys = {COLS[40:48]}. Cluster = category (n={len(ELIGIBLE)}). **Gate rule (design §4):** maintain must exceed absent on the "
           f"member aggregate (signs >= 6/8 and 95% CI clear of 0) at >= 1 window, else the member endpoint is 'instrument not validated' and "
           f"the select stage is read on the label endpoint only. maintain vs mention is reported but not gating.\n",
           "## 2. Main findings\n"]
    for key in ("J_NP|member|L48-50", "J_NP|member|L51-59", "J_NP|label|L48-50", "J_NP|label|L51-59", "LOGITS|member", "LOGITS|label"):
        T = tables[key]
        line = (f"- **{key}:** maintain {cs(T['maintain'])}; mention {cs(T['mention'])}; absent {cs(T['absent'])}. "
                f"maintain-absent {cs(T['maint_abs'])}; maintain-mention {cs(T['maint_ment'])}; mention-absent {cs(T['ment_abs'])}.")
        if "PASS" in T and "member" in key:
            line += f" **gate {'PASS' if T['PASS'] else 'FAIL'}**"
            if "maxmember_maint_abs" in T:
                line += f"; max-member(maint-abs) {cs(T['maxmember_maint_abs'])}"
        rep.append(line)
    passes = [wn for wn in WINDOWS if tables[f"J_NP|member|{wn}"]["PASS"]]
    rep.append(f"\n**Gate decision:** member instrument {'VALIDATED' if passes else 'NOT validated'} "
               f"({'passes at ' + ', '.join(passes) if passes else 'fails both windows'}). Holm-adjusted p (J_NP member maint-abs): "
               f"{json.dumps({k: round(v, 4) for k, v in tables['holm_gate_JNP_member'].items()})}.\n")
    rep.append("## 3. Per-member distribution (J_NP member, maintain-absent, mean over carriers)\n")
    for wn in WINDOWS:
        pm = tables[f"J_NP|member|{wn}"].get("per_member_maint_abs", {})
        rep.append(f"### {wn}\n\n| category | " + " | ".join(f"m{i+1}" for i in range(4)) + " | members |\n|---|---|---|---|---|---|")
        for c in ELIGIBLE:
            vals = pm.get(c, {}); order = MEMBERS[c]
            rep.append(f"| {c} | " + " | ".join(f"{vals.get(mw, float('nan')):+.3f} ({mw})" for mw in order)
                       + f" | {np.mean([vals.get(mw, np.nan) for mw in order]):+.3f} |")
        rep.append("")
    rep.append("## 4. Complete tables\n")
    for key in ("J_NP|member|L48-50", "J_NP|member|L51-59", "J_NP|label|L48-50", "J_NP|label|L51-59", "LOGITS|member", "LOGITS|label"):
        T = tables[key]; rep.append(f"### {key}\n\n| quantity | mean | 95% CI | signs>0/n | per-category |\n|---|---|---|---|---|")
        for q in ("maintain", "mention", "absent", "maint_abs", "maint_ment", "ment_abs"):
            e = T[q]; rep.append(f"| {q} | {e['mean']:+.4f} | [{e['ci'][0]:+.4f},{e['ci'][1]:+.4f}] | {e.get('signs_pos',0)}/{e['n']} | "
                                 + ", ".join(f"{x:+.3f}" for x in e["per_cluster"]) + " |")
        rep.append("")
    rep.append("## 5. Interpretation and next decision\n\n_Filled in by hand after reading the tables._\n")
    open(os.path.join(RES, "tagged_categories_gate.md"), "w").write("\n".join(rep))
    print("\n".join(rep[:22]))

# =====================================================================================
else:  # select
    ENDPTS = [("J_NP", "member"), ("J_NP", "label"), ("RESID_P", "member"), ("LOGITS", "member"), ("LOGITS", "label")]
    tables = {"triples": [list(t) for t in TRIPLES], "n_forwards": META["n_forwards"]}
    P0 = [0, 1]                                       # pure partition triples
    MIXED = list(range(2, len(TRIPLES)))

    for inst, endpoint in ENDPTS:
        wins = [("out", None)] if inst == "LOGITS" else list(WINDOWS.items())
        for wname, win in wins:
            w = win if win is not None else None
            key = f"{inst}|{endpoint}" + ("" if inst == "LOGITS" else f"|{wname}")
            # ---- accumulate per triple and per category ----
            tri = {q: [] for q in ("self", "other", "ctrl", "S", "Q", "U")}
            catacc = {c: {"self": [], "other": [], "ctrl": []} for c in PRIMARY}
            S_by_tri = {}                             # for P0/mixed split
            for ti, tr in enumerate(TRIPLES):
                s_, o_, c_ = [], [], []
                for ck in CARRIERS:
                    for rot in range(3):
                        cats = CELLS[f"sel|{ck}|T{ti}|rot{rot}|A"]["cats"]
                        for j in range(3):
                            base_p = f"sel|{ck}|T{ti}|rot{rot}|{TAGS[j]}"
                            sv = C(base_p, j, w, inst, endpoint)
                            ov = np.mean([C(f"sel|{ck}|T{ti}|rot{rot}|{a}", j, w, inst, endpoint) for a in TAGS if a != TAGS[j]])
                            cv = C(f"sel|{ck}|T{ti}|rot{rot}|ctrl", j, w, inst, endpoint)
                            s_.append(sv); o_.append(ov); c_.append(cv)
                            cc = cats[j]
                            if cc in catacc:
                                catacc[cc]["self"].append(sv); catacc[cc]["other"].append(ov); catacc[cc]["ctrl"].append(cv)
                tri["self"].append(np.mean(s_)); tri["other"].append(np.mean(o_)); tri["ctrl"].append(np.mean(c_))
                tri["S"].append(np.mean(s_) - np.mean(o_)); tri["Q"].append(np.mean(o_) - np.mean(c_)); tri["U"].append(np.mean(s_) - np.mean(c_))
                S_by_tri[ti] = tri["S"][-1]
            T = {"cluster_triple": {q: S.cluster_t(v) for q, v in tri.items()}}
            T["cluster_triple"]["S_over_U"] = S.ratio_of_means(tri["S"], tri["U"])
            # category clustering (n=6)
            catrows = {q: [] for q in ("self", "other", "ctrl", "S", "Q", "U")}
            catnames = []
            for c in PRIMARY:
                a = catacc[c]; catnames.append(c)
                catrows["self"].append(np.mean(a["self"])); catrows["other"].append(np.mean(a["other"])); catrows["ctrl"].append(np.mean(a["ctrl"]))
                catrows["S"].append(np.mean(a["self"]) - np.mean(a["other"])); catrows["Q"].append(np.mean(a["other"]) - np.mean(a["ctrl"]))
                catrows["U"].append(np.mean(a["self"]) - np.mean(a["ctrl"]))
            T["cluster_category"] = {q: S.cluster_t(v) for q, v in catrows.items()}
            T["cluster_category"]["names"] = catnames
            T["cluster_category"]["S_over_U"] = S.ratio_of_means(catrows["S"], catrows["U"])
            # P0 (pure, within/cross superclass) vs mixed
            T["S_P0_pure"] = S.cluster_t([S_by_tri[i] for i in P0])
            T["S_mixed"] = S.cluster_t([S_by_tri[i] for i in MIXED])
            tables[key] = T

    # ---- S by layer (J_NP member & label): where does selection emerge? ----
    layer_S = {"member": [], "label": [], "layers": list(range(24, 63))}
    for endpoint in ("member", "label"):
        for L in layer_S["layers"]:
            triS = []
            for ti, tr in enumerate(TRIPLES):
                s_, o_ = [], []
                for ck in CARRIERS:
                    for rot in range(3):
                        for j in range(3):
                            s_.append(C(f"sel|{ck}|T{ti}|rot{rot}|{TAGS[j]}", j, [L], "J_NP", endpoint))
                            o_.append(np.mean([C(f"sel|{ck}|T{ti}|rot{rot}|{a}", j, [L], "J_NP", endpoint) for a in TAGS if a != TAGS[j]]))
                triS.append(np.mean(s_) - np.mean(o_))
            layer_S[endpoint].append(float(np.mean(triS)))
    tables["S_by_layer"] = layer_S

    # ---- readout-only S_nat (mammals, vegetables) on members, natural selectivity (no swap) ----
    ro_tab = {}
    for wname, win in WINDOWS.items():
        percat = {}
        for ti, tr in enumerate(RO_TRIPLES):
            for ck in CARRIERS:
                for rot in range(3):
                    cats = CELLS[f"ro|{ck}|R{ti}|rot{rot}|A"]["cats"]
                    for j in range(3):
                        c = cats[j]
                        pv = presence_clean(f"ro|{ck}|R{ti}|rot{rot}|{TAGS[j]}", c, win)
                        ov = np.mean([presence_clean(f"ro|{ck}|R{ti}|rot{rot}|{a}", c, win) for a in TAGS if a != TAGS[j]])
                        percat.setdefault(c, []).append(pv - ov)
        ro_tab[wname] = {c: S.cluster_t(v) for c, v in percat.items()}
    tables["S_nat_readout_only"] = ro_tab

    # ---- natural presence selectivity on the primary triples (clean, no swap), companion to S ----
    nat = {}
    for wname, win in WINDOWS.items():
        s_, o_, c_ = [], [], []
        for ti, tr in enumerate(TRIPLES):
            ss, oo, cc = [], [], []
            for ck in CARRIERS:
                for rot in range(3):
                    cats = CELLS[f"sel|{ck}|T{ti}|rot{rot}|A"]["cats"]
                    for j in range(3):
                        ss.append(presence_clean(f"sel|{ck}|T{ti}|rot{rot}|{TAGS[j]}", cats[j], win))
                        oo.append(np.mean([presence_clean(f"sel|{ck}|T{ti}|rot{rot}|{a}", cats[j], win) for a in TAGS if a != TAGS[j]]))
                        cc.append(presence_clean(f"sel|{ck}|T{ti}|rot{rot}|ctrl", cats[j], win))
            s_.append(np.mean(ss) - np.mean(oo)); o_.append(np.mean(oo)); c_.append(np.mean(cc))
        nat[wname] = {"S_nat": S.cluster_t(s_)}
    tables["S_nat_primary"] = nat

    # ---- prominence: rank-1-anywhere of pointed category's members (L24-59, clean) ----
    # rank layout [36,19,15]: [:,:,0:3] = labels of cats[0,1,2]; [:,:,3+4j : 3+4j+4] = members of cats[j]
    hits = {"self": [], "other": [], "ctrl": []}
    for ti in range(len(TRIPLES)):
        for ck in CARRIERS:
            for rot in range(3):
                for j in range(3):
                    def anymem(a):
                        rk = Z[f"sel|{ck}|T{ti}|rot{rot}|{a}|clean|rank"][:, :, 3 + 4 * j:3 + 4 * j + 4]
                        return float(rk.min() == 1)
                    hits["self"].append(anymem(TAGS[j]))
                    hits["other"].append(np.mean([anymem(a) for a in TAGS if a != TAGS[j]]))
                    hits["ctrl"].append(anymem("ctrl"))
    tables["rank1_anywhere_members"] = {k: float(np.mean(v)) for k, v in hits.items()}

    # ---- per-member transfer (§4.3 guard): pointed-arm Δz(swap-clean) on each donor/source member, L51-59 ----
    pm_win = WINDOWS["L51-59"]; du, sd = {}, {}
    for base, cell in CELLS.items():
        if not base.startswith("sel|") or cell["arm"] == "ctrl":
            continue
        j = {"A": 0, "B": 1, "C": 2}[cell["arm"]]; X = cell["cats"][j]; Y = cell["donor"][str(j)]
        zc = zwin(f"{base}|clean", pm_win); zs = zwin(f"{base}|swap{j}", pm_win)
        for w in MEMBERS[Y]:
            du.setdefault(w, []).append(float((zs[:, :, CIX[w]] - zc[:, :, CIX[w]]).mean()))
        for w in MEMBERS[X]:
            sd.setdefault(w, []).append(float((zs[:, :, CIX[w]] - zc[:, :, CIX[w]]).mean()))
    tables["per_member_transfer_L51-59"] = {c: {"donor_up": {w: float(np.mean(du[w])) for w in MEMBERS[c]},
                                                "source_down": {w: float(np.mean(sd[w])) for w in MEMBERS[c]}} for c in PRIMARY}
    tables["per_member_consistency"] = {"donor_up_pos": int(sum(np.mean(du[w]) > 0 for w in du)), "n_donor": len(du),
                                        "source_down_neg": int(sum(np.mean(sd[w]) < 0 for w in sd)), "n_source": len(sd)}

    # ---- damage on swaps (ΔNLL, top-1 retention) vs each cell's own clean ----
    dnll, top1r = [], []
    for base in CELLS:
        if not base.startswith("sel|"):
            continue
        cn = float(Z[f"{base}|clean|nll"]); ct = Z[f"{base}|clean|top1"]
        for j in range(3):
            dnll.append(float(Z[f"{base}|swap{j}|nll"]) - cn)
            top1r.append(float((Z[f"{base}|swap{j}|top1"] == ct).mean()))
    tables["damage"] = {"dNLL_mean": float(np.mean(dnll)), "dNLL_max": float(np.max(dnll)),
                        "top1_retention_min": float(np.min(top1r)), "top1_retention_mean": float(np.mean(top1r))}

    # ---- Holm across the two windows for primary S (member, both clusterings) ----
    for clus in ("cluster_triple", "cluster_category"):
        ps = [S.paired_p(tables[f"J_NP|member|{wn}"][clus]["S"]["per_cluster"]) for wn in WINDOWS]
        tables[f"holm_S_JNP_member_{clus}"] = {wn: float(v) for wn, v in zip(WINDOWS, S.holm(ps))}

    json.dump(tables, open(os.path.join(RES, "tagged_categories_select_tables.json"), "w"), indent=1, default=float)

    # ---- figures ----
    keys = ["J_NP|member|L48-50", "J_NP|member|L51-59", "J_NP|label|L48-50", "J_NP|label|L51-59", "RESID_P|member|L48-50", "RESID_P|member|L51-59", "LOGITS|member", "LOGITS|label"]
    fig, axes = plt.subplots(2, len(keys) // 2, figsize=(4 * (len(keys) // 2), 8))
    for ax, key in zip(axes.ravel(), keys):
        T = tables[key]["cluster_triple"]
        for i, q in enumerate(("self", "other", "ctrl")):
            e = T[q]; ax.errorbar(i, e["mean"], yerr=[[e["mean"] - e["ci"][0]], [e["ci"][1] - e["mean"]]], fmt="o", color="k", capsize=3)
            ax.scatter(np.full(len(e["per_cluster"]), i), e["per_cluster"], s=14, alpha=0.6)
        ax.set_xticks(range(3)); ax.set_xticklabels(["pointed", "unpointed", "control"], fontsize=8); ax.axhline(0, color="k", lw=0.5)
        ax.set_title(f"{key}\nS={T['S']['mean']:+.3f} Q={T['Q']['mean']:+.3f} U={T['U']['mean']:+.3f}", fontsize=8)
    plt.tight_layout(); plt.savefig(os.path.join(FIG, "tagged_categories_transfer.png"), dpi=130); plt.close()

    plt.figure(figsize=(7, 4))
    plt.plot(layer_S["layers"], layer_S["member"], "-o", ms=3, label="member S")
    plt.plot(layer_S["layers"], layer_S["label"], "-s", ms=3, label="label S")
    plt.axvspan(48, 50, alpha=0.1, color="C0"); plt.axvspan(51, 59, alpha=0.1, color="C1")
    plt.axhline(0, color="k", lw=0.5); plt.xlabel("layer (block output)"); plt.ylabel("S (pointed - unpointed), J_NP"); plt.legend(); plt.title("tagged_categories: selectivity by layer")
    plt.tight_layout(); plt.savefig(os.path.join(FIG, "tagged_categories_S_by_layer.png"), dpi=130); plt.close()

    # ---- report ----
    def blk(key):
        T = tables[key]; tr = T["cluster_triple"]; ca = T["cluster_category"]
        return (f"- **{key}:** [triple n=8] pointed {cs(tr['self'])}; unpointed {cs(tr['other'])}; control {cs(tr['ctrl'])}. "
                f"**S={cs(tr['S'])}**; Q={cs(tr['Q'])}; U={cs(tr['U'])}; S/U {tr['S_over_U']['ratio']:.2f}. "
                f"[category n=6] S={cs(ca['S'])}; Q={cs(ca['Q'])}; U={cs(ca['U'])}. "
                f"P0(pure) S={cs(T['S_P0_pure'])}; mixed S={cs(T['S_mixed'])}.")

    rep = [f"# H1 · tagged_categories — SELECT (does the pointer transfer unshown members?) — run {META['run_id']}\n",
           "## 1. Question and setup\n",
           f"Every selection result so far scored a word literally in the prompt, so transfer could be lexical echo. Here the pointer selects "
           f"among three tagged *category labels*; the primary endpoint is the **member aggregate** (4 unshown members per category, never a token "
           f"in the prompt). If pointing at a category transfers its members (not just its label), selection is of associated content. "
           f"8 triples over 6 shared identities ({', '.join(PRIMARY)}); 3 rotations; carriers {CARRIERS}; arms A/B/C point at slots 0/1/2, ctrl none; "
           f"source slot j replaced from block 36 by the partner-triple category. Transfer C_j=m_j(swap j)-m_j(clean), m_j=s_bar(donor_j)-s_bar(source_j). "
           f"S=pointed-unpointed, Q=unpointed-control, U=pointed-control; windows L48-50 & L51-59; TWO clusterings: triple (n=8) and category (n=6). "
           f"{META['n_forwards']} forwards; same-source and layer<36 identity asserted per cell at generation. **Extension scale** (6 shared identities, "
           f"overlapping folds), not evaluation-scale independence.\n",
           "## 2. Main findings (primary = J_NP member)\n"]
    for key in ("J_NP|member|L48-50", "J_NP|member|L51-59", "J_NP|label|L48-50", "J_NP|label|L51-59", "RESID_P|member|L48-50", "RESID_P|member|L51-59", "LOGITS|member", "LOGITS|label"):
        rep.append(blk(key))
    rep.append(f"- **S_nat readout-only (natural selectivity, no swap):** " +
               "; ".join(f"{c} L51-59 {cs(tables['S_nat_readout_only']['L51-59'][c])}" for c in RO) + ".")
    rep.append(f"- **S_nat primary triples (clean presence):** L48-50 {cs(tables['S_nat_primary']['L48-50']['S_nat'])}; L51-59 {cs(tables['S_nat_primary']['L51-59']['S_nat'])}.")
    rep.append(f"- **Rank-1-anywhere of pointed members (L24-59):** pointed {tables['rank1_anywhere_members']['self']:.3f}, unpointed {tables['rank1_anywhere_members']['other']:.3f}, control {tables['rank1_anywhere_members']['ctrl']:.3f}.")
    rep.append(f"- **Damage:** ΔNLL mean {tables['damage']['dNLL_mean']:+.4f} (max {tables['damage']['dNLL_max']:+.4f}); top-1 retention min {tables['damage']['top1_retention_min']:.3f} (mean {tables['damage']['top1_retention_mean']:.3f}).")
    rep.append(f"- **Holm-adjusted p (J_NP member S):** triple {json.dumps({k: round(v,4) for k,v in tables['holm_S_JNP_member_cluster_triple'].items()})}; category {json.dumps({k: round(v,4) for k,v in tables['holm_S_JNP_member_cluster_category'].items()})}.\n")

    rep.append("## 3. Complete tables (both clusterings)\n")
    for key in ("J_NP|member|L48-50", "J_NP|member|L51-59", "J_NP|label|L48-50", "J_NP|label|L51-59", "RESID_P|member|L48-50", "RESID_P|member|L51-59", "LOGITS|member", "LOGITS|label"):
        T = tables[key]
        for clus, cl in (("cluster_triple", "triple n=8"), ("cluster_category", "category n=6")):
            D = T[clus]; rep.append(f"### {key} · {cl}\n\n| quantity | mean | 95% CI | signs>0/n | per-cluster |\n|---|---|---|---|---|")
            for q in ("self", "other", "ctrl", "S", "Q", "U"):
                e = D[q]; rep.append(f"| {q} | {e['mean']:+.4f} | [{e['ci'][0]:+.4f},{e['ci'][1]:+.4f}] | {e.get('signs_pos',0)}/{e['n']} | "
                                     + ", ".join(f"{x:+.3f}" for x in e["per_cluster"]) + " |")
            rep.append("")
    rep.append("### Per-member transfer (pointed arm, Δz = swap − clean, L51–59) — the §4.3 guard\n")
    pmc = tables["per_member_consistency"]
    rep.append(f"Donor members moving up: {pmc['donor_up_pos']}/{pmc['n_donor']}; source members moving down: {pmc['source_down_neg']}/{pmc['n_source']}. "
               "If S_member were one member's lexical echo, the members would not move together.\n")
    rep.append("| category | donor-member Δz (installed as donor) | source-member Δz (removed as source) |\n|---|---|---|")
    for c in PRIMARY:
        d = tables["per_member_transfer_L51-59"][c]
        rep.append(f"| {c} | " + " ".join(f"{w}={v:+.2f}" for w, v in d["donor_up"].items())
                   + " | " + " ".join(f"{w}={v:+.2f}" for w, v in d["source_down"].items()) + " |")
    rep.append("")
    rep.append(f"Figures: `figures/tagged_categories_transfer.png`, `figures/tagged_categories_S_by_layer.png`. Machine-readable: `tagged_categories_select_tables.json`.\n")
    rep.append("## 4. Verification and limitations\n\n"
               "- Same-source (slot 0) bitwise equal to clean and layers < 36 identical between futures asserted per cell at generation; donor geometry asserted per swap. Damage above.\n"
               "- Decoys cancel in every pair margin (member and label). No scored member or label occurs in any carrier (asserted at generation).\n"
               "- Extension scale: 6 shared category identities, 8 triples, overlapping RESID_P/direction folds; intervals describe evaluation variability under this procedure, not independent runs. Member holdout not available at K=4 (RESID_P axis uses context holdout only).\n"
               "- Two clusterings (triple n=8, category n=6): a licensed claim needs both. Per §4.3, the per-member distribution guards against renaming one member's lexical echo as category abstraction.\n")
    rep.append("## 5. Interpretation and next decision\n\n_Filled in by hand after reading the tables (gate first, then S_member vs S_label)._\n")
    open(os.path.join(RES, "tagged_categories_select.md"), "w").write("\n".join(rep))
    print("\n".join(rep[:14]))
