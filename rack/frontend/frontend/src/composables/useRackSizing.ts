import { ref, onMounted, onUnmounted, computed } from 'vue';

export function useRackSizing() {
  const windowWidth = ref(window.innerWidth);

  const updateWidth = () => {
    windowWidth.value = window.innerWidth;
  };

  onMounted(() => window.addEventListener('resize', updateWidth));
  onUnmounted(() => window.removeEventListener('resize', updateWidth));

  // Replicating the logic: If screen is huge (>1920), use 30px/unit. Else 20px/unit.
  const unitPixelHeight = computed(() => {
    if (windowWidth.value >= 1921) {
      return 30; 
    } else {
      return 20;
    }
  });

  return { unitPixelHeight };
}