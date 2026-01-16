import { ref, watchEffect } from 'vue';
const isDarkMode = ref(false);
export function useTheme() {
  const toggleTheme = () => {
    isDarkMode.value = !isDarkMode.value;
  };

  const setTheme = (value: boolean) => {
    isDarkMode.value = value;
  };

  watchEffect(() => {
    const theme = isDarkMode.value ? 'dark' : 'light';
    document.body.classList.remove('light-mode', 'dark-mode');
    document.body.classList.add(`${theme}-mode`);
  });

  return {
    isDarkMode,
    toggleTheme,
    setTheme
  };
}
