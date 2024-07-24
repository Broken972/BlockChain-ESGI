import consul

def register_service(consul_host, consul_port, consul_scheme, service_name, service_id, service_port, service_check=None, service_tags=None):
    """
    Registers a service in Consul.

    :param consul_host: Host where Consul is running.
    :param consul_port: Port where Consul is running.
    :param consul_scheme: Scheme used by Consul (http or https).
    :param service_name: Name of the service to register.
    :param service_id: Unique ID for the service.
    :param service_port: Port on which the service is running.
    :param service_check: Dictionary defining a health check for the service (optional).
    :param service_tags: List of tags to associate with the service (optional).
    """
    c = consul.Consul(host=consul_host, port=consul_port, scheme=consul_scheme)

    # Define the service registration parameters
    service_definition = {
        "service_id": service_id,
        "name": service_name,
        "port": service_port,
    }

    if service_check:
        service_definition["check"] = service_check

    if service_tags:
        service_definition["tags"] = service_tags

    # Register the service
    c.agent.service.register(**service_definition)
    print(f"Service '{service_name}' registered with Consul.")