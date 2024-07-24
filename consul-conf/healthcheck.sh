#!/bin/sh

ip=$(tailscale ip | head -1)
curl -k -f https://$ip:8501/v1/status/leader
