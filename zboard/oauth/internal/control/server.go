package control

import (
	"context"
	"encoding/json"
	"net/http"
	"sync"
	"time"

	pluginv1 "github.com/zerodenet/zboard/backend/pkg/pluginapi/v1"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	"github.com/zerodenet/plugins/zboard/oauth/internal/config"
	"github.com/zerodenet/plugins/zboard/oauth/internal/provider"
)

const ID = "zboard.oauth"
const Version = "0.2.0"

type Server struct {
	pluginv1.UnimplementedPluginControlServer
	discovery    map[string]provider.Metadata
	discoveredAt map[string]time.Time
	mu           sync.RWMutex
	config       config.Config
	client       *http.Client
}

func New() *Server { return &Server{client: provider.NewClient()} }

func (s *Server) GetInfo(context.Context, *pluginv1.Empty) (*pluginv1.Info, error) {
	return &pluginv1.Info{Id: ID, Version: Version, Protocol: pluginv1.ProtocolVersion, Capabilities: []string{"zboard.ui.page.v1", "zboard.config.v1", "zboard.identity.provider.v1"}}, nil
}
func (s *Server) Health(context.Context, *pluginv1.Empty) (*pluginv1.HealthResult, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	message := "ready; provider is not configured"
	if s.config.Configured() {
		message = "ready; provider configuration applied; identity provider ready"
	}
	return &pluginv1.HealthResult{Healthy: true, Message: message}, nil
}
func (s *Server) ValidateConfig(_ context.Context, r *pluginv1.ConfigRequest) (*pluginv1.ConfigResult, error) {
	c, err := config.Parse(r.GetConfigJson())
	if err != nil {
		return nil, status.Error(codes.InvalidArgument, err.Error())
	}
	if err := preserveSecrets(&c, r.PreviousConfigJson); err != nil {
		return nil, status.Error(codes.InvalidArgument, err.Error())
	}
	raw, err := json.Marshal(c)
	if err != nil {
		return nil, status.Error(codes.Internal, "configuration encoding failed")
	}
	return &pluginv1.ConfigResult{NormalizedJson: raw}, nil
}
func (s *Server) ApplyConfig(_ context.Context, r *pluginv1.ConfigRequest) (*pluginv1.HealthResult, error) {
	c, err := config.Parse(r.GetConfigJson())
	if err != nil {
		return nil, status.Error(codes.InvalidArgument, err.Error())
	}
	// Applying configuration has no network or user-state side effects.
	s.mu.Lock()
	s.config = c
	s.discovery = nil
	s.mu.Unlock()
	return &pluginv1.HealthResult{Healthy: true, Message: "configuration applied"}, nil
}
func (s *Server) TestConfig(ctx context.Context, r *pluginv1.ConfigRequest) (*pluginv1.HealthResult, error) {
	c, err := config.Parse(r.GetConfigJson())
	if err != nil {
		return nil, status.Error(codes.InvalidArgument, err.Error())
	}
	if len(c.Entries()) == 0 {
		return &pluginv1.HealthResult{Healthy: false, Message: "no providers configured"}, nil
	}
	for _, entry := range c.Entries() {
		if entry.Disabled {
			continue
		}
		if err := provider.Check(ctx, s.client, entry); err != nil {
			return &pluginv1.HealthResult{Healthy: false, Message: err.Error()}, nil
		}
	}
	return &pluginv1.HealthResult{Healthy: true, Message: "provider configuration check passed; client credentials and actual authorization have not been verified"}, nil
}
