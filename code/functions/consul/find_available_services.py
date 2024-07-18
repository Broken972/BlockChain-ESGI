import consul
async def get_healthy_services(service_name,host):
    c = consul.Consul(host=host,port=8501,scheme="https")

    index, nodes = c.health.service(service_name, passing=True)
    
    healthy_services = [node for node in nodes if node['Checks'][0]['Status'] == 'passing']
    healthy_nodes = []
    for node in healthy_services:
        healthy_nodes.append(f"{node['Node']['Node']}.tailc2844.ts.net")
    return healthy_nodes