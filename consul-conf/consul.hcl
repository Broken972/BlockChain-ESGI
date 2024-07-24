acl {
  enabled = true
  default_policy = "allow"
  enable_token_persistence = true
  tokens {
    master = "magrossebite"
  }
}

data_dir = "/consul/data"

ports {
  https = 8501
  http = 8500
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