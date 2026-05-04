import api from '../../core/api';

export default {
  updateCartonStatus(cartonId, status) {
    return api.patch(`/print/carton/${cartonId}/status`, { status });
  },
  searchCarton(sn) {
    return api.get('/cartons/search', { params: { carton_sn: sn } });
  },
  reprintCarton(cartonId, templatePath, printerName) {
    return api.post(`/print/carton/${cartonId}/reprint`, null, { 
      params: { template_path: templatePath, printer_name: printerName }
    });
  },
  /** Lấy cấu hình in từ server */
  getPrintConfig() {
    return api.get('/print/config');
  },
  /** Gửi lệnh in qua Backend → Agent Server */
  serverPrint(cartonId, printerName, fallbackTemplatePath) {
    return api.post(`/print/carton/${cartonId}/server-print`, null, {
      params: { 
        printer_name: printerName || undefined,
        fallback_template_path: fallbackTemplatePath || undefined,
      }
    });
  },
  /** Gửi lệnh in qua Local Agent (Chạy tại máy trạm) */
  async agentPrint(agentUrl, xmlContent, printerName, localTemplateDir) {
    try {
      const response = await fetch(`${agentUrl}/print`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          xml_content: xmlContent,
          printer_name: printerName || null,
          local_template_dir: localTemplateDir || null
        })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Agent print failed');
      return data;
    } catch (err) {
      if (err.message.includes('Failed to fetch')) {
        throw new Error('Không thể kết nối tới Print Agent. Bạn đã bật file agent.py chưa?');
      }
      throw err;
    }
  },
  /** Lấy danh sách máy in khả dụng từ Server/Agent */
  getAvailablePrinters() {
    return api.get('/print/printers');
  },
  /** Lấy IP của Client từ server */
  whoami() {
    return api.get('/print/whoami');
  },
  /** Lấy file .xml của thùng để in qua Agent */
  download_carton_btxml(cartonId, templatePath) {
    return api.get(`/print/carton/${cartonId}/btxml`, {
      params: { template_path: templatePath }
    });
  }
};
