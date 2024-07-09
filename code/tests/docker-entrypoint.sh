#!/bin/bash
set -e

if [ -n "$CLUSTER_WITH" ]; then
  echo "Joining cluster with $CLUSTER_WITH"
  rabbitmqctl stop_app
  rabbitmqctl reset
  rabbitmqctl join_cluster rabbit@$CLUSTER_WITH
  rabbitmqctl start_app
else
  echo "No cluster to join, starting normally."
fi

exec docker-entrypoint.sh rabbitmq-server
