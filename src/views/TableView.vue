<script setup>
import { ref } from 'vue';
import {
  NIcon,
  NButton,
  NInput,
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
// import { handleDownload } from '@/utils';

const upload = ref(null);

const fileList = ref([]);
const pageNumber = ref();
const response = ref({});
const errorPages = ref([]);

const loading = ref(false);

const handleChange = (data) => {
  fileList.value = data.fileList;
};

const handleUpload = () => {
  loading.value = true;
  const formData = new FormData();
  formData.append('file', fileList.value[0].file);
  formData.append('pageNumber', pageNumber.value);
  lyla
    .post('/table', { body: formData })
    .then((res) => {
      console.log(res);
      response.value = res.json;
    })
    .catch((err) => {})
    .finally(() => {
      loading.value = false;
    });
};
</script>

<template>
  <n-space vertical>
    <n-spin :show="loading">
      <n-h3 prefix="bar">1. 选择要检查的PDF文件</n-h3>
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
            检查爆炸图表格与下文不同语言对应表格的正误
          </n-p>
        </n-upload-dragger>
      </n-upload>
      <n-space>
        <n-input
          v-model:value="pageNumber"
          type="text"
          placeholder="爆炸图的页码数"
        />
        <n-button @click="handleUpload"> 开始检查 </n-button>
      </n-space>
    </n-spin>
    <n-h3 prefix="bar">2. 检查结果</n-h3>
    <n-p v-show="response.length">出错表格所在的页码为: {{ errorPages }}</n-p>
  </n-space>
</template>

<style scoped>
.n-space {
  gap: 24px 12px !important;
}
.n-h3 {
  margin-bottom: 8px;
}
</style>