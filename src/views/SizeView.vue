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
import { scrollInneHeight } from '@/utils';

const upload = ref(null);

const fileList = ref([]);
const response = ref({
  error: false,
  error_msg: '',
  result: '',
});

const loading = ref(false);

const handleChange = (data) => {
  console.log(data)
  fileList.value = data.fileList;
};

const handleUpload = () => {
  loading.value = true;
  const formData = new FormData();
  formData.append('file', fileList.value[0].file);
  lyla
    .post('/size', { body: formData })
    .then((res) => {
      console.log(res);
      response.value = res.json;
    })
    .catch((err) => {})
    .finally(() => (loading.value = false));
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
        ref="upload"
        accept=".pdf"
        :max="1"
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
    <div v-show="response.result">
      <n-h3
        prefix="bar"
        :class="`n-h3-${response.error ? 'error' : 'success'}`"
        :type="response.error ? 'error' : 'success'"
      >
        检测结果: {{ response.error_msg }}
      </n-h3>
      <n-image :src="response.result" alt="image" width="100%" />
    </div>
  </n-space>
</template>

<style scoped>
.n-image {
  border: solid 1px rgb(224, 224, 230);
  border-radius: 3px;
}
.n-h3 {
  position: relative;
}
.n-h3-success::after,
.n-h3-error::after {
  content: ' ';
  width: calc(100% - 8px);
  height: 100%;
  position: absolute;
  left: 8px;
  border-radius: 3px;
}
.n-h3-success::after {
  background: rgba(24, 160, 88, 0.2);
}
.n-h3-error::after {
  background: rgba(208, 48, 80, 0.2);
}
</style>