<script setup>
import { ref } from 'vue';
import {
  NRadioGroup,
  NRadio,
  NInput,
  NIcon,
  NButton,
  NUpload,
  NUploadDragger,
  NText,
  NP,
  NImage,
  NSpin,
  NSpace,
  useMessage,
} from 'naive-ui';
import { ArchiveOutline as ArchiveIcon } from '@vicons/ionicons5';
import { lyla } from '@/request';
import result_normal from '@/assets/result_normal.png';

const message = useMessage();
const upload = ref(null);

const fileList = ref([]);
const response = ref({ result: '' });
const loading = ref(false);
const mode = ref(0);
const options = [
  { label: '常规模式', value: 0 },
  { label: '丹麦模式', value: 1 },
];

const handleChange = (data) => {
  fileList.value = data.fileList;
};

const handleUpload = () => {
  if (!fileList.value.length) {
    message.info('请选择文件');
    return;
  }
  loading.value = true;
  const formData = new FormData();
  for (const item of fileList.value) {
    formData.append(item.file.name, item.file);
  }
  formData.append('mode', mode.value);
  // lyla
  //   .post('/ce', { body: formData })
  //   .then((res) => {
  //     console.log(res);
  //     response.value = res.json;
  //   })
  //   .catch((err) => {})
  //   .finally(() => (loading.value = false));
  setTimeout(() => {
    response.value.result = result_normal;
    loading.value = false;
  }, 1000);
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
      <n-space vertical>
        <n-radio-group v-model:value="mode" name="radiogroup">
          <n-space>
            <n-radio
              v-for="option in options"
              :key="option.value"
              :value="option.value"
            >
              {{ option.label }}
            </n-radio>
          </n-space>
        </n-radio-group>
        <n-space>
          <n-input type="text" placeholder="Sheet表" />
          <n-button type="primary" @click="handleUpload"> 开始对比 </n-button>
        </n-space>
      </n-space>
    </n-spin>
    <n-image
      v-show="response.result"
      :src="response.result"
      alt="image"
      width="100%"
    />
  </n-space>
</template>

<style scoped>
.n-select {
  width: 200px;
}
</style>