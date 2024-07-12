#!/bin/sh

# Wait for Consul to be ready
sleep 5
export CONSUL_HTTP_TOKEN="magrossebite"
# Apply the JWT provider configuration

consul acl auth-method create \
    -name jwt \
    -type jwt \
    -description "JWT auth method" \
    -config '{
        "BoundAudiences": ["rabbitmq"],
        "JWKSURL": "https://node-local-kali-2.tailc2844.ts.net:5000/.well-known/jwks.json",
        "ClaimMappings": {
            "sub": "username"
        },
        "JWTSupportedAlgs": ["RS256"]
    }'

consul acl policy create -name read-policy -rules '
key_prefix "" {
  policy = "read"
}
service_prefix "" {
  policy = "read"
}
node_prefix "" {
  policy = "read"}
agent_prefix "" {
  policy = "read"
}
session_prefix "" {
  policy = "read"
}
'
consul acl role create -name read-role -policy-name read-policy
consul acl binding-rule create \
    -method jwt \
    -bind-type role \
    -bind-name read-role \
    -selector 'value.sub == "Max Tests"'


consul acl auth-method list
consul acl policy read -name read-policy
consul acl role read -name read-role
consul acl binding-rule list
# Apply the service intentions configuration
#consul config write /consul/config/service-intentions.hcl
