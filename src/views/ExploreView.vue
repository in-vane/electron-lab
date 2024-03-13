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
import { handleDownload } from '@/utils';

const message = useMessage();
const fileList = ref([]);
const images = ref([]);
const cropend = ref([]);
const currentImg = ref(0);
const compared = ref('');
const upload = ref(null);
const loadingUpload = ref(false);
const loadingCompare = ref(false);

const handleChange = (data) => {
  fileList.value = data.fileList;
};

const handlePreviewClick = (i) => {
  currentImg.value = i;
};

const handleGetCrop = () => {
  const base64 = cropper.getDataURL();
  cropend.value[currentImg.value] = base64;
};

const handleUpload = () => {
  if (fileList.value.length != 2) {
    message.info('请上传两份文件');
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
      images.value = res.json.data;
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

const handleCompare = () => {
  if (cropend.value.length != 2) {
    message.info('两张图都需要选择区域，点击缩略图切换！');
    return;
  }

  const formData = new FormData();
  cropend.value.forEach((_, i) => {
    formData.append(`file_${i}`, _);
  });

  loadingCompare.value = true;
  lyla
    .post('/explore/compare', { body: formData })
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

const handleSaveResult = () => {
  const data = compared.value.split(',')[1];
  handleDownload(data, 'png');
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
        <n-button type="primary" :ghost="true" @click="handleUpload">
          开始转换
        </n-button>
      </n-space>
      <n-spin :show="loadingUpload">
        <n-upload
          multiple
          ref="upload"
          accept=".pdf"
          :max="2"
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
              检查两份pdf中爆炸图与安装图不一致的部分
            </n-p>
          </n-upload-dragger>
        </n-upload>
      </n-spin>
      <!-- preview -->
      <n-spin :show="loadingCompare">
        <div class="box-divider">
          <div class="box-divider-vertical">
            <div class="box-divider-item">
              <n-h3 prefix="bar">2. 单击缩略图以切换选择区域</n-h3>
              <div
                :class="`preview-box ${
                  images.length ? '' : 'preview-box-skeleton'
                }`"
              >
                <n-image
                  v-for="(img, i) in images"
                  :key="i"
                  :src="img[1]"
                  alt="image"
                  width="100%"
                  height="200px"
                  :preview-disabled="true"
                  @click="(e) => handlePreviewClick(i)"
                />
              </div>
            </div>
            <div class="box-divider-item">
              <n-h3 prefix="bar">3. 选择区域</n-h3>
              <vue-picture-cropper
                :boxStyle="{
                  height: '500px',
                  border: '1px dashed rgb(224, 224, 230)',
                  borderRadius: '3px',
                  background: 'rgb(250, 250, 252)',
                }"
                :img="images[currentImg]?.[0]"
                :options="{
                  viewMode: 1,
                  dragMode: 'move',
                  autoCrop: true,
                  cropend: handleGetCrop,
                }"
              />
            </div>
          </div>
          <div class="box-divider-vertical">
            <div class="box-divider-item">
              <n-space justify="space-between">
                <n-h3 prefix="bar">4. 选中区域预览</n-h3>
                <n-button type="primary" :ghost="true" @click="handleCompare">
                  开始对比
                </n-button>
              </n-space>
              <div
                :class="`preview-box ${
                  cropend.length ? '' : 'preview-box-skeleton'
                }`"
              >
                <n-image
                  v-for="(img, i) in cropend"
                  :key="i"
                  :src="img"
                  alt="image"
                  width="100%"
                  height="200px"
                />
              </div>
            </div>
            <div class="box-divider-item">
              <n-space justify="space-between">
                <n-h3 prefix="bar">5. 对比结果</n-h3>
                <n-button
                  type="primary"
                  :ghost="true"
                  @click="handleSaveResult"
                >
                  保存结果
                </n-button>
              </n-space>
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
}
.box-divider-item {
  margin-top: 32px;
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