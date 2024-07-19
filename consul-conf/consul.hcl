acl {
  enabled = true
  default_policy = "allow"
  enable_token_persistence = true
  tokens {
    master = "magrossebite"
  }
}
node_name = "node-local-kali-2"
server = true
data_dir = "/consul/data"
bind_addr = "100.103.228.105"
client_addr = "100.103.228.105"

ports {
  https = 8501
}

tls {
  https {
    ca_file = "/certs/ca.crt",
    tls_min_version = "TLSv1_2",
    verify_incoming = false,
    verify_outgoing = true
    cert_file = "/certs/ca.crt",
    key_file = "/certs/ca.key",
  },
}