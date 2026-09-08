// Package config owns plugin settings only. It never reads host user state.
package config

import (
	"bytes"
	"encoding/json"
	"errors"
	"io"
	"net/netip"
	"net/url"
	"slices"
	"strings"
	"unicode"
)

const MaxBytes = 64 << 10

type Config struct {
	Issuer       string   `json:"issuer,omitempty"`
	ClientID     string   `json:"client_id,omitempty"`
	ClientSecret string   `json:"client_secret,omitempty"`
	Scopes       []string `json:"scopes,omitempty"`
}

func (c Config) Configured() bool { return c.Issuer != "" && c.ClientID != "" }

func Parse(raw []byte) (Config, error) {
	var c Config
	trimmed := bytes.TrimSpace(raw)
	if len(trimmed) == 0 || len(raw) > MaxBytes || trimmed[0] != '{' {
		return c, errors.New("configuration must be a JSON object of at most 64 KiB")
	}
	d := json.NewDecoder(bytes.NewReader(raw))
	d.DisallowUnknownFields()
	if err := d.Decode(&c); err != nil {
		return Config{}, errors.New("unsupported configuration fields or invalid JSON")
	}
	if err := d.Decode(new(any)); err != io.EOF {
		return Config{}, errors.New("trailing JSON is not allowed")
	}
	c.Issuer = strings.TrimSpace(c.Issuer)
	c.ClientID = strings.TrimSpace(c.ClientID)
	// The empty initial state must be applicable before the first host config save.
	if c.Issuer == "" && c.ClientID == "" && c.ClientSecret == "" && len(c.Scopes) == 0 {
		return Config{}, nil
	}
	if err := ValidateURL(c.Issuer); err != nil {
		return Config{}, errors.New("issuer must be a public HTTPS URL without credentials, query or fragment")
	}
	if c.ClientID == "" || len(c.ClientID) > 512 || strings.ContainsFunc(c.ClientID, unicode.IsControl) {
		return Config{}, errors.New("client_id is required and must be at most 512 bytes without control characters")
	}
	if len(c.ClientSecret) > 8192 || strings.ContainsFunc(c.ClientSecret, unicode.IsControl) {
		return Config{}, errors.New("client_secret must be at most 8192 bytes without control characters")
	}
	if len(c.Scopes) == 0 {
		c.Scopes = []string{"openid", "profile", "email"}
	}
	if len(c.Scopes) > 16 {
		return Config{}, errors.New("at most 16 scopes are allowed")
	}
	scopes := make([]string, 0, len(c.Scopes))
	for _, scope := range c.Scopes {
		if scope == "" || len(scope) > 128 {
			return Config{}, errors.New("invalid scope")
		}
		for _, r := range scope {
			if r < 0x21 || r > 0x7e || r == '"' || r == '\\' {
				return Config{}, errors.New("invalid scope")
			}
		}
		if !slices.Contains(scopes, scope) {
			scopes = append(scopes, scope)
		}
	}
	if !slices.Contains(scopes, "openid") {
		return Config{}, errors.New("openid scope is required for an OIDC provider")
	}
	c.Scopes = scopes
	return c, nil
}

func ValidateURL(raw string) error {
	u, err := url.Parse(raw)
	if err != nil || len(raw) > 2048 || u.Scheme != "https" || u.Hostname() == "" || u.User != nil || u.RawQuery != "" || u.ForceQuery || u.Fragment != "" || strings.Contains(raw, "#") || u.Opaque != "" {
		return errors.New("invalid public HTTPS URL")
	}
	if u.Port() != "" && u.Port() != "443" {
		return errors.New("only HTTPS port 443 is supported")
	}
	host := strings.ToLower(strings.TrimSuffix(u.Hostname(), "."))
	ip, literalIP := netip.ParseAddr(host)
	if literalIP == nil {
		if !PublicIP(ip) {
			return errors.New("private or reserved address is not allowed")
		}
		return nil
	}
	if !strings.Contains(host, ".") || strings.HasSuffix(host, ".localhost") || strings.HasSuffix(host, ".local") || strings.HasSuffix(host, ".internal") {
		return errors.New("local issuer is not supported")
	}
	return nil
}

var reserved = []netip.Prefix{
	netip.MustParsePrefix("0.0.0.0/8"), netip.MustParsePrefix("100.64.0.0/10"),
	netip.MustParsePrefix("192.0.0.0/24"), netip.MustParsePrefix("192.0.2.0/24"),
	netip.MustParsePrefix("192.88.99.0/24"), netip.MustParsePrefix("198.18.0.0/15"),
	netip.MustParsePrefix("198.51.100.0/24"), netip.MustParsePrefix("203.0.113.0/24"),
	netip.MustParsePrefix("240.0.0.0/4"), netip.MustParsePrefix("2001::/23"),
	netip.MustParsePrefix("2001:db8::/32"), netip.MustParsePrefix("2002::/16"),
}

func PublicIP(ip netip.Addr) bool {
	ip = ip.Unmap()
	if !ip.IsValid() || !ip.IsGlobalUnicast() || ip.IsPrivate() || ip.IsLoopback() || ip.IsLinkLocalUnicast() {
		return false
	}
	// IPv6 global unicast only; exclude NAT64 and other translation ranges.
	if ip.Is6() && !netip.MustParsePrefix("2000::/3").Contains(ip) {
		return false
	}
	for _, prefix := range reserved {
		if prefix.Contains(ip) {
			return false
		}
	}
	return true
}
