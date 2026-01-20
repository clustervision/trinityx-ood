import { ref } from 'vue';
const isDarkMode = ref(false);
export function useTheme() {
  const toggleTheme = () => {
    isDarkMode.value = !isDarkMode.value;
  };

  const setTheme = (value: boolean) => {
    isDarkMode.value = value;
  };


  return {
    isDarkMode,
    toggleTheme,
    setTheme
  };
}
