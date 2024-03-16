<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import {
  NSwitch,
  NScrollbar,
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
import bgGray from '@/assets/bgGray.png';
import testImg from './a2.jpg';

const message = useMessage();
const fileList = ref([]);
const images = ref([
  [testImg, testImg, testImg, testImg],
  [testImg, testImg, testImg, testImg],
]);
const cropend = ref([bgGray, bgGray]);
const current = ref([0, 0]);
const compared = ref('');
const upload = ref(null);
const loadingUpload = ref(false);
const loadingCompare = ref(false);

const handleChange = (data) => {
  fileList.value = data.fileList;
};

const handlePreviewClick = (selectedPDF, selectedImg) => {
  current.value[0] = selectedPDF;
  current.value[1] = selectedImg;
};

const handleGetCrop = () => {
  const base64 = cropper.getDataURL();
  cropend.value[current.value[0]] = base64;
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
  handleDownload(data, 'img');
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
    <n-space vertical>
      <!-- upload -->
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
          <div class="box-divider-item">
            <n-h3 prefix="bar">文件1中的图像预览</n-h3>
            <div class="scroll-box">
              <n-scrollbar x-scrollable>
                <div
                  :class="`preview-box ${
                    images.length ? '' : 'preview-box-skeleton'
                  }`"
                >
                  <n-image
                    v-for="(img, i) in images[0]"
                    :key="i"
                    :src="img"
                    alt="image"
                    height="200px"
                    @click="(e) => handlePreviewClick(0, i)"
                  />
                </div>
              </n-scrollbar>
              <n-image
                :src="cropend[0]"
                height="120px"
                width="100%"
                alt="image"
              />
            </div>
          </div>
          <div class="box-divider-item">
            <n-h3 prefix="bar">文件2中的图像预览</n-h3>
            <div class="scroll-box">
              <n-scrollbar x-scrollable>
                <div
                  :class="`preview-box ${
                    images.length ? '' : 'preview-box-skeleton'
                  }`"
                >
                  <n-image
                    v-for="(img, i) in images[1]"
                    :key="i"
                    :src="img"
                    alt="image"
                    height="200px"
                    @click="(e) => handlePreviewClick(1, i)"
                  />
                </div>
              </n-scrollbar>
              <n-image
                :src="cropend[1]"
                height="120px"
                width="100%"
                alt="image"
              />
            </div>
          </div>
        </div>
        <div class="box-divider">
          <div class="box-divider-item">
            <n-space justify="space-between">
              <n-h3 prefix="bar">3. 选取对比区域</n-h3>
              <n-button type="primary" :ghost="true" @click="handleCompare">
                开始对比
              </n-button>
            </n-space>
            <vue-picture-cropper
              :boxStyle="{
                height: '400px',
                width: '100%',
                border: '1px dashed rgb(224, 224, 230)',
                borderRadius: '3px',
                background: 'rgb(250, 250, 252)',
              }"
              :img="images[current[0]][current[1]]"
              :options="{
                viewMode: 1,
                dragMode: 'move',
                autoCrop: true,
                cropend: handleGetCrop,
              }"
            />
          </div>
          <div class="box-divider-item">
            <n-space justify="space-between">
              <n-h3 prefix="bar">5. 对比结果</n-h3>
              <n-button type="primary" :ghost="true" @click="handleSaveResult">
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
              />
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
.box-divider-item {
  width: calc(50% - 12px);
  margin-top: 32px;
}
.preview-box {
  display: flex;
  gap: 12px;
  border-radius: 3px;
}
.preview-box-skeleton {
  background: rgb(250, 250, 252);
  border: 1px dashed rgb(224, 224, 230);
  min-height: 120px;
}
.scroll-box {
  display: flex;
  gap: 12px;
}
.preview-box-result {
  min-height: 400px;
}
.n-image {
  border: 1px dashed rgb(224, 224, 230);
  border-radius: 3px;
  background: rgb(250, 250, 252);
  min-width: 150px;
  min-height: 200px;
}
.n-button {
  height: 28px;
}
</style>