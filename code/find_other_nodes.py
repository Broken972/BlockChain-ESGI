import asyncio
import json
from tailscale import Tailscale
import requests

async def main():
    """Show example on using the Tailscale API client."""
    async with Tailscale(
        tailnet="pyrogelofthedead@gmail.com",
        api_key="tskey-api-kssAFP3CNTRL-4ALEgqm3xcZmMe6iQasYmZCxa6fwhTzAb",
    ) as tailscale:
        functionning_nodes=[]
        devices = await tailscale.devices()
        for key,values in devices.items():
            try:
                print(values.name)
                req = requests.head(f"http://{values.name}:5000/health",timeout=3)
                status_code = req.status_code
                if status_code == 200:
                    #print(f"[*] Node {values.name} is reachable !")
                    functionning_nodes.append(values.name)
            except Exception as error:
                pass
                #print(f"[!] Node {values.name} is unreachable")
                #print(error)
        if len(functionning_nodes) == 0:
            print("[!] Aucun node est disponible")
        else:
            print("[*] Ce\ces noeuds sont opérationnels :")
            for node in functionning_nodes:
                print(node)

if __name__ == "__main__":
    asyncio.run(main())