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
} from 'naive-ui';
import { ArchiveOutline as ArchiveIcon } from '@vicons/ionicons5';
import { lyla } from '@/request';

const upload = ref(null);
const fileList = ref([]);
const response = ref('');
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
    .post('/language', { body: formData })
    .then((res) => {
      console.log(res);
      const _ = res.json;
      if (_.is_error) {
        const error_language =
          typeof _.error_language == 'object' ? _.error_language : {};
        let str = '检测到错误';
        for (const [key, value] of Object.entries(error_language)) {
          str += `\n目录为${key}, 正文为${value}`;
        }
        response.value = str;
      } else {
        response.value = '未检测到错误';
      }
    })
    .catch((error) => {})
    .finally(() => {
      loading.value = false;
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
            检查说明书中语言顺序是否正确
          </n-p>
        </n-upload-dragger>
      </n-upload>
      <n-button @click="handleUpload"> 开始检查 </n-button>
    </n-spin>
    <n-p v-show="response">{{ response }}</n-p>
  </n-space>
</template>

<style scoped>
.n-p{
  white-space: pre-line;
}
</style>