#!/usr/bin/env bash

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TDLIB_PATH="${PROJECT_ROOT}/tdlib"

export CGO_CFLAGS="-I${TDLIB_PATH}/include"
export CGO_LDFLAGS="-L${TDLIB_PATH}/lib"
export LD_LIBRARY_PATH="${TDLIB_PATH}/lib"

echo "[*] Running client..."

cd "${PROJECT_ROOT}"
export $(grep -v '^#' .env | xargs)
go run ./cmd