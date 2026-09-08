package provider

import (
	"bytes"
	"context"
	"errors"
	"io"
	"net"
	"net/http"
	"net/netip"
	"time"

	"zboard.local/plugins/oauth/internal/config"
)

type resolver interface {
	LookupNetIP(context.Context, string, string) ([]netip.Addr, error)
}
type dialFunc func(context.Context, string, string) (net.Conn, error)

// Resolve and pin the connection to a checked IP. A second DNS lookup must never
// occur between validation and dialing. Mixed private/public answers fail closed.
func publicDial(r resolver, dial dialFunc) dialFunc {
	return func(ctx context.Context, network, address string) (net.Conn, error) {
		host, port, err := net.SplitHostPort(address)
		if err != nil || port != "443" {
			return nil, errors.New("unsupported discovery destination")
		}
		ips, err := r.LookupNetIP(ctx, "ip", host)
		if err != nil || len(ips) == 0 {
			return nil, errors.New("provider DNS resolution failed")
		}
		for _, ip := range ips {
			if !config.PublicIP(ip) {
				return nil, errors.New("provider resolves to a private or reserved address")
			}
		}
		for _, ip := range ips {
			conn, err := dial(ctx, network, net.JoinHostPort(ip.String(), port))
			if err == nil {
				return conn, nil
			}
		}
		return nil, errors.New("provider connection failed")
	}
}

func NewClient() *http.Client {
	dialer := &net.Dialer{Timeout: 3 * time.Second}
	return &http.Client{
		Timeout:       8 * time.Second,
		CheckRedirect: func(*http.Request, []*http.Request) error { return http.ErrUseLastResponse },
		Transport: boundedTransport{base: &http.Transport{
			Proxy:                  nil,
			DialContext:            publicDial(net.DefaultResolver, dialer.DialContext),
			TLSHandshakeTimeout:    3 * time.Second,
			ResponseHeaderTimeout:  5 * time.Second,
			MaxResponseHeaderBytes: 32 << 10,
			DisableKeepAlives:      true,
		}},
	}
}

// Bound token and JWKS replies as well as discovery; credentials remain in memory.
type boundedTransport struct{ base http.RoundTripper }

func (t boundedTransport) RoundTrip(r *http.Request) (*http.Response, error) {
	if config.ValidateURL(r.URL.String()) != nil {
		return nil, errors.New("unsupported provider endpoint")
	}
	response, err := t.base.RoundTrip(r)
	if err != nil {
		return nil, err
	}
	defer response.Body.Close()
	raw, err := io.ReadAll(io.LimitReader(response.Body, (1<<20)+1))
	if err != nil || len(raw) > 1<<20 {
		return nil, errors.New("provider response exceeds limit or cannot be read")
	}
	response.Body = io.NopCloser(bytes.NewReader(raw))
	return response, nil
}
