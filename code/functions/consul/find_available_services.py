import consul

async def get_healthy_services(service_name, host, tag=None):
    c = consul.Consul(host=host, port=8501, scheme="https")
    index, nodes = c.health.service(service_name, passing=True)
    healthy_services = [node for node in nodes if node['Checks'][0]['Status'] == 'passing']
    if tag:
        healthy_services = [node for node in healthy_services if tag in node['Service']['Tags']]
    healthy_nodes = [f"{node['Node']['Node']}.tailc2844.ts.net" for node in healthy_services]
    return healthy_nodes
