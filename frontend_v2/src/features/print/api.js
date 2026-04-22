import api from '../../core/api';

export default {
  updateCartonStatus(cartonId, status) {
    return api.patch(`/cartons/${cartonId}/status`, { status });
  },
  searchCarton(sn) {
    return api.get('/cartons/search', { params: { carton_sn: sn } });
  },
  reprintCarton(cartonId, templatePath, printerName) {
    return api.post(`/cartons/${cartonId}/reprint`, null, { 
      params: { template_path: templatePath, printer_name: printerName }
    });
  }
};
