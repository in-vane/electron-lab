<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
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
  useMessage,
} from 'naive-ui';
import { ArchiveOutline as ArchiveIcon } from '@vicons/ionicons5';
import { lyla } from '@/request';
import VuePictureCropper, { cropper } from 'vue-picture-cropper';

const message = useMessage();
const fileList = ref([]);
const images = ref([]);
const cropend = ref(null);
const compared = ref(null);
const upload = ref(null);
const loadingUpload = ref(false);
const loadingCompare = ref(false);

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
    .catch((error) => {})
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
  formData.append('file_0', cropend.value);

  loadingCompare.value = true;
  lyla
    .post('/contours', { body: formData })
    .then((res) => {
      console.log(res);
      compared.value = res.json.data;
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
          <n-button type="primary" @click="handleCheckContours">
            开始检测
          </n-button>
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
        <n-h3 prefix="bar">3. 边缘检测结果</n-h3>
        <div class="box-divider-item">
          <div
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
          </div>
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
  height: 28px;
}
</style>