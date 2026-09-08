package control

import (
	"context"
	"encoding/json"
	"errors"
	pluginv1 "github.com/zerodenet/zboard/backend/pkg/pluginapi/v1"
	"golang.org/x/oauth2"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"io"
	"net/http"
	"strings"
	"zboard.local/plugins/oauth/internal/config"
)

func tokenAuthStyle(method string) oauth2.AuthStyle {
	if method == "post" || method == "none" {
		return oauth2.AuthStyleInParams
	}
	return oauth2.AuthStyleInHeader
}
func (s *Server) exchangeOAuth2(ctx context.Context, c config.Config, r *pluginv1.IdentityExchange) (*pluginv1.VerifiedIdentity, error) {
	oauth := oauth2.Config{ClientID: c.ClientID, ClientSecret: c.ClientSecret, RedirectURL: r.RedirectUri, Scopes: c.Scopes, Endpoint: oauth2.Endpoint{AuthURL: c.AuthorizationEndpoint, TokenURL: c.TokenEndpoint, AuthStyle: tokenAuthStyle(c.TokenAuthMethod)}}
	token, err := oauth.Exchange(ctx, r.Code, oauth2.VerifierOption(r.PkceVerifier))
	if err != nil || token.AccessToken == "" || len(token.AccessToken) > 64<<10 || !strings.EqualFold(token.TokenType, "bearer") {
		return nil, status.Error(codes.Unauthenticated, "OAuth2 code exchange failed")
	}
	var profile map[string]any
	if err := s.userInfo(ctx, c.UserInfoEndpoint, token.AccessToken, &profile); err != nil {
		return nil, status.Error(codes.Unauthenticated, "OAuth2 user profile unavailable")
	}
	subject := profileString(profileField(profile, c.SubjectField))
	if subject == "" || len(subject) > 512 {
		return nil, status.Error(codes.Unauthenticated, "OAuth2 profile has no stable subject")
	}
	email, _ := profileField(profile, c.EmailField).(string)
	verified, _ := profileField(profile, c.EmailVerifiedField).(bool)
	if c.Preset == "github" {
		// GitHub's public profile email is not proof of verification. Only the
		// authenticated email endpoint's primary+verified record may assert it.
		var emails []struct {
			Email    string `json:"email"`
			Primary  bool   `json:"primary"`
			Verified bool   `json:"verified"`
		}
		email = ""
		verified = false
		if err := s.userInfo(ctx, "https://api.github.com/user/emails", token.AccessToken, &emails); err != nil {
			return nil, status.Error(codes.Unauthenticated, "GitHub verified email lookup failed")
		}
		for _, item := range emails {
			if item.Primary && item.Verified {
				email = item.Email
				verified = true
				break
			}
		}
	}
	return &pluginv1.VerifiedIdentity{Issuer: c.Issuer, Subject: subject, Email: email, EmailVerified: verified}, nil
}
func (s *Server) userInfo(ctx context.Context, endpoint, accessToken string, out any) error {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, endpoint, nil)
	if err != nil {
		return err
	}
	req.Header.Set("Authorization", "Bearer "+accessToken)
	req.Header.Set("Accept", "application/json")
	req.Header.Set("User-Agent", "ZBoard-OAuth/"+Version)
	res, err := s.client.Do(req)
	if err != nil {
		return err
	}
	defer res.Body.Close()
	if res.StatusCode != http.StatusOK {
		return errors.New("userinfo requires HTTP 200")
	}
	raw, err := io.ReadAll(io.LimitReader(res.Body, (1<<20)+1))
	if err != nil || len(raw) > 1<<20 {
		return errors.New("userinfo exceeds limit")
	}
	d := json.NewDecoder(strings.NewReader(string(raw)))
	d.UseNumber()
	if d.Decode(out) != nil || d.Decode(new(any)) != io.EOF {
		return errors.New("invalid userinfo JSON")
	}
	return nil
}
func profileField(profile map[string]any, path string) any {
	if path == "" {
		return nil
	}
	var value any = profile
	for _, part := range strings.Split(path, ".") {
		obj, ok := value.(map[string]any)
		if !ok {
			return nil
		}
		value = obj[part]
	}
	return value
}
func profileString(value any) string {
	switch v := value.(type) {
	case string:
		return v
	case json.Number:
		if _, err := v.Int64(); err == nil {
			return string(v)
		}
	}
	return ""
}
