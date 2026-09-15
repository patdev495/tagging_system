import { ref } from 'vue';
import { useSettingsStore } from '../../../core/stores/settings';
import { useSystemStore } from '../../../core/stores/system';
import type { Carton } from '../../../types/api';
import printApi from '../api';

export function useAdminReprint(onSuccess: () => void) {
  const settingsStore = useSettingsStore();
  const system = useSystemStore();
  const reprintingCartonId = ref<number | null>(null);

  const handleReprint = async (carton: Carton) => {
    if (!confirm(`Bạn có chắc muốn in lại tem cho Carton SN ${carton.carton_sn}?`)) return;

    try {
      reprintingCartonId.value = carton.id;
      const reprintResponse = await printApi.reprintCarton(
        carton.id,
        settingsStore.templatePath || '',
        settingsStore.printerName || '',
      );
      const reprint = reprintResponse.data;
      if (!reprint?.id) throw new Error('Không tạo được bản ghi in lại.');

      if (settingsStore.printMode === 'local') {
        const xmlContent = reprint.btxml || (await printApi.download_carton_btxml(
          reprint.id,
          carton.product?.template_path || settingsStore.templatePath || '',
        )).data;
        const result = await printApi.agentPrint(
          settingsStore.agentUrl || 'http://127.0.0.1:8080',
          xmlContent,
          settingsStore.printerName || undefined,
          settingsStore.localTemplateDir || undefined,
        );
        if (!result?.success) throw new Error(result?.message || 'Print Agent không in được tem.');
        if (result.type === 'pdf' && result.data) {
          const link = document.createElement('a');
          link.href = `data:application/pdf;base64,${result.data}`;
          link.download = `Label_${reprint.carton_sn}.pdf`;
          link.click();
        }
      } else {
        const result = await printApi.serverPrint(
          reprint.id,
          settingsStore.printerName || undefined,
          carton.product?.template_path || settingsStore.templatePath || undefined,
        );
        if (!result.data?.success) throw new Error(result.data?.message || 'Máy chủ không in được tem.');
      }

      system.showNotification(`Đã in lại tem: ${carton.carton_sn}`, 'success');
      onSuccess();
    } catch (err: any) {
      const detail = err.response?.data?.detail || err.message || 'Không thể in lại tem.';
      system.showNotification(`In lại tem thất bại: ${detail}`, 'error');
    } finally {
      reprintingCartonId.value = null;
    }
  };

  return { reprintingCartonId, handleReprint };
}
