#!/bin/sh
# Wait for Consul to be ready
sleep 5
export CONSUL_HTTP_TOKEN="magrossebite"
consul services register -http-addr=https://node-local-kali-2.tailc2844.ts.net:8501 /consul/services.hcl