package main

import (
	pluginv1 "github.com/zerodenet/zboard/backend/pkg/pluginapi/v1"
	"zboard.local/plugins/oauth/internal/control"
)

func main() { pluginv1.Serve(control.New()) }
