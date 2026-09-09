package control

import (
	"context"
	"encoding/json"
	"errors"
	"github.com/zerodenet/plugins/zboard/oauth/internal/config"
	pluginv1 "github.com/zerodenet/zboard/backend/pkg/pluginapi/v1"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

func (s *Server) ListIdentityProviders(context.Context, *pluginv1.Empty) (*pluginv1.IdentityProviderList, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := &pluginv1.IdentityProviderList{}
	for _, c := range s.config.Entries() {
		if !c.Disabled {
			out.Providers = append(out.Providers, &pluginv1.IdentityProviderOption{Id: c.ID, Name: c.Name})
		}
	}
	return out, nil
}
func (s *Server) DescribeConfig(_ context.Context, r *pluginv1.ConfigRequest) (*pluginv1.ConfigResult, error) {
	c, err := config.Parse(r.ConfigJson)
	if err != nil {
		return nil, status.Error(codes.InvalidArgument, "invalid saved configuration")
	}
	entries := []map[string]any{}
	for _, entry := range c.Entries() {
		hasSecret := entry.ClientSecret != ""
		entry.ClientSecret = ""
		entry.KeepSecret = false
		raw, _ := json.Marshal(entry)
		view := map[string]any{}
		_ = json.Unmarshal(raw, &view)
		view["has_secret"] = hasSecret
		entries = append(entries, view)
	}
	raw, _ := json.Marshal(map[string]any{"providers": entries})
	return &pluginv1.ConfigResult{NormalizedJson: raw}, nil
}
func preserveSecrets(c *config.Config, previous []byte) error {
	entries := c.Entries()
	var old config.Config
	if len(previous) != 0 {
		var err error
		old, err = config.Parse(previous)
		if err != nil {
			return errors.New("invalid prior configuration")
		}
	}
	for i := range entries {
		entry := &entries[i]
		if !entry.KeepSecret {
			continue
		}
		if entry.ClientSecret != "" {
			return errors.New("choose either retaining or replacing a client secret")
		}
		found := false
		for _, prior := range old.Entries() {
			if prior.ID == entry.ID && prior.Issuer == entry.Issuer && prior.ClientID == entry.ClientID && prior.Protocol == entry.Protocol && prior.Preset == entry.Preset && prior.TokenEndpoint == entry.TokenEndpoint && prior.TokenAuthMethod == entry.TokenAuthMethod {
				entry.ClientSecret = prior.ClientSecret
				found = true
				break
			}
		}
		if !found {
			return errors.New("re-enter the secret when changing the client or provider endpoints")
		}
		entry.KeepSecret = false
	}
	if c.Providers != nil {
		c.Providers = entries
	} else if len(entries) == 1 {
		*c = entries[0]
	}
	return nil
}
