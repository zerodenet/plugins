package provider

import (
	"context"
	"errors"
	"net"
	"net/http"
	"net/netip"
	"testing"
)

type fakeResolver []netip.Addr

func (r fakeResolver) LookupNetIP(context.Context, string, string) ([]netip.Addr, error) {
	return r, nil
}
func TestDNSRebindingAndMixedAnswersAreBlockedBeforeDial(t *testing.T) {
	for _, answers := range []fakeResolver{nil, {netip.MustParseAddr("127.0.0.1")}, {netip.MustParseAddr("8.8.8.8"), netip.MustParseAddr("10.0.0.1")}, {netip.MustParseAddr("::ffff:169.254.169.254")}} {
		calls := 0
		dial := publicDial(answers, func(context.Context, string, string) (net.Conn, error) { calls++; return nil, errors.New("unused") })
		if _, err := dial(context.Background(), "tcp", "id.example.com:443"); err == nil || calls != 0 {
			t.Fatal("unsafe DNS result reached dial")
		}
	}
}
func TestDialPinsValidatedAddress(t *testing.T) {
	calls := 0
	dial := publicDial(fakeResolver{netip.MustParseAddr("8.8.8.8")}, func(_ context.Context, network, address string) (net.Conn, error) {
		calls++
		if network != "tcp" || address != "8.8.8.8:443" {
			t.Fatal("dial resolved hostname again")
		}
		return nil, errors.New("simulated failure")
	})
	_, _ = dial(context.Background(), "tcp", "id.example.com:443")
	if calls != 1 {
		t.Fatal("did not attempt checked address")
	}
	_, _ = dial(context.Background(), "tcp", "id.example.com:80")
	if calls != 1 {
		t.Fatal("unsafe port dialed")
	}
}
func TestHTTPClientHasNoProxyOrRedirectFallback(t *testing.T) {
	c := NewClient()
	tr := c.Transport.(boundedTransport).base.(*http.Transport)
	if tr.Proxy != nil || tr.DialContext == nil || c.Timeout == 0 || tr.ResponseHeaderTimeout == 0 {
		t.Fatal("network restrictions missing")
	}
	if c.CheckRedirect(nil, nil) != http.ErrUseLastResponse {
		t.Fatal("redirect enabled")
	}
}
