import { ref, computed } from 'vue';
import { defineStore } from 'pinia';

export const useCropperStore = defineStore('cropper', () => {
  const current = ref(null);
  const imgs = ref([]);

  return { current, imgs };
});
