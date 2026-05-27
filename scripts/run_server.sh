#!/usr/bin/env bash

set -e

SCRIPTS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPTS_ROOT}/.." && pwd)"

SERVER_ROOT="${PROJECT_ROOT}/server"

echo "[*] Starting server..."
cd "${SERVER_ROOT}"
export $(grep -v '^#' .env | xargs)
go run ./cmd