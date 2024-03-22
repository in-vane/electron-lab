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
  NDataTable,
} from 'naive-ui';
import { ArchiveOutline as ArchiveIcon } from '@vicons/ionicons5';
import { lyla } from '@/request';

const upload = ref(null);
const fileList = ref([]);
const response = ref({
  error: false,
  content_page: 0,
  result: [],
});
const loading = ref(false);

const handleChange = (data) => {
  fileList.value = data.fileList;
};

const handleUpload = () => {
  loading.value = true;
  const formData = new FormData();
  formData.append('file', fileList.value[0].file);
  // lyla
  //   .post('/language', { body: formData })
  //   .then((res) => {
  //     console.log(res);
  //     response.value = res.json;
  //   })
  //   .catch((err) => {})
  //   .finally(() => {
  //     loading.value = false;
  //   });
  setTimeout(() => {
    response.value.result = mock
    loading.value = false;
  }, 1000);
};
const renderRowClass = (rowData) => (rowData.error ? 'row-error' : '');
const columns = [
  { title: '目录语言', key: 'language' },
  { title: '页码范围', render: (_) => _.page_number.join(' ~ ') },
  { title: '顺序正误', render: (_) => (_.error ? '错误' : '正确') },
  { title: '正文语言', render: (_) => (_.error ? _.actual_language : '-') },
];
const mock = [
  {
    language: 'FR',
    page_number: [11, 17],
    error: true,
    actual_language: 'EN',
  },
  {
    language: 'EN',
    page_number: [18, 24],
    error: true,
    actual_language: 'FR',
  },
  {
    language: 'NL',
    page_number: [4, 10],
    error: false,
    actual_language: 'NL',
  },
  {
    language: 'DE',
    page_number: [25, 52],
    error: false,
    actual_language: 'DE',
  },
];
</script>

<template>
  <n-space vertical>
    <n-spin :show="loading">
      <n-h3 prefix="bar">1. 上传PDF</n-h3>
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
    <div>
      <n-h3 prefix="bar">2. 语言顺序检测结果</n-h3>
      <n-data-table
        size="small"
        :columns="columns"
        :data="response.result"
        :bordered="false"
        :row-class-name="renderRowClass"
      />
    </div>
  </n-space>
</template>

<style scoped>
.n-space {
  gap: 24px 12px !important;
}
.n-h3 {
  margin-bottom: 8px;
}
:deep(.row-error td) {
  color: rgb(208, 48, 80);
  background: rgba(208, 48, 80, 0.2);
}
</style>