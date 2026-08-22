#!/usr/bin/env bash
# Silicon Dreams · Module 3 · First-run PDK installer.
set -euo pipefail

PDK_ROOT="${PDK_ROOT:-$HOME/.volare/pdks}"

echo "==> Installing sky130A PDK into $PDK_ROOT"

# Use the correct image and install volare first
docker run --rm -v "$PDK_ROOT":/pdk \
  ghcr.io/librelane/librelane:3.0.10 \
  /bin/sh -c "
    python3 -m pip install volare
    python3 -m volare enable --pdk sky130 --pdk-root /pdk
  "

echo "==> Done. PDK_ROOT=$PDK_ROOT"
echo "Add this to your shell rc:"
echo "  export PDK_ROOT=$PDK_ROOT"
