#!/bin/bash
set -e
source /venv/main/bin/activate
export HF_HOME=/workspace/.hf_home PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
cd /workspace/tcsif
echo "=== natural_modulation evaluate"; python H1/scripts/natural_modulation.py evaluate
echo "=== task_state_modulation evaluate"; python H1/scripts/task_state_modulation.py evaluate
echo "=== tagged_selection evaluate"; python H1/scripts/tagged_selection.py evaluate
echo "=== CHAIN DONE"
