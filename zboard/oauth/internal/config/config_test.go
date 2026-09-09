package config

import (
	"encoding/json"
	"net/netip"
	"strings"
	"testing"
)

func TestConfigurationLifecycle(t *testing.T) {
	c, err := Parse([]byte(`{}`))
	if err != nil || c.Configured() {
		t.Fatalf("initial config: %+v %v", c, err)
	}
	c, err = Parse([]byte(`{"issuer":" https://login.example.com/realm ","client_id":" client ","client_secret":"secret","scopes":["openid","email","email"]}`))
	if err != nil || c.Issuer != "https://login.example.com/realm" || c.ClientID != "client" || c.ClientSecret != "secret" || len(c.Scopes) != 2 {
		t.Fatalf("normalization failed: %v", err)
	}
	raw, _ := json.Marshal(c)
	if _, err := Parse(raw); err != nil {
		t.Fatal(err)
	}
	c, err = Parse([]byte(`{"issuer":"https://login.example.com/","client_id":"client"}`))
	if err != nil || len(c.Scopes) != 3 || c.Issuer != "https://login.example.com/" {
		t.Fatal("default scopes or issuer identity changed")
	}
}
func TestRejectMalformedConfiguration(t *testing.T) {
	cases := []string{"", "  ", "null", "[]", "{}{}", `{"unexpected":true}`, `{"issuer":"https://login.example.com"}`, `{"client_id":"test"}`, `{"issuer":"http://login.example.com","client_id":"test"}`, `{"issuer":"https://login.example.com","client_id":"test","scopes":["email"]}`, `{"issuer":"https://login.example.com","client_id":"test","scopes":["openid","bad scope"]}`, `{"issuer":"https://login.example.com","client_id":"test","client_secret":"secret\n"}`, strings.Repeat(" ", MaxBytes+1)}
	for i, raw := range cases {
		if _, err := Parse([]byte(raw)); err == nil {
			t.Errorf("case %d accepted", i)
		}
	}
}
func TestRejectNonPublicURLs(t *testing.T) {
	for _, raw := range []string{"https://localhost", "https://a.local", "https://a.internal", "https://127.0.0.1", "https://10.0.0.1", "https://[::1]", "https://[::ffff:127.0.0.1]", "https://169.254.169.254", "https://100.100.100.200", "https://192.0.2.1", "https://user:secret@id.example.com", "https://id.example.com?a=b", "https://id.example.com#", "https://id.example.com:8443"} {
		if ValidateURL(raw) == nil {
			t.Errorf("accepted %q", raw)
		}
	}
	for _, raw := range []string{"https://accounts.google.com", "https://login.example.com/path/", "https://[2606:4700:4700::1111]"} {
		if err := ValidateURL(raw); err != nil {
			t.Errorf("rejected %q: %v", raw, err)
		}
	}
}
func TestPublicIPPolicy(t *testing.T) {
	for _, ip := range []string{"127.0.0.1", "10.1.2.3", "172.16.1.1", "192.168.1.1", "0.0.0.0", "100.64.0.1", "198.18.0.1", "198.51.100.1", "224.0.0.1", "240.0.0.1", "::1", "::ffff:10.0.0.1", "fc00::1", "fe80::1", "64:ff9b::a00:1", "2002:a00:1::", "2001:db8::1"} {
		if PublicIP(netip.MustParseAddr(ip)) {
			t.Errorf("accepted %s", ip)
		}
	}
	for _, ip := range []string{"8.8.8.8", "1.1.1.1", "2606:4700:4700::1111"} {
		if !PublicIP(netip.MustParseAddr(ip)) {
			t.Errorf("rejected %s", ip)
		}
	}
}
func FuzzParse(f *testing.F) {
	for _, raw := range []string{"{}", " ", `{"issuer":"https://id.example.com","client_id":"client"}`} {
		f.Add([]byte(raw))
	}
	f.Fuzz(func(t *testing.T, raw []byte) { _, _ = Parse(raw) })
}
