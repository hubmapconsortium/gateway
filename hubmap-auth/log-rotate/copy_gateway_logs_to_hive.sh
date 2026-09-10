#!/bin/bash
set -euo pipefail

SOURCE_DIR="/opt/repositories/vm001-dev/gateway/hubmap-auth/log"
DEST_DIR="/hive/hubmap/data/gateway-logs/vm001-dev"

mkdir -p "$DEST_DIR"

rsync -a --ignore-existing --include='*.log-*.gz' --exclude='*' "$SOURCE_DIR"/ "$DEST_DIR"/