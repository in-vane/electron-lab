<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import {
  NForm,
  NFormItem,
  NInputNumber,
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
  useMessage,
} from 'naive-ui';
import { ArchiveOutline as ArchiveIcon } from '@vicons/ionicons5';
import { lyla } from '@/request';
import VuePictureCropper, { cropper } from 'vue-picture-cropper';

const message = useMessage();
const fileList = ref([]);
const images = ref([]);
const matchResults = ref([]);
const cropend = ref(null);
const compared = ref(null);
const upload = ref(null);
const loadingUpload = ref(false);
const loadingCompare = ref(false);
const pageNumber = ref(0);

const handleChange = (data) => {
  fileList.value = data.fileList;
};

const handleGetCrop = () => {
  const base64 = cropper.getDataURL();
  cropend.value = base64;
};

const handleUpload = () => {
  if (!fileList.value.length) {
    message.info('请选择文件');
    return;
  }
  const formData = new FormData();
  for (const item of fileList.value) {
    formData.append(item.name, item.file);
  }
  loadingUpload.value = true;
  lyla
    .post('/explore/pdf2img', { body: formData })
    .then((res) => {
      console.log(res);
      images.value = res.json.data[0];
    })
    .catch((error) => {
      console.log(error);
    })
    .finally(() => {
      loadingUpload.value = false;
      window.scrollTo({
        top: window.innerHeight,
        behavior: 'smooth',
      });
    });
};

const handleCheckContours = () => {
  const formData = new FormData();
  for (const item of fileList.value) {
    formData.append(item.name, item.file);
  }
  formData.append('img_base64', cropend.value);
  formData.append('pageNumber', pageNumber.value);

  console.log(formData);

  loadingCompare.value = true;
  lyla
    .post('/contours', { body: formData })
    .then((res) => {
      console.log(res);
      // compared.value = res.json.data;
      matchResults.value = res.json.match_results;
    })
    .catch((error) => {})
    .finally(() => {
      loadingCompare.value = false;
      window.scrollTo({
        top: window.innerHeight,
        behavior: 'smooth',
      });
    });
};

const handleKeyDownEsc = (e) => {
  if (e.keyCode == 27) {
    cropper.clear();
  }
};

onMounted(() => {
  document.addEventListener('keydown', handleKeyDownEsc);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDownEsc);
});

const test = [
  ['1', false, 11, [1]],
  ['10', false, 0, [1]],
  ['11', true, null, null],
  ['12', true, null, null],
  ['14', true, null, null],
  ['13', false, 1, [4]],
  ['27', true, null, null],
  ['26', true, null, null],
  ['25', true, null, null],
  ['23', true, null, null],
  ['24', true, null, null],
  ['22', true, null, null],
  ['21', true, null, null],
  ['20', false, 18, [1]],
  ['19', true, null, null],
  ['18', true, null, null],
  ['17', false, 0, [1]],
  ['15', false, 1, [2]],
  ['16', false, 0, [1]],
];
</script>

<template>
  <div>
    <!-- upload -->
    <n-space vertical>
      <n-space justify="space-between">
        <n-h3 prefix="bar">1. 上传PDF</n-h3>
        <n-button type="primary" @click="handleUpload"> 开始转换 </n-button>
      </n-space>
      <n-spin :show="loadingUpload">
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
              pdf中爆炸图零件的边缘检测
            </n-p>
          </n-upload-dragger>
        </n-upload>
      </n-spin>
      <!-- preview -->
      <n-spin :show="loadingCompare">
        <n-space justify="space-between">
          <n-h3 prefix="bar">2. 选取爆炸图</n-h3>
          <n-space>
            <span>爆炸图所在页</span>
            <n-input-number v-model:value="pageNumber" />
            <n-button type="primary" @click="handleCheckContours">
              开始检测
            </n-button>
          </n-space>
        </n-space>
        <div class="box-divider-item">
          <vue-picture-cropper
            :boxStyle="{
              height: '500px',
              border: '1px dashed rgb(224, 224, 230)',
              borderRadius: '3px',
              background: 'rgb(250, 250, 252)',
            }"
            :img="images[0]"
            :options="{
              viewMode: 1,
              dragMode: 'move',
              autoCrop: true,
              cropend: handleGetCrop,
            }"
          />
        </div>
        <n-h3 prefix="bar">3. 零件计数检测结果</n-h3>
        <div class="box-divider-item">
          <!-- <div
            :class="`preview-box preview-box-result ${
              compared ? '' : 'preview-box-skeleton'
            }`"
          >
            <n-image
              v-show="compared"
              :src="compared"
              alt="image"
              width="100%"
              height="500px"
            />
          </div> -->
          <n-space vertical>
            <div v-for="(item, i) in matchResults" :key="i">
              <n-space>
                <span>序号: {{ item[0] }}</span>
                <span>{{ item[1]? '正确': '错误' }}</span>
                <span v-if="!item[1]">检测到 {{ item[2] }} 个</span>
                <span v-if="!item[1]">明细表显示 {{ item[3][0] }} 个</span>
              </n-space>
            </div>
          </n-space>
        </div>
      </n-spin>
    </n-space>
  </div>
</template>

<style scoped>
.box-divider {
  display: flex;
  gap: 24px;
}
.box-divider-vertical {
  width: 50%;
  /* border-top: 1px solid rgb(239, 239, 245); */
  /* padding-top: 24px; */
  margin-top: 16px;
}
.box-divider-item {
  margin-top: 16px;
}
.n-h3 {
  margin-bottom: 0;
}
.preview-box {
  display: flex;
  gap: 12px;
  min-height: 200px;
  border-radius: 3px;
}
.preview-box-skeleton {
  background: rgb(250, 250, 252);
  border: 1px dashed rgb(224, 224, 230);
}
.preview-box-result {
  min-height: 500px;
}
.n-image {
  border: solid 1px rgb(224, 224, 230);
  border-radius: 3px;
}
.n-button {
  /* height: 28px; */
}
</style>