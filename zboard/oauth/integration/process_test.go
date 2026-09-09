package integration

import (
	"context"
	"os"
	"os/exec"
	"strings"
	"testing"
	"time"

	hcplugin "github.com/hashicorp/go-plugin"
	pluginv1 "github.com/zerodenet/zboard/backend/pkg/pluginapi/v1"
)

func TestRealPluginProcessCanRestartAndConfigure(t *testing.T) {
	binary := os.Getenv("OAUTH_PLUGIN_BINARY")
	if binary == "" {
		t.Skip("set OAUTH_PLUGIN_BINARY to test built executable")
	}
	for range 2 {
		client := hcplugin.NewClient(&hcplugin.ClientConfig{HandshakeConfig: pluginv1.Handshake, Plugins: pluginv1.ClientMap(), Cmd: exec.Command(binary), AllowedProtocols: []hcplugin.Protocol{hcplugin.ProtocolGRPC}, AutoMTLS: true, SkipHostEnv: true, StartTimeout: 10 * time.Second})
		func() {
			defer client.Kill()
			rpc, err := client.Client()
			if err != nil {
				t.Fatal(err)
			}
			raw, err := rpc.Dispense("control")
			if err != nil {
				t.Fatal(err)
			}
			api := raw.(pluginv1.PluginControlClient)
			ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
			defer cancel()
			info, err := api.GetInfo(ctx, &pluginv1.Empty{})
			if err != nil || info.Id != "zboard.oauth" || info.Protocol != 1 || len(info.Capabilities) != 3 {
				t.Fatalf("invalid handshake: %v", err)
			}
			config := &pluginv1.ConfigRequest{ConfigJson: []byte(`{}`)}
			normalized, err := api.ValidateConfig(ctx, config)
			if err != nil {
				t.Fatal(err)
			}
			config.ConfigJson = normalized.NormalizedJson
			if _, err = api.ApplyConfig(ctx, config); err != nil {
				t.Fatal(err)
			}
			health, err := api.Health(ctx, &pluginv1.Empty{})
			if err != nil || !health.Healthy {
				t.Fatalf("unhealthy process: %v", err)
			}
			result, err := api.TestConfig(ctx, config)
			if err != nil || result.Healthy {
				t.Fatal("unconfigured diagnostic should fail")
			}
			multi := &pluginv1.ConfigRequest{ConfigJson: []byte(`{"providers":[{"id":"github","preset":"github","client_id":"client","client_secret":"secret"},{"id":"google","preset":"google","client_id":"google","disabled":true}]}`)}
			normalized, err = api.ValidateConfig(ctx, multi)
			if err != nil {
				t.Fatal(err)
			}
			multi.ConfigJson = normalized.NormalizedJson
			if _, err = api.ApplyConfig(ctx, multi); err != nil {
				t.Fatal(err)
			}
			catalog, err := api.ListIdentityProviders(ctx, &pluginv1.Empty{})
			if err != nil || len(catalog.Providers) != 1 || catalog.Providers[0].Id != "github" {
				t.Fatal("process provider catalog failed", err)
			}
			provider, err := api.GetIdentityProvider(ctx, &pluginv1.IdentityProviderRequest{ProviderId: "github"})
			if err != nil || provider.Protocol != "oauth2" || provider.ProviderId != "github" {
				t.Fatal("process selected metadata failed", err)
			}
			view, err := api.DescribeConfig(ctx, multi)
			if err != nil || strings.Contains(string(view.NormalizedJson), `"client_secret"`) || !strings.Contains(string(view.NormalizedJson), `"has_secret":true`) {
				t.Fatal("process config projection failed", err)
			}

		}()
	}
}
