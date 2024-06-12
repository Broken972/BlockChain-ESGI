#!/bin/bash
random_id=$(cat /proc/sys/kernel/random/uuid)
trap 'kill -TERM $PID' TERM INT
echo "Starting Tailscale daemon"
# -state=mem: will logout and remove ephemeral node from network immediately after ending.
tailscaled --tun=userspace-networking --state=${TAILSCALE_STATE_ARG} ${TAILSCALE_OPT} &
PID=$!
until tailscale up --authkey="${TAILSCALE_AUTH_KEY}" --hostname="${TAILSCALE_HOSTNAME}-$random_id"; do
    sleep 0.1
done
tailscale status
wait ${PID}
wait ${PID}

tskey-auth-kRJfdBuMvA21CNTRL-ikGGuFz8VfLkhHCxvd36gLtDgHXHHsFi