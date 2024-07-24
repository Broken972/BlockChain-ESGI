#!/bin/sh

mkdir /certs

tailscale status --json | jq -r '.Self.DNSName' | cut -d'.' -f1 > /tmp/node-id

tailscale cert $(tailscale status --json | jq -r '.Self.DNSName' | sed 's/.$//')

mv *.crt /certs/ca.crt
mv *.key /certs/ca.key

consul agent -server -ui -config-dir=/consul/config -join desktop-obd817h-1 -join node-local-kali-2 -bootstrap-expect 3 -node $(cat /tmp/node-id) -bind '{{ GetInterfaceIP "tailscale0" }}' -client='{{ GetInterfaceIP "tailscale0" }}'