#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
sh zboard/oauth/scripts/check.sh
