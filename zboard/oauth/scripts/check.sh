#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
: "${GOWORK:=off}"
export GOWORK
test -z "$(gofmt -l cmd internal integration)"
mkdir -p .build
go test -race ./internal/...
go vet ./...
go build -trimpath -o .build/oauth ./cmd/oauth
OAUTH_PLUGIN_BINARY="$(pwd)/.build/oauth" go test -count=1 ./integration/...
node --test tests/*.test.cjs
