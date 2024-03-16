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
  NImageGroup,
  NSpin,
  NSpace,
  NH3,
} from 'naive-ui';
import { ArchiveOutline as ArchiveIcon } from '@vicons/ionicons5';
import { lyla } from '@/request';
import { handleDownload } from '@/utils';

const upload = ref(null);
const fileList = ref([]);
const response = ref([]);
const loading = ref(false);

const handleChange = (data) => {
  fileList.value = data.fileList;
};

const handleUpload = () => {
  const formData = new FormData();
  for (const item of fileList.value) {
    formData.append(item.name, item.file);
  }
  loading.value = true;
  lyla
    .post('/screw', { body: formData })
    .then((res) => {
      console.log(res);
      // response.value = res.json.data;
      handleDownload(res.json.data, 'excel');
    })
    .catch((error) => {})
    .finally(() => {
      loading.value = false;
    });
};
</script>

<template>
  <n-space vertical>
    <n-space justify="space-between">
      <n-h3 prefix="bar">选择要检查的PDF文件</n-h3>
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
            检查螺丝包中数量的正误
          </n-p>
        </n-upload-dragger>
      </n-upload>
    </n-spin>
    <!-- <n-h3 v-show="response.length" prefix="bar">检查结果</n-h3>
    <n-image-group>
      <n-space>
        <n-image
          v-for="(img, i) in response"
          :key="i"
          :src="img"
          alt="image"
          height="200px"
        />
      </n-space>
    </n-image-group> -->
  </n-space>
</template>

<style scoped>
.n-image {
  border: solid 1px rgb(224, 224, 230);
  border-radius: 3px;
}
</style>