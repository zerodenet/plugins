package control

import (
	"context"
	"strings"
	"sync"
	"testing"

	pluginv1 "github.com/zerodenet/zboard/backend/pkg/pluginapi/v1"
)

func TestHostBootstrapSaveAndRollback(t *testing.T) {
	s := New()
	ctx := context.Background()
	if _, err := s.ApplyConfig(ctx, &pluginv1.ConfigRequest{ConfigJson: []byte(`{}`)}); err != nil {
		t.Fatal(err)
	}
	good := &pluginv1.ConfigRequest{ConfigJson: []byte(`{"issuer":"https://id.example.com","client_id":"client","client_secret":"supersecret"}`), Revision: 1}
	normalized, err := s.ValidateConfig(ctx, good)
	if err != nil || !strings.Contains(string(normalized.NormalizedJson), "openid") {
		t.Fatal("normalization failed")
	}
	if _, err = s.ApplyConfig(ctx, good); err != nil {
		t.Fatal(err)
	}
	if _, err = s.ApplyConfig(ctx, &pluginv1.ConfigRequest{ConfigJson: []byte(`{"client_secret":"supersecret","invalid":true}`)}); err == nil || strings.Contains(err.Error(), "supersecret") {
		t.Fatal("invalid config accepted or secret leaked")
	}
	health, _ := s.Health(ctx, &pluginv1.Empty{})
	if !health.Healthy || !strings.Contains(health.Message, "applied") || strings.Contains(health.Message, "supersecret") {
		t.Fatal("failed config changed state or health leaked secret")
	}
	// Host rollback can apply an older revision after its persistence fails.
	if _, err = s.ApplyConfig(ctx, &pluginv1.ConfigRequest{ConfigJson: []byte(`{}`), Revision: 0}); err != nil {
		t.Fatal(err)
	}
	health, _ = s.Health(ctx, &pluginv1.Empty{})
	if !strings.Contains(health.Message, "not configured") {
		t.Fatal("rollback failed")
	}
	result, err := s.TestConfig(ctx, &pluginv1.ConfigRequest{ConfigJson: []byte(`{}`)})
	if err != nil || result.Healthy {
		t.Fatal("unconfigured diagnostic succeeded")
	}
}
func TestControlIsSafeDuringConcurrentHealthAndApply(t *testing.T) {
	s := New()
	var wg sync.WaitGroup
	for range 20 {
		wg.Go(func() {
			_, _ = s.ApplyConfig(context.Background(), &pluginv1.ConfigRequest{ConfigJson: []byte(`{}`)})
			_, _ = s.Health(context.Background(), &pluginv1.Empty{})
		})
	}
	wg.Wait()
}
