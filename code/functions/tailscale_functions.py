import asyncio
import json
from tailscale import Tailscale
import requests
import os
import psutil,socket
async def find_other_nodes():
    async with Tailscale(
        tailnet=os.environ.get('TS_EMAIL'),
        api_key=os.environ.get('TS_API_KEY')
    ) as tailscale:
        functionning_nodes=[]
        devices = await tailscale.devices()
        for key,values in devices.items():
            try:
                if "noeud" in values.name:
                    req = requests.head(f"http://{values.name}:5000/health",timeout=3)
                    status_code = req.status_code
                    if status_code == 200:
                        functionning_nodes.append(values.name)
            except Exception as error:
                pass
    return functionning_nodes

def get_tailscale_ip_address():
    adapter_name = "tailscale0"
    addrs = psutil.net_if_addrs()
    if adapter_name in addrs:
        for addr in addrs[adapter_name]:
            if addr.family == socket.AF_INET:
                return addr.address
    return None

def return_current_tailscale_domains():
    try:
        api_key = os.getenv("TS_API_KEY")
        tailscale_name = os.getenv("TS_EMAIL")
        url = f'https://api.tailscale.com/api/v2/tailnet/{tailscale_name}/devices'
        response = requests.get(url, auth=(api_key, ''))

        if response.status_code == 200:
            devices = response.json()
            my_ip = get_tailscale_ip_address()
            for device in devices['devices']:
                if device['addresses'][0] == my_ip:
                    our_domain = device['name']
                    dot_position = our_domain.find(".")
                    our_short_domain = our_domain[:dot_position]
                    return [our_domain,our_short_domain]
        else:
            print(f"Failed to retrieve devices. Status code: {response.status_code}, Error: {response.text}")
            return False
    except Exception as e:
        print("error while obtaining current_tailscale domain : " + e)
        return False