#!/usr/bin/env bash

set -e

SCRIPTS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPTS_ROOT}/.." && pwd)"

CLIENT_ROOT="${PROJECT_ROOT}/client"
SERVER_ROOT="${PROJECT_ROOT}/server"
TDLIB_PATH="${CLIENT_ROOT}/tdlib"

export CGO_CFLAGS="-I${TDLIB_PATH}/include"
export CGO_LDFLAGS="-L${TDLIB_PATH}/lib"
export LD_LIBRARY_PATH="${TDLIB_PATH}/lib"

cleanup() {
    echo "[*] Stopping server..."
    pkill -f "cmd" 2>/dev/null || true
}
trap cleanup EXIT

echo "[*] Starting server..."
cd "${SERVER_ROOT}"
export $(grep -v '^#' .env | xargs)
go run ./cmd &
SERVER_PID=$!

echo "[*] Starting client..."
cd "${CLIENT_ROOT}"
export $(grep -v '^#' .env | xargs)
go run ./cmd

echo "[*] Client exited."