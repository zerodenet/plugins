package control

import (
	"context"
	"encoding/json"
	pluginv1 "github.com/zerodenet/zboard/backend/pkg/pluginapi/v1"
	"io"
	"net/http"
	"strings"
	"testing"
)

func TestGitHubAndCustomOAuth2UseSelectedEndpointsAndStableIdentity(t *testing.T) {
	for _, preset := range []string{"github", "custom"} {
		t.Run(preset, func(t *testing.T) {
			s := New()
			c := map[string]any{"providers": []any{map[string]any{"id": "github", "preset": "github", "client_id": "github-client", "client_secret": "github-secret"}, map[string]any{"id": "custom", "name": "Company", "preset": "custom", "protocol": "oauth2", "issuer": "https://id.example.com", "authorization_endpoint": "https://id.example.com/auth", "token_endpoint": "https://id.example.com/token", "userinfo_endpoint": "https://id.example.com/me", "subject_field": "data.id", "email_field": "data.email", "email_verified_field": "data.verified", "client_id": "custom-client", "client_secret": "custom-secret", "token_auth_method": "post"}}}
			raw, _ := json.Marshal(c)
			if _, err := s.ApplyConfig(context.Background(), &pluginv1.ConfigRequest{ConfigJson: raw}); err != nil {
				t.Fatal(err)
			}
			tokenCalls := 0
			profileCalls := 0
			s.client = &http.Client{Transport: identityTransport(func(r *http.Request) (*http.Response, error) {
				var result any
				switch r.URL.Path {
				case "/login/oauth/access_token", "/token":
					tokenCalls++
					r.ParseForm()
					if r.Form.Get("client_id") != preset+"-client" || r.Form.Get("client_secret") != preset+"-secret" || r.Form.Get("code_verifier") != strings.Repeat("v", 43) || r.Form.Get("redirect_uri") != "https://panel.example.com/api/v1/auth/oidc/callback" {
						t.Fatal("wrong provider credentials or missing PKCE binding")
					}
					result = map[string]any{"access_token": "provider-private-token", "token_type": "bearer"}
				case "/user":
					profileCalls++
					result = map[string]any{"id": json.Number("9007199254740993"), "login": "mutable-name", "email": "untrusted@example.com"}
				case "/user/emails":
					profileCalls++
					result = []any{map[string]any{"email": "ignored@example.com", "primary": true, "verified": false}, map[string]any{"email": "verified@example.com", "primary": true, "verified": true}}
				case "/me":
					profileCalls++
					result = map[string]any{"data": map[string]any{"id": "stable-custom-id", "email": "verified@example.com", "verified": true}}
				default:
					t.Fatalf("unexpected endpoint %s", r.URL)
				}
				if r.Method == "GET" && r.Header.Get("Authorization") != "Bearer provider-private-token" {
					t.Fatal("userinfo missing access token")
				}
				b, _ := json.Marshal(result)
				return &http.Response{StatusCode: 200, Header: http.Header{"Content-Type": []string{"application/json"}}, Body: io.NopCloser(strings.NewReader(string(b)))}, nil
			})}
			list, err := s.ListIdentityProviders(context.Background(), &pluginv1.Empty{})
			if err != nil || len(list.Providers) != 2 {
				t.Fatal("multiple provider catalog missing")
			}
			info, err := s.GetIdentityProvider(context.Background(), &pluginv1.IdentityProviderRequest{ProviderId: preset})
			if err != nil || info.Protocol != "oauth2" || info.ProviderId != preset {
				t.Fatal("provider selection missing", err)
			}
			got, err := s.ExchangeIdentity(context.Background(), &pluginv1.IdentityExchange{ProviderId: preset, Issuer: info.Issuer, Code: "code", Nonce: strings.Repeat("n", 43), PkceVerifier: strings.Repeat("v", 43), RedirectUri: "https://panel.example.com/api/v1/auth/oidc/callback"})
			if err != nil || got.Email != "verified@example.com" || !got.EmailVerified || tokenCalls != 1 || profileCalls == 0 {
				t.Fatalf("identity failed: %v %v", got, err)
			}
			want := "stable-custom-id"
			if preset == "github" {
				want = "9007199254740993"
			}
			if got.Subject != want {
				t.Fatal("lost stable subject precision")
			}
			if _, err := s.GetIdentityProvider(context.Background(), &pluginv1.IdentityProviderRequest{ProviderId: "unknown"}); err == nil {
				t.Fatal("unknown provider fell back")
			}
		})
	}
}
func TestConfigurationProjectionAndSecretRetention(t *testing.T) {
	s := New()
	ctx := context.Background()
	old := []byte(`{"providers":[{"id":"gh","preset":"github","client_id":"client","client_secret":"never-echo"},{"id":"google","preset":"google","client_id":"google","client_secret":"other-secret"}]}`)
	view, err := s.DescribeConfig(ctx, &pluginv1.ConfigRequest{ConfigJson: old})
	if err != nil || strings.Contains(string(view.NormalizedJson), "never-echo") || strings.Contains(string(view.NormalizedJson), "other-secret") || !strings.Contains(string(view.NormalizedJson), `"has_secret":true`) {
		t.Fatal("secret projection failed")
	}
	next := []byte(`{"providers":[{"id":"gh","preset":"github","client_id":"client","disabled":true,"keep_secret":true}]}`)
	out, err := s.ValidateConfig(ctx, &pluginv1.ConfigRequest{ConfigJson: next, PreviousConfigJson: old})
	if err != nil || !strings.Contains(string(out.NormalizedJson), "never-echo") || strings.Contains(string(out.NormalizedJson), "other-secret") {
		t.Fatal("retention or deletion incorrect", err)
	}
	if _, err := s.ApplyConfig(ctx, &pluginv1.ConfigRequest{ConfigJson: out.NormalizedJson}); err != nil {
		t.Fatal(err)
	}
	catalog, _ := s.ListIdentityProviders(ctx, &pluginv1.Empty{})
	if len(catalog.Providers) != 0 {
		t.Fatal("disabled provider visible")
	}
	changed := []byte(strings.Replace(string(next), `"client_id":"client"`, `"client_id":"attacker"`, 1))
	if _, err := s.ValidateConfig(ctx, &pluginv1.ConfigRequest{ConfigJson: changed, PreviousConfigJson: old}); err == nil {
		t.Fatal("secret transferred to changed client")
	}
	if _, err := s.ValidateConfig(ctx, &pluginv1.ConfigRequest{ConfigJson: next}); err == nil {
		t.Fatal("secret retention without host snapshot accepted")
	}
}
func TestOAuthProfileVerificationIsStrictAndSubjectIsRequired(t *testing.T) {
	for _, v := range []any{nil, true, 1.5, map[string]any{"id": "wrong"}} {
		if profileString(v) != "" {
			t.Fatal("invalid profile subject accepted")
		}
	}
	if profileString(json.Number("9223372036854775808")) != "" {
		t.Fatal("out-of-range subject accepted")
	}
	if profileField(map[string]any{"data": map[string]any{"verified": "true"}}, "data.verified") == true {
		t.Fatal("string accepted as verification boolean")
	}
}
