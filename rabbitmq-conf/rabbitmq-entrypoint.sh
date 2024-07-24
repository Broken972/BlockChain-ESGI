#!/bin/bash

tailscale ip

export NODENAME=rabbitmq@$(tailscale status --json | jq -r '.Self.DNSName' | cut -d'.' -f1)

echo """
# Enable both internal and OAuth2 backends
auth_backends.1 = internal
auth_backends.2 = oauth2

# OAuth2 settings
auth_oauth2.resource_server_id = rabbitmq
auth_oauth2.jwks_url = https://$(tailscale status --json | jq -r '.Self.DNSName' | sed 's/.$//'):5000/.well-known/jwks.json
auth_oauth2.default_key = ac4ba3eb7ba0ad03353bdf5396ea78999f7c60ca7e1a1b8d4641819894d1f4d8
auth_oauth2.https.peer_verification = verify_none
auth_oauth2.algorithms.1 = RS256
auth_oauth2.additional_scopes_key = roles

# Allow guest user to connect from localhost only
#loopback_users.user = true

cluster_formation.peer_discovery_backend = rabbit_peer_discovery_consul
cluster_formation.consul.host = $(tailscale status --json | jq -r '.Self.DNSName' | sed 's/.$//')
cluster_formation.consul.svc_addr_auto = false
cluster_formation.consul.svc_addr = $(tailscale status --json | jq -r '.Self.DNSName' | sed 's/.$//')
cluster_formation.consul.svc_addr_use_nodename = false

cluster_name = linksys_rabbit
""" > /etc/rabbitmq/rabbitmq.conf

bash /usr/local/bin/docker-entrypoint.sh rabbitmq-server