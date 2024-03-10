<script setup>
import { ref } from 'vue';
import {
  NIcon,
  NButton,
  NUpload,
  NUploadDragger,
  NText,
  NP,
  NImage,
  NSpin,
  NSpace,
  NH3,
} from 'naive-ui';
import { ArchiveOutline as ArchiveIcon } from '@vicons/ionicons5';
import { lyla } from '@/request';

const upload = ref(null);
const fileList = ref([]);
const response = ref('');
const isError = ref(false);
const msg = ref('');
const loading = ref(false);

const handleChange = (data) => {
  fileList.value = data.fileList;
};

const handleUpload = () => {
  if (fileList.value.length < 2) {
  }
  const formData = new FormData();
  for (const item of fileList.value) {
    formData.append(item.name, item.file);
  }
  loading.value = true;
  lyla
    .post('/size', { body: formData })
    .then((res) => {
      console.log(res);
      response.value = res.json.data;
      isError.value = res.json.is_error;
      msg.value = res.json.msg;
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
    <n-space justify="space-between">
      <n-h3 prefix="bar">选择要检查尺寸的CE文件</n-h3>
      <n-button type="primary" :ghost="true" @click="handleUpload">
        开始检查
      </n-button>
    </n-space>
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
            检查贴纸上标注尺寸是否与实际尺寸相符
          </n-p>
        </n-upload-dragger>
      </n-upload>
    </n-spin>
    <n-h3 prefix="bar" :type="isError ? 'error' : 'success'">
      {{ msg }}
    </n-h3>
    <n-image v-show="response" :src="response" alt="image" width="100%" />
  </n-space>
</template>

<style scoped>
.n-image {
  border: solid 1px rgb(224, 224, 230);
  border-radius: 3px;
}
</style>