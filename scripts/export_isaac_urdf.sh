#!/bin/bash
# Exports a resolved URDF for Isaac Sim 5.1.0 import.
# Replaces package:// URIs with absolute paths so Isaac Sim finds the meshes.
#
# Usage: bash scripts/export_isaac_urdf.sh
# Output: src/amiibot_description/urdf/isaac/amiibot_isaac.urdf

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_DIR="$(dirname "$SCRIPT_DIR")"

source "$WS_DIR/install/setup.bash"

PKG_PATH=$(ros2 pkg prefix amiibot_description)/share/amiibot_description
OUT_DIR="$WS_DIR/src/amiibot_description/urdf/isaac"
OUT_FILE="$OUT_DIR/amiibot_isaac.urdf"

mkdir -p "$OUT_DIR"

xacro "$WS_DIR/src/amiibot_description/urdf/amiibot_isaac.urdf.xacro" \
  | sed "s|package://amiibot_description|${PKG_PATH}|g" \
  > "$OUT_FILE"

echo "Exported: $OUT_FILE"
echo "Meshes:"
grep "mesh filename" "$OUT_FILE"
