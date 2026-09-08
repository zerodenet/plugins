package provider

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"strings"
	"testing"

	"zboard.local/plugins/oauth/internal/config"
)

type transportFunc func(*http.Request) (*http.Response, error)

func (f transportFunc) RoundTrip(r *http.Request) (*http.Response, error) { return f(r) }
func goodMetadata() Metadata {
	return Metadata{Issuer: "https://id.example.com/realm", AuthorizationEndpoint: "https://id.example.com/authorize", TokenEndpoint: "https://id.example.com/token", JWKSURI: "https://id.example.com/keys", ResponseTypes: []string{"code"}, SubjectTypes: []string{"public"}, SigningAlgorithms: []string{"RS256"}, PKCEMethods: []string{"S256"}, Scopes: []string{"openid", "email"}}
}
func TestDiscoveryChecksMetadataWithoutSendingCredentials(t *testing.T) {
	c := config.Config{Issuer: "https://id.example.com/realm", ClientID: "sensitive-id", ClientSecret: "sensitive-secret", Scopes: []string{"openid"}}
	m := goodMetadata()
	client := &http.Client{Transport: transportFunc(func(r *http.Request) (*http.Response, error) {
		if r.Method != "GET" || r.URL.String() != c.Issuer+"/.well-known/openid-configuration" || r.Body != nil || r.Header.Get("Authorization") != "" || strings.Contains(r.URL.String(), c.ClientSecret) {
			t.Fatal("diagnostic leaked credentials or used wrong request")
		}
		raw, _ := json.Marshal(m)
		return &http.Response{StatusCode: 200, Body: io.NopCloser(strings.NewReader(string(raw))), Header: make(http.Header)}, nil
	})}
	if err := Check(context.Background(), client, c); err != nil {
		t.Fatal(err)
	}
	cases := []struct {
		name   string
		mutate func(*Metadata)
	}{
		{"issuer", func(m *Metadata) { m.Issuer += "/" }},
		{"endpoint", func(m *Metadata) { m.TokenEndpoint = "http://id.example.com/token" }},
		{"private", func(m *Metadata) { m.JWKSURI = "https://169.254.169.254/keys" }},
		{"flow", func(m *Metadata) { m.ResponseTypes = []string{"token"} }},
		{"subject", func(m *Metadata) { m.SubjectTypes = nil }},
		{"algorithm", func(m *Metadata) { m.SigningAlgorithms = []string{"none", "HS256"} }},
		{"pkce", func(m *Metadata) { m.PKCEMethods = []string{"plain"} }},
		{"scope", func(m *Metadata) { m.Scopes = []string{"profile"} }},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			m = goodMetadata()
			tc.mutate(&m)
			if Check(context.Background(), client, c) == nil {
				t.Fatal("bad metadata accepted")
			}
		})
	}
	m = goodMetadata()
	m.PKCEMethods = nil
	if err := Check(context.Background(), client, c); err != nil {
		t.Fatal("optional PKCE metadata rejected:", err)
	}
}
func TestDiscoveryRejectsIncompleteAndInvalidResponses(t *testing.T) {
	c := config.Config{Issuer: "https://id.example.com", ClientID: "client"}
	for _, tc := range []struct {
		status int
		body   string
	}{{302, `{}`}, {500, `{}`}, {200, `{}`}, {200, `null`}, {200, `<html>`}, {200, strings.Repeat(" ", 1<<20+1)}} {
		client := &http.Client{Transport: transportFunc(func(*http.Request) (*http.Response, error) {
			return &http.Response{StatusCode: tc.status, Body: io.NopCloser(strings.NewReader(tc.body)), Header: make(http.Header)}, nil
		})}
		if Check(context.Background(), client, c) == nil {
			t.Fatal("invalid response accepted")
		}
	}
	if Check(context.Background(), nil, config.Config{}) == nil {
		t.Fatal("empty configuration accepted")
	}
}
