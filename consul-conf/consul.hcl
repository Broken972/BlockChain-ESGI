acl {
  enabled = true
  default_policy = "allow"
  enable_token_persistence = true
  tokens {
    master = "magrossebite"
  }
}

data_dir = "/consul/data"
bind_addr = "127.0.0.1"
client_addr = "127.0.0.1"
