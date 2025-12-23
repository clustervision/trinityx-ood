import { ref, watch } from 'vue';
import axios from 'axios';
import type { Device } from '@/types/rack';

// Define the shape of the data from Prometheus
export interface NodeMetric {
  hostname: string;
  load: number;
  temperature: number;
  power: number;
  gpu_temp?: number;
}

export function useRackMetrics() {
  const prome_url = 'https://yixin3-dev-ctrl001:9090';
  const metric1 = ref<string | null>('No Scale');
  const metric2 = ref<string | null>('No Scale');
  const rawMetricData = ref<NodeMetric[]>([]); // Typed to avoid the 'never' error

  const fetchMetricData = async () => {
    // Only fetch if a metric is actually selected
    if (metric1.value === 'No Scale' && metric2.value === 'No Scale') {
      rawMetricData.value = [];
      return;
    }
    try {
      const response = await axios.get(`${prome_url}/get_node`);
      rawMetricData.value = response.data; 
    } catch (e) {
      console.error("Fetch metrics error:", e);
    }
  };

  const getMetricForDevice = (device: Device | null, type: string | null) => {
    if (!device || !type || type === 'No Scale' || !rawMetricData.value.length) return undefined;
    
    const found = rawMetricData.value.find((item) => item.hostname === device.name);
    if (!found) return undefined;

    // Logic to return the correct number based on the dropdown selection
    if (type === 'System Load') return found.load;
    if (type === 'Temperature') return found.temperature; 
    if (type === 'Power Consumption') return found.power;
    if (type === 'GPU Temperature') return found.gpu_temp;
    
    return undefined;
  };

  // Automatically fetch new data when the user changes the dropdowns
  watch([metric1, metric2], fetchMetricData);

  return { 
    metric1, 
    metric2, 
    getMetricForDevice, 
    fetchMetricData 
  };
}