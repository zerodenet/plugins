package main

import (
	"github.com/zerodenet/plugins/zboard/oauth/internal/control"
	pluginv1 "github.com/zerodenet/zboard/backend/pkg/pluginapi/v1"
)

func main() { pluginv1.Serve(control.New()) }
