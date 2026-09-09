export default {
  async getScaleStatus(agentUrl: string = 'http://127.0.0.1:8080') {
    const res = await fetch(`${agentUrl}/scale/status`, { signal: AbortSignal.timeout(1500) });
    if (!res.ok) throw new Error('Failed to fetch scale status');
    return res.json();
  },
  async getScaleCurrent(agentUrl: string = 'http://127.0.0.1:8080') {
    const res = await fetch(`${agentUrl}/scale/current`, { signal: AbortSignal.timeout(1500) });
    if (!res.ok) throw new Error('Failed to fetch scale reading');
    return res.json();
  },
  async getScalePorts(agentUrl: string = 'http://127.0.0.1:8080') {
    const res = await fetch(`${agentUrl}/scale/ports`, { signal: AbortSignal.timeout(2000) });
    if (!res.ok) throw new Error('Failed to fetch scale ports');
    return res.json();
  },
  async tareScale(agentUrl: string = 'http://127.0.0.1:8080') {
    const res = await fetch(`${agentUrl}/scale/tare`, { method: 'POST', signal: AbortSignal.timeout(2000) });
    if (!res.ok) throw new Error('Failed to tare scale');
    return res.json();
  },
  async zeroScale(agentUrl: string = 'http://127.0.0.1:8080') {
    const res = await fetch(`${agentUrl}/scale/zero`, { method: 'POST', signal: AbortSignal.timeout(2000) });
    if (!res.ok) throw new Error('Failed to zero scale');
    return res.json();
  },
  async updateScaleConfig(config: { port?: string; baudrate?: number; hotkey?: string }, agentUrl: string = 'http://127.0.0.1:8080') {
    const res = await fetch(`${agentUrl}/scale/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
      signal: AbortSignal.timeout(3000),
    });
    if (!res.ok) throw new Error('Failed to update scale config');
    return res.json();
  },
};
