#!/bin/bash
# Rebuild the TCSIF environment after an instance recycle (recipe from CLAUDE.md).
# Sequential on purpose: packages -> jlens -> primary model -> three lenses -> hash check -> Qwen3-32B lens ckpt -> Qwen3-32B model.
set -euo pipefail
source /venv/main/bin/activate
export HF_HOME=/workspace/.hf_home PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True HF_HUB_ENABLE_HF_TRANSFER=0
export HF_TOKEN="$(cat /workspace/.hf_home/token)"
cd /workspace/tcsif
echo "== $(date -u +%FT%TZ) packages"
uv pip install -q transformers==5.15.0 safetensors accelerate scipy matplotlib huggingface_hub
echo "== $(date -u +%FT%TZ) jacobian-lens @581d398"
if [ ! -d /workspace/jacobian-lens ]; then git clone -q https://github.com/anthropics/jacobian-lens /workspace/jacobian-lens; fi
(cd /workspace/jacobian-lens && git checkout -q 581d398 && uv pip install -q -e . --no-deps)
python -c "import transformers, torch, jlens; print('transformers', transformers.__version__, 'torch', torch.__version__, 'jlens ok')"
echo "== $(date -u +%FT%TZ) primary model Qwen/Qwen3.6-27B@6a9e13bd"
python - <<'EOF'
from huggingface_hub import snapshot_download
p = snapshot_download("Qwen/Qwen3.6-27B", revision="6a9e13bd6fc8f0983b9b99948120bc37f49c13e9", max_workers=8)
print("model at", p)
EOF
echo "== $(date -u +%FT%TZ) lens files (J_NP, J_CB, R_CB) at pinned revisions"
python - <<'EOF'
import json, hashlib
from huggingface_hub import hf_hub_download
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        while (b:=f.read(1<<24)): h.update(b)
    return h.hexdigest()
reg = json.load(open("common/configs/instrument_registry.json"))["instruments"]
for nm in ["J_NP","J_CB","R_CB"]:
    e = reg[nm]
    p = hf_hub_download(e["hf_repo"], e["file"], revision=e["hf_revision"])
    got = sha(p)
    print(nm, p, "sha OK" if got==e["sha256"] else f"SHA MISMATCH {got} != {e['sha256']}")
    assert got == e["sha256"]
EOF
echo "== $(date -u +%FT%TZ) Qwen3-32B lens checkpoint (n=80 fit) + model @9216db57"
python - <<'EOF'
import json
from huggingface_hub import hf_hub_download, snapshot_download
reg = json.load(open("common/configs/instrument_registry_qwen3_32b.json"))
e = reg["instruments"]["J_NP"]
p = hf_hub_download(e["hf_repo"], e["file"], revision=e["hf_revision"]); print("32b lens ckpt at", p)
p = snapshot_download(reg["model"]["repo"], revision=reg["model"]["revision"], max_workers=8); print("32b model at", p)
EOF
echo "== $(date -u +%FT%TZ) done"; du -sh /workspace/.hf_home
