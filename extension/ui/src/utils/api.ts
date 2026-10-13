let ddClientInstance: any = null;

export const setApiClientDesktopClient = (client: any) => {
  ddClientInstance = client;
};

// Cached working port to prevent probing on every single request
let activePort: number | null = null;
const CANDIDATE_PORTS = [40040, 8000, 40041];

/**
 * Universal API client for Docker Desktop and Rancher Desktop.
 * 1. Attempts Docker Desktop native VM service socket proxy.
 * 2. Falls back to probing HTTP ports: 40040 (compose default), 8000 (direct uvicorn), 40041 (secondary).
 */
export const apiCall = async (endpoint: string, method = 'GET', body: any = null): Promise<any> => {
  // 1. Docker Desktop internal VM service proxy
  const client = ddClientInstance || (typeof window !== 'undefined' ? (window as any).ddClient : null);
  if (client?.extension?.vm?.service) {
    try {
      if (method === 'GET') {
        return await client.extension.vm.service.get(endpoint);
      } else {
        return await client.extension.vm.service.post(endpoint, body);
      }
    } catch (err) {
      console.warn('Docker Desktop VM service call failed, attempting HTTP port fallback:', err);
    }
  }

  // 2. HTTP Port fallback (Rancher Desktop, browser dev, or standalone daemon)
  const portsToTry = activePort
    ? [activePort, ...CANDIDATE_PORTS.filter(p => p !== activePort)]
    : CANDIDATE_PORTS;

  let lastError: any = null;
  for (const port of portsToTry) {
    try {
      const res = await fetch(`http://localhost:${port}${endpoint}`, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: body ? JSON.stringify(body) : undefined,
      });
      if (res.ok) {
        activePort = port;
        return await res.json();
      }
    } catch (err) {
      lastError = err;
    }
  }

  throw lastError || new Error(`Failed to communicate with Rover-Slim backend on ports ${CANDIDATE_PORTS.join(', ')}`);
};
