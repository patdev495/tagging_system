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
  /** Lấy danh sách máy in khả dụng từ Agent */
  getAvailablePrinters() {
    return api.get('/print/printers');
  }
};
