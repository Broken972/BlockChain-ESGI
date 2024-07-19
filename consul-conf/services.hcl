service {
  name = "blockchain-server"
  tags = ["http"]
  port = 5000
  check {
    id       = "blockchain-check"
    name     = "ETAT DU NOEUD"
    http     = "https://node-local-kali-2.tailc2844.ts.net:5000/health"
    interval = "10s"
    timeout  = "1s"
  }
}