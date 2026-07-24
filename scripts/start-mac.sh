#!/usr/bin/env bash
open http://localhost:5173 2>/dev/null || true
exec "$(dirname "$0")/dev.sh"
