import { ref } from 'vue';
import { defineStore } from 'pinia';

export const useRouterStore = defineStore('router', () => {
  const current = ref('');

  return { current };
});
