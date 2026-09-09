package control

import (
	"context"
	"crypto/subtle"
	"errors"
	"net/url"
	"time"

	"github.com/coreos/go-oidc/v3/oidc"
	pluginv1 "github.com/zerodenet/zboard/backend/pkg/pluginapi/v1"
	"golang.org/x/oauth2"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	"github.com/zerodenet/plugins/zboard/oauth/internal/config"
	"github.com/zerodenet/plugins/zboard/oauth/internal/provider"
)

func (s *Server) providerSnapshot(ctx context.Context, id string) (config.Config, provider.Metadata, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	var c config.Config
	for _, entry := range s.config.Entries() {
		if entry.ID == id && !entry.Disabled {
			c = entry
			break
		}
	}
	if !c.Configured() {
		return config.Config{}, provider.Metadata{}, errors.New("provider is not configured")
	}
	if s.discovery == nil {
		s.discovery = map[string]provider.Metadata{}
		s.discoveredAt = map[string]time.Time{}
	}
	if _, ok := s.discovery[id]; !ok || time.Since(s.discoveredAt[id]) > 5*time.Minute {
		metadata, err := provider.Discover(ctx, s.client, c)
		if err != nil {
			return config.Config{}, provider.Metadata{}, err
		}
		s.discovery[id] = metadata
		s.discoveredAt[id] = time.Now()
	}
	return c, s.discovery[id], nil
}
func (s *Server) GetIdentityProvider(ctx context.Context, r *pluginv1.IdentityProviderRequest) (*pluginv1.IdentityProvider, error) {
	c, m, err := s.providerSnapshot(ctx, r.GetProviderId())
	if err != nil {
		return nil, status.Error(codes.FailedPrecondition, "OIDC provider is unavailable; check saved configuration")
	}
	return &pluginv1.IdentityProvider{Issuer: c.Issuer, AuthorizationEndpoint: m.AuthorizationEndpoint, ClientId: c.ClientID, Scopes: append([]string{}, c.Scopes...), ProviderId: c.ID, Protocol: c.Protocol}, nil
}
func validCallback(raw string) bool {
	u, err := url.Parse(raw)
	if err != nil || u.Hostname() == "" || u.User != nil || u.Fragment != "" || u.RawQuery != "" || u.Path != "/api/v1/auth/oidc/callback" {
		return false
	}
	return u.Scheme == "https" || (u.Scheme == "http" && (u.Hostname() == "127.0.0.1" || u.Hostname() == "localhost" || u.Hostname() == "::1"))
}
func (s *Server) ExchangeIdentity(ctx context.Context, r *pluginv1.IdentityExchange) (*pluginv1.VerifiedIdentity, error) {
	if r == nil || len(r.Code) == 0 || len(r.Code) > 8192 || len(r.Nonce) != 43 || len(r.PkceVerifier) != 43 || !validCallback(r.RedirectUri) {
		return nil, status.Error(codes.InvalidArgument, "invalid identity exchange request")
	}
	c, m, err := s.providerSnapshot(ctx, r.GetProviderId())
	if err != nil || r.Issuer != c.Issuer {
		return nil, status.Error(codes.FailedPrecondition, "OIDC configuration changed or unavailable")
	}
	ctx = oidc.ClientContext(ctx, s.client)
	if c.Protocol == "oauth2" {
		return s.exchangeOAuth2(ctx, c, r)
	}
	oidcProvider := (&oidc.ProviderConfig{IssuerURL: c.Issuer, AuthURL: m.AuthorizationEndpoint, TokenURL: m.TokenEndpoint, JWKSURL: m.JWKSURI, Algorithms: []string{"RS256", "ES256"}}).NewProvider(ctx)
	oauth := oauth2.Config{ClientID: c.ClientID, ClientSecret: c.ClientSecret, Endpoint: oidcProvider.Endpoint(), RedirectURL: r.RedirectUri, Scopes: c.Scopes}
	oauth.Endpoint.AuthStyle = tokenAuthStyle(c.TokenAuthMethod)
	token, err := oauth.Exchange(ctx, r.Code, oauth2.VerifierOption(r.PkceVerifier))
	if err != nil {
		return nil, status.Error(codes.Unauthenticated, "authorization code exchange failed")
	}
	raw, ok := token.Extra("id_token").(string)
	if !ok || len(raw) > 64<<10 {
		return nil, status.Error(codes.Unauthenticated, "provider did not return a valid ID token")
	}
	verified, err := oidcProvider.Verifier(&oidc.Config{ClientID: c.ClientID, SupportedSigningAlgs: []string{"RS256", "ES256"}}).Verify(ctx, raw)
	if err != nil || (verified.Issuer != r.Issuer && !(c.Issuer == "https://accounts.google.com" && verified.Issuer == "accounts.google.com")) || verified.Subject == "" || len(verified.Subject) > 512 || subtle.ConstantTimeCompare([]byte(verified.Nonce), []byte(r.Nonce)) != 1 {
		return nil, status.Error(codes.Unauthenticated, "ID token verification failed")
	}
	var claims struct {
		AuthorizedParty string `json:"azp"`
		Email           string `json:"email"`
		EmailVerified   bool   `json:"email_verified"`
	}
	if verified.Claims(&claims) != nil || (len(verified.Audience) > 1 && claims.AuthorizedParty != c.ClientID) || (claims.AuthorizedParty != "" && claims.AuthorizedParty != c.ClientID) {
		return nil, status.Error(codes.Unauthenticated, "ID token authorized party mismatch")
	}
	if verified.AccessTokenHash != "" && verified.VerifyAccessToken(token.AccessToken) != nil {
		return nil, status.Error(codes.Unauthenticated, "access token binding failed")
	}
	// No token, user ID, role, SQL or node operation crosses back to the host.
	return &pluginv1.VerifiedIdentity{Issuer: c.Issuer, Subject: verified.Subject, Email: claims.Email, EmailVerified: claims.EmailVerified}, nil
}
