fetch('https://api.tailscale.com/api/v2/tailnet/pyrogelofthedead@gmail.com/devices', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer tskey-api-kssAFP3CNTRL-4ALEgqm3xcZmMe6iQasYmZCxa6fwhTzAb'
  }
})
.then(response => response.json())
.then(data => {
  if (Array.isArray(data.devices)) {
    const hostnames = data.devices.map(device => device.name);
    const filteredHostnames = hostnames.filter(hostname => hostname.includes("node")); // Filter hostnames to include only those with "node"
    const healthCheckPromises = filteredHostnames.map(hostname => {
      return fetch(`http://${hostname}:5000/health`)
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(() => hostname) // Return hostname if health check is successful
        .catch(() => null); // Ignore errors and return null
    });

    // Wait for all health check promises to resolve
    Promise.all(healthCheckPromises).then(results => {
      // Filter out nulls (failed health checks) and print successful hostnames
      const successfulHosts = results.filter(hostname => hostname !== null);
      if (successfulHosts.length !== 0) {
        console.log('Noeuds opérationnels:', successfulHosts);
      }
      else {
        console.error('Aucun noeud fonctionnel détecté');
      }
    });
  } else {
    console.error('Aucun noeud fonctionnel détecté');
  }
})
.catch(error => console.error('Error:', error));
