"""Model, tokenizer and lens loading pinned to the instrument registry.

Every scientific script loads the model and lenses through this module so that the
revision, dtype, attention implementation, and lens hashes are asserted in one place.
"""
import os, json, glob, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, "..", ".."))
MODEL_KEY = os.environ.get("TCSIF_MODEL", "")           # "" = primary model; "qwen3_32b" = pure-attention replication
REGISTRY_PATH = os.path.join(PROJECT, "common", "configs", "instrument_registry%s.json" % (("_" + MODEL_KEY) if MODEL_KEY else ""))
OUT_ROOT = os.path.join(PROJECT, "replication_" + MODEL_KEY) if MODEL_KEY else PROJECT
REGISTRY = json.load(open(REGISTRY_PATH))

os.environ.setdefault("HF_HOME", REGISTRY["model"]["hf_home"])
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

MODEL = REGISTRY["model"]["repo"]
REV = REGISTRY["model"]["revision"]
N_BLOCKS = REGISTRY["model"]["n_blocks"]
D_MODEL = REGISTRY["model"]["d_model"]
N_SRC = N_BLOCKS - 1  # lens source layers 0..62


def sha256(path, buf=1 << 24):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while (b := f.read(buf)):
            h.update(b)
    return h.hexdigest()


def make_tokenizer():
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(MODEL, revision=REV)


def load_model(attn_impl=None):
    import torch
    from transformers import AutoModelForCausalLM
    attn_impl = attn_impl or REGISTRY["model"]["attn_implementation"]
    m = AutoModelForCausalLM.from_pretrained(MODEL, revision=REV, dtype=torch.bfloat16,
                                             device_map="cuda", attn_implementation=attn_impl)
    m.eval()
    return m


def layer_types(model):
    """Per-block mixer type. Dense transformers (Qwen3) have no `layer_types` field: every block is full attention."""
    cfg = model.config
    tc = getattr(cfg, "text_config", cfg)
    lt = getattr(tc, "layer_types", None)
    if lt is None:
        return ["full_attention"] * N_BLOCKS
    lt = list(lt)
    assert len(lt) == N_BLOCKS, f"layer_types len {len(lt)} != {N_BLOCKS}"
    return lt


def out_dir(*parts):
    """Output/results root, per model. Primary model writes in place; a replication writes under replication_<key>/."""
    d = os.path.join(OUT_ROOT, *parts); os.makedirs(d, exist_ok=True); return d


def full_attention_layers(model):
    return [i for i, t in enumerate(layer_types(model)) if t == "full_attention"]


def linear_attention_layers(model):
    return [i for i, t in enumerate(layer_types(model)) if t == "linear_attention"]


def lens_path(name):
    e = REGISTRY["instruments"][name]
    if e.get("local_path") and os.path.exists(e["local_path"]):
        return e["local_path"]
    repo_dir = "models--" + e["hf_repo"].replace("/", "--")
    p = os.path.join(os.environ["HF_HOME"], "hub", repo_dir, "snapshots", e["hf_revision"], e["file"])
    if not os.path.exists(p):
        hits = sorted(glob.glob(os.path.join(os.environ["HF_HOME"], "hub", repo_dir, "snapshots", "*", e["file"])))
        assert hits, f"lens file for {name} not found under {repo_dir}"
        p = hits[-1]
    return p


def load_lenses(names=("J_NP",), device="cuda", verify_sha=True):
    """Load lenses by registry name. Jacobians moved to `device` as float32."""
    from jlens.lens import JacobianLens
    out = {}
    for nm in names:
        e = REGISTRY["instruments"][nm]
        p = lens_path(nm)
        if verify_sha:
            got = sha256(p)
            assert got == e["sha256"], f"{nm} sha256 mismatch: {got} != {e['sha256']}"
        L = JacobianLens.load(p)
        assert L.source_layers == list(range(N_SRC)), f"{nm} unexpected layer map"
        L.jacobians = {l: J.to(device) for l, J in L.jacobians.items()}
        out[nm] = L
    return out


def manifest_block():
    """Immutable pins for run manifests."""
    import torch, transformers
    return {"model": REGISTRY["model"], "instruments": {k: {kk: vv for kk, vv in v.items() if kk != "stored_meta"}
                                                        for k, v in REGISTRY["instruments"].items()},
            "software": {"torch": torch.__version__, "transformers": transformers.__version__,
                         "jlens_commit": REGISTRY["software"]["jlens_commit"]}}
