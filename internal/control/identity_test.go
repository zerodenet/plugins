package control

import (
	"context"
	"crypto"
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"io"
	"math/big"
	"net/http"
	"strings"
	"testing"
	"time"

	pluginv1 "github.com/zerodenet/zboard/backend/pkg/pluginapi/v1"
)

type identityTransport func(*http.Request) (*http.Response, error)

func (f identityTransport) RoundTrip(r *http.Request) (*http.Response, error) { return f(r) }
func signIdentity(t *testing.T, key *rsa.PrivateKey, claims map[string]any) string {
	t.Helper()
	header := base64.RawURLEncoding.EncodeToString([]byte(`{"alg":"RS256","kid":"test-key"}`))
	raw, _ := json.Marshal(claims)
	input := header + "." + base64.RawURLEncoding.EncodeToString(raw)
	digest := sha256.Sum256([]byte(input))
	signature, err := rsa.SignPKCS1v15(rand.Reader, key, crypto.SHA256, digest[:])
	if err != nil {
		t.Fatal(err)
	}
	return input + "." + base64.RawURLEncoding.EncodeToString(signature)
}
func TestOIDCExchangeVerifiesSignatureNonceAudienceIssuerAndPKCE(t *testing.T) {
	key, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		t.Fatal(err)
	}
	badKey, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		t.Fatal(err)
	}
	nonce := strings.Repeat("n", 43)
	verifier := strings.Repeat("v", 43)
	cases := []struct {
		name         string
		change       func(map[string]any)
		badSignature bool
		want         bool
	}{
		{name: "valid", want: true},
		{name: "nonce", change: func(m map[string]any) { m["nonce"] = "wrong" }},
		{name: "audience", change: func(m map[string]any) { m["aud"] = "another-client" }},
		{name: "issuer", change: func(m map[string]any) { m["iss"] = "https://attacker.example.com" }},
		{name: "expired", change: func(m map[string]any) { m["exp"] = time.Now().Add(-time.Hour).Unix() }},
		{name: "missing-subject", change: func(m map[string]any) { delete(m, "sub") }},
		{name: "wrong-authorized-party", change: func(m map[string]any) { m["azp"] = "another-client" }},
		{name: "multiple-audiences", change: func(m map[string]any) { m["aud"] = []string{"client", "other"} }},
		{name: "bad-access-token-binding", change: func(m map[string]any) { m["at_hash"] = "invalid" }},
		{name: "signature", badSignature: true},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			claims := map[string]any{"iss": "https://id.example.com", "sub": "opaque-subject", "aud": "client", "iat": time.Now().Unix(), "exp": time.Now().Add(time.Minute).Unix(), "nonce": nonce}
			if tc.change != nil {
				tc.change(claims)
			}
			signingKey := key
			if tc.badSignature {
				signingKey = badKey
			}
			idToken := signIdentity(t, signingKey, claims)
			tokenCalls := 0
			s := New()
			s.client = &http.Client{Transport: identityTransport(func(r *http.Request) (*http.Response, error) {
				var response any
				switch r.URL.Path {
				case "/.well-known/openid-configuration":
					if r.Header.Get("Authorization") != "" || r.Method != "GET" {
						t.Fatal("discovery received credentials")
					}
					response = map[string]any{"issuer": "https://id.example.com", "authorization_endpoint": "https://id.example.com/auth", "token_endpoint": "https://id.example.com/token", "jwks_uri": "https://id.example.com/keys", "response_types_supported": []string{"code"}, "subject_types_supported": []string{"public"}, "id_token_signing_alg_values_supported": []string{"RS256"}, "code_challenge_methods_supported": []string{"S256"}}
				case "/token":
					tokenCalls++
					if r.Method != "POST" {
						t.Fatal("invalid exchange method")
					}
					if err := r.ParseForm(); err != nil {
						t.Fatal(err)
					}
					client, secret, ok := r.BasicAuth()
					if !ok || client != "client" || secret != "secret" || r.Form.Get("code_verifier") != verifier || r.Form.Get("code") != "one-time-code" || r.Form.Get("redirect_uri") != "https://panel.example.com/api/v1/auth/oidc/callback" {
						t.Fatal("exchange lacked client/PKCE/redirect binding")
					}
					response = map[string]any{"access_token": "private-access-token", "token_type": "Bearer", "id_token": idToken}
				case "/keys":
					if r.Header.Get("Authorization") != "" {
						t.Fatal("JWKS received credentials")
					}
					response = map[string]any{"keys": []any{map[string]any{"kty": "RSA", "kid": "test-key", "use": "sig", "alg": "RS256", "n": base64.RawURLEncoding.EncodeToString(key.PublicKey.N.Bytes()), "e": base64.RawURLEncoding.EncodeToString(big.NewInt(int64(key.PublicKey.E)).Bytes())}}}
				default:
					t.Fatalf("unexpected provider request %s", r.URL.Path)
				}
				raw, _ := json.Marshal(response)
				return &http.Response{StatusCode: 200, Header: http.Header{"Content-Type": []string{"application/json"}}, Body: io.NopCloser(strings.NewReader(string(raw)))}, nil
			})}
			_, err := s.ApplyConfig(context.Background(), &pluginv1.ConfigRequest{ConfigJson: []byte(`{"issuer":"https://id.example.com","client_id":"client","client_secret":"secret"}`)})
			if err != nil {
				t.Fatal(err)
			}
			result, err := s.ExchangeIdentity(context.Background(), &pluginv1.IdentityExchange{Code: "one-time-code", RedirectUri: "https://panel.example.com/api/v1/auth/oidc/callback", Nonce: nonce, PkceVerifier: verifier, Issuer: "https://id.example.com"})
			if tc.want {
				if err != nil || result.Subject != "opaque-subject" || tokenCalls != 1 {
					t.Fatalf("valid exchange: %v", err)
				}
			} else if err == nil {
				t.Fatal("invalid ID token accepted")
			}
			if err != nil && (strings.Contains(err.Error(), "private-access-token") || strings.Contains(err.Error(), idToken)) {
				t.Fatal("token leaked in error")
			}
		})
	}
}
func TestIdentityExchangeRejectsUnsafeCallbacksBeforeNetworking(t *testing.T) {
	for _, callback := range []string{"http://panel.example.com/api/v1/auth/oidc/callback", "https://panel.example.com/wrong", "https://user:pass@panel.example.com/api/v1/auth/oidc/callback", "https://panel.example.com/api/v1/auth/oidc/callback?extra=value"} {
		if validCallback(callback) {
			t.Errorf("unsafe callback accepted: %s", callback)
		}
	}
	if !validCallback("http://127.0.0.1:18090/api/v1/auth/oidc/callback") {
		t.Fatal("local development callback rejected")
	}
	if _, err := New().ExchangeIdentity(context.Background(), nil); err == nil {
		t.Fatal("empty exchange accepted")
	}
}
