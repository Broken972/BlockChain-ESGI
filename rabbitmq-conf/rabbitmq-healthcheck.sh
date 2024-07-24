#!/bin/bash

rabbitmq-diagnostics status  --node rabbitmq@$(tailscale status --json | jq -r '.Self.DNSName' | cut -d'.' -f1)