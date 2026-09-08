// Package provider performs read-only provider metadata diagnostics. OAuth code
// exchange and ZBoard authentication are deliberately not configuration effects.
package provider

import (
	"context"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"slices"
	"strings"

	"zboard.local/plugins/oauth/internal/config"
)

type Metadata struct {
	Issuer                string   `json:"issuer"`
	AuthorizationEndpoint string   `json:"authorization_endpoint"`
	TokenEndpoint         string   `json:"token_endpoint"`
	JWKSURI               string   `json:"jwks_uri"`
	ResponseTypes         []string `json:"response_types_supported"`
	SubjectTypes          []string `json:"subject_types_supported"`
	SigningAlgorithms     []string `json:"id_token_signing_alg_values_supported"`
	PKCEMethods           []string `json:"code_challenge_methods_supported"`
	Scopes                []string `json:"scopes_supported"`
}

func Discover(ctx context.Context, client *http.Client, c config.Config) (Metadata, error) {
	if !c.Configured() {
		return Metadata{}, errors.New("save an issuer and client_id before testing")
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, strings.TrimSuffix(c.Issuer, "/")+"/.well-known/openid-configuration", nil)
	if err != nil {
		return Metadata{}, errors.New("invalid discovery URL")
	}
	req.Header.Set("Accept", "application/json")
	// Client ID and client secret are never sent during metadata diagnostics.
	res, err := client.Do(req)
	if err != nil {
		return Metadata{}, errors.New("OIDC discovery connection failed")
	}
	defer res.Body.Close()
	if res.StatusCode != http.StatusOK {
		return Metadata{}, errors.New("OIDC discovery must return HTTP 200 without redirects")
	}
	raw, err := io.ReadAll(io.LimitReader(res.Body, (1<<20)+1))
	if err != nil || len(raw) > 1<<20 {
		return Metadata{}, errors.New("OIDC discovery response exceeds limit or could not be read")
	}
	var metadata Metadata
	if json.Unmarshal(raw, &metadata) != nil {
		return Metadata{}, errors.New("invalid OIDC discovery document")
	}
	if metadata.Issuer != c.Issuer {
		return Metadata{}, errors.New("OIDC discovery issuer does not exactly match configuration")
	}
	for _, endpoint := range []string{metadata.AuthorizationEndpoint, metadata.TokenEndpoint, metadata.JWKSURI} {
		if config.ValidateURL(endpoint) != nil {
			return Metadata{}, errors.New("OIDC endpoints must be public HTTPS URLs without query or fragment")
		}
	}
	if !slices.Contains(metadata.ResponseTypes, "code") {
		return Metadata{}, errors.New("provider does not advertise authorization code flow")
	}
	if !slices.Contains(metadata.SubjectTypes, "public") && !slices.Contains(metadata.SubjectTypes, "pairwise") {
		return Metadata{}, errors.New("provider has no supported subject type")
	}
	if !slices.Contains(metadata.SigningAlgorithms, "RS256") && !slices.Contains(metadata.SigningAlgorithms, "ES256") {
		return Metadata{}, errors.New("provider has no supported asymmetric ID token signing algorithm")
	}
	// OIDC does not require PKCE metadata. When advertised, reject a provider
	// explicitly advertising no S256 support; absence is not proof of support.
	if len(metadata.PKCEMethods) > 0 && !slices.Contains(metadata.PKCEMethods, "S256") {
		return Metadata{}, errors.New("provider does not advertise S256 PKCE")
	}
	for _, scope := range c.Scopes {
		if len(metadata.Scopes) > 0 && !slices.Contains(metadata.Scopes, scope) {
			return Metadata{}, errors.New("provider does not advertise a configured scope")
		}
	}
	return metadata, nil
}

func Check(ctx context.Context, client *http.Client, c config.Config) error {
	_, err := Discover(ctx, client, c)
	return err
}
