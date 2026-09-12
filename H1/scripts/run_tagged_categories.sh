#!/bin/bash
# gate then select, sequential, one GPU
source /venv/main/bin/activate
export HF_HOME=/workspace/.hf_home PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
cd /workspace/tcsif
python H1/scripts/tagged_categories.py gate   > H1/outputs/tagged_categories/log_gate.txt 2>&1 || { echo GATE_FAILED; exit 1; }
python H1/scripts/tagged_categories.py select > H1/outputs/tagged_categories/log_select.txt 2>&1 || { echo SELECT_FAILED; exit 1; }
echo ALL_DONE
