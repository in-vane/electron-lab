<script setup>
import { ref } from 'vue';
import {
  NSelect,
  NIcon,
  NButton,
  NUpload,
  NUploadDragger,
  NText,
  NP,
  NImage,
  NSpin,
  NSpace,
} from 'naive-ui';
import { ArchiveOutline as ArchiveIcon } from '@vicons/ionicons5';
import { lyla } from '@/request';
import { CONST, handleDownload } from '@/utils';

const upload = ref(null);
const fileList = ref([]);
const response = ref('');
const loading = ref(false);
const selectedMode = ref(0);
const options = [
  { label: '常规模式', value: 0 },
  { label: '丹麦模式', value: 1 },
];

const handleChange = (data) => {
  fileList.value = data.fileList;
};

const handleUpload = () => {
  const formData = new FormData();
  for (const item of fileList.value) {
    formData.append(item.name, item.file);
  }
  formData.append('selectedMode', selectedMode.value);
  loading.value = true;
  lyla
    .post('/ce', { body: formData })
    .then((res) => {
      console.log(res);
      // response.value = res.json.data;
      handleDownload(res.json.data, 'excel');
    })
    .catch((error) => {})
    .finally(() => {
      loading.value = false;
      window.scrollTo({
        top: window.innerHeight,
        behavior: 'smooth',
      });
    });
};
</script>

<template>
  <n-space vertical>
    <n-spin :show="loading">
      <n-upload
        multiple
        ref="upload"
        :default-upload="false"
        v-model:file-list="fileList"
        @change="handleChange"
      >
        <n-upload-dragger>
          <div style="margin-bottom: 12px">
            <n-icon size="48" :depth="3">
              <archive-icon />
            </n-icon>
          </div>
          <n-text style="font-size: 16px">
            点击或者拖动文件到该区域来上传
          </n-text>
          <n-p depth="3" style="margin: 8px 0 0 0">
            检查CE表中对应位置的错误项
          </n-p>
        </n-upload-dragger>
      </n-upload>
      <n-space>
        <n-select v-model:value="selectedMode" :options="options" />
        <n-button type="primary" @click="handleUpload"> 开始对比 </n-button>
      </n-space>
    </n-spin>
    <!-- <n-image v-show="response" :src="response" alt="image" width="100%" /> -->
  </n-space>
</template>

<style scoped>
.n-select {
  width: 200px;
}
</style>