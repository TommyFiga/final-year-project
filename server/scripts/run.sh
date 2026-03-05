#!/usr/bin/env bash

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[*] Running server..."

cd "${PROJECT_ROOT}"
export $(grep -v '^#' .env | xargs)
go run ./cmd