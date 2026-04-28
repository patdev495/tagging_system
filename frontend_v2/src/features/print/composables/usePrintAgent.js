import { ref } from 'vue';

export function usePrintAgent() {
  const isAgentConnected = ref(false);
  const agentErrorMessage = ref('');

  const checkAgentHealth = async () => {
    try {
      // 2-second timeout for quick health check
      const controller = new AbortController();
      const id = setTimeout(() => controller.abort(), 2000);
      
      const response = await fetch('http://127.0.0.1:1234/status', { signal: controller.signal });
      clearTimeout(id);
      
      if (response.ok) {
        const data = await response.json();
        isAgentConnected.value = true;
        return data.station_id || '';
      } else {
        isAgentConnected.value = false;
        return '';
      }
    } catch (err) {
      isAgentConnected.value = false;
    }
  };

  const sendPrintJob = async (btxmlContent, cartonSn, folderPath, printerName) => {
    try {
      const response = await fetch('http://127.0.0.1:1234/print', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          type: 'print',
          xml: btxmlContent,
          filename: `print_job_${cartonSn}.xml`,
          path: folderPath || undefined,
          printer_name: printerName || undefined,
          fallback_template_path: (window.localStorage.getItem('settings') ? JSON.parse(window.localStorage.getItem('settings')).templatePath : undefined)
        })
      });
      
      if (!response.ok) {
        const errData = await response.json();
        agentErrorMessage.value = errData.error || 'Agent returned error status';
        return { success: false, error: agentErrorMessage.value };
      }
      
      agentErrorMessage.value = '';
      return { success: true };
    } catch (err) {
      agentErrorMessage.value = err.message || 'Could not connect to Print Agent';
      return { success: false, error: agentErrorMessage.value };
    }
  };

  return {
    isAgentConnected,
    agentErrorMessage,
    checkAgentHealth,
    sendPrintJob
  };
}
