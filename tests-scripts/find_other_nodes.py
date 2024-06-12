import asyncio
import json
from tailscale import Tailscale
import requests
import os

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
                    print(f"[+] Found node : {values.name}")
                    req = requests.head(f"http://{values.name}:5000/health",timeout=3)
                    status_code = req.status_code
                    if status_code == 200:
                        functionning_nodes.append(values.name)
            except Exception as error:
                pass
    return functionning_nodes

async def find_all_nodes():
    async with Tailscale(
        tailnet=os.environ.get('TS_EMAIL'),
        api_key=os.environ.get('TS_API_KEY')
    ) as tailscale:
        all_nodes=[]
        devices = await tailscale.devices()
        for key,values in devices.items():
            try:
                if "noeud" in values.name:
                    print(f"[+] Found node : {values.name}")
                    all_nodes.append(values.name)
            except Exception as error:
                pass
    return all_nodes

if __name__ == "__main__":
    print(asyncio.run(find_other_nodes()))