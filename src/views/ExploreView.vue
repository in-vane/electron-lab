<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import {
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
import { CONST } from '@/utils';

const message = useMessage();
const upload = ref(null);
const ws = ref(null);
const isComplete = ref([false, false]);

const fileList = ref([]);
const images = ref([[], []]);
const progress = ref([0, 0]);
const current = ref([0, 0]);
const cropend = ref([]);
const response = ref({ result: '' });

const loadingUpload = ref(false);
const loadingCompare = ref(false);

const openWebsocket = () => {
  loadingUpload.value = true;
  const api_url = 'ws://localhost:4242/api';
  const websocket = new WebSocket(api_url);

  websocket.onopen = (e) => {
    console.log('connected: ', e);
    sendMessage(0);
    sendMessage(1);
  };
  websocket.onclose = (e) => {
    console.log('disconnected: ', e);
    loadingUpload.value = false;
  };
  websocket.onmessage = (e) => {
    const data = JSON.parse(e.data);
    const { total, current, img_base64, options } = data;
    if (img_base64) {
      images.value[options.index].push(img_base64);
      progress.value[options.index] = total; // 总数，用以显示进度
      isComplete.value[options.index] = current == total; // 是否完成
      isComplete.value.every((_) => _) && ws.value.close(); // 两个都完成后关闭
    }
  };
  websocket.onerror = (e) => {
    console.log('error: ', e);
  };

  ws.value = websocket;
};

const sendMessage = (index) => {
  const file = fileList.value[index].file;
  const size = file.size;
  const shardSize = 1024 * 1024; // 以1MB为一个分片
  const shardCount = Math.ceil(size / shardSize); // 总片数

  for (let i = 0; i < shardCount; i++) {
    const start = i * shardSize;
    const end = Math.min(size, start + shardSize);
    const fileClip = file.slice(start, end);
    const reader = new FileReader();
    reader.onload = (e) => {
      const message = {
        fileName: file.name,
        file: reader.result,
        total: shardCount,
        current: i + 1,
        options: { mode: CONST.MODE_PDF2IMG.MODE_VECTOR, index },
      };
      ws.value.send(JSON.stringify(message));
    };
    reader.readAsDataURL(fileClip);
  }
};

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
  if (!fileList.value.length) {
    message.info('请选择文件');
    return;
  }
  openWebsocket();
};

const handleCompare = () => {
  if (cropend.value.length != 2) {
    message.info('两张图都需要选择区域，点击缩略图切换！');
    return;
  }
  loadingCompare.value = true;
  const formData = new FormData();
  formData.append('img_1', cropend.value[0].split(',')[1]);
  formData.append('img_2', cropend.value[1].split(',')[1]);
  lyla
    .post('/explore', { body: formData })
    .then((res) => {
      console.log(res);
      response.value = res.json;
    })
    .catch((err) => {})
    .finally(() => {
      loadingCompare.value = false;
      window.scrollTo({
        top: window.innerHeight,
        behavior: 'smooth',
      });
    });
};

const handleSaveResult = () => {
  // const data = response.value.split(',')[1];
  // handleDownload(data, 'img');
};

const handleKeyDownEsc = (e) => {
  if (e.keyCode == 27) {
    cropper.clear();
  }
};

const boxStyle = {
  height: '400px',
  width: '100%',
  border: '1px dashed rgb(224, 224, 230)',
  borderRadius: '3px',
  marginTop: '8px',
};

const options = {
  viewMode: 1,
  dragMode: 'move',
  autoCrop: true,
  cropend: handleGetCrop,
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
      <div>
        <n-h3 prefix="bar">1. 上传PDF</n-h3>
        <n-upload
          multiple
          ref="upload"
          accept=".pdf"
          :max="2"
          :default-upload="false"
          v-model:file-list="fileList"
          :disabled="loadingUpload"
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
        <n-button :disabled="loadingUpload" @click="handleUpload">
          开始转换
        </n-button>
      </div>
      <!-- preview -->
      <n-spin :show="loadingUpload">
        <div class="box-divider">
          <div class="box-divider-item">
            <n-h3 prefix="bar">
              文件1中的图像预览
              {{ `${images[0].length} / ${progress[0]}` }}
            </n-h3>
            <div class="scroll-box">
              <n-scrollbar class="n-scrollbar" x-scrollable>
                <div class="preview-box">
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
              <div class="preview-crop">
                <n-image
                  v-show="cropend[0]"
                  :src="cropend[0]"
                  height="120px"
                  width="100%"
                  alt="image"
                />
              </div>
            </div>
          </div>
          <div class="box-divider-item">
            <n-h3 prefix="bar"
              >文件2中的图像预览
              {{ `${images[1].length} / ${progress[1]}` }}</n-h3
            >
            <div class="scroll-box">
              <n-scrollbar x-scrollable>
                <div class="preview-box">
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
              <div class="preview-crop">
                <n-image
                  v-show="cropend[1]"
                  :src="cropend[1]"
                  height="120px"
                  width="100%"
                  alt="image"
                />
              </div>
            </div>
          </div>
        </div>
      </n-spin>
      <!-- result -->
      <div class="box-divider">
        <div class="box-divider-item">
          <n-h3 prefix="bar">3. 选取对比区域</n-h3>
          <n-button @click="handleCompare"> 开始对比 </n-button>
          <vue-picture-cropper
            :boxStyle="boxStyle"
            :img="images[current[0]][current[1]]"
            :options="options"
          />
        </div>
        <div class="box-divider-item">
          <n-spin :show="loadingCompare">
            <n-h3 prefix="bar">5. 对比结果</n-h3>
            <n-button @click="handleSaveResult"> 保存结果 </n-button>
            <div class="preview-box preview-box-result">
              <n-image
                v-show="response.result"
                :src="response.result"
                alt="image"
                width="100%"
              />
            </div>
          </n-spin>
        </div>
      </div>
    </n-space>
  </div>
</template>

<style scoped>
.n-space {
  gap: 24px 12px !important;
}
.n-h3 {
  margin-bottom: 8px;
}
.box-divider {
  display: flex;
  gap: 24px;
}
.box-divider-item {
  width: calc(50% - 12px);
}
.preview-box {
  display: flex;
  gap: 12px;
  min-height: 200px;
  border-radius: 3px;
  border: 1px dashed rgb(224, 224, 230);
  border-radius: 3px;
}
.preview-crop {
  border: 1px dashed rgb(224, 224, 230);
  border-radius: 3px;
  min-width: 150px;
  min-height: 200px;
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
  margin-top: 8px;
  min-height: 400px;
}
</style>