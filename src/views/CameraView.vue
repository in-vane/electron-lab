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
} from 'naive-ui';
import { ArchiveOutline as ArchiveIcon } from '@vicons/ionicons5';
import { lyla } from '@/request';

const upload = ref(null);
const fileList = ref([]);
const response = ref([]);
const loading = ref(false);
const cropImg = ref('');
const mediaTrack = ref(null);

const LOGI_CAMERA_LABLE = 'USB Camera VID:1133 PID:2085 (046d:0825)';
const VIDEO_WIDTH = 640;
const VIDEO_HEIGHT = 480;
const video = ref(null);
const canvas = document.createElement('canvas');
canvas.width = VIDEO_WIDTH;
canvas.height = VIDEO_HEIGHT;
const ctx = canvas.getContext('2d');

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
  formData.append('cropImg', cropImg.value);
  loading.value = true;
  lyla
    .post('/camera', { body: formData })
    .then((res) => {
      response.value.push(res.json.img_base64_doc);
      response.value.push(res.json.img_base64_pic);
    })
    .catch((error) => {})
    .finally(() => {
      loading.value = false;
      window.scrollTo({
        top: window.innerHeight,
        behavior: 'smooth',
      });
    });
};

const handleOpenCamera = () => {
  loading.value = true;
  navigator.mediaDevices.enumerateDevices().then((devices) => {
    const i = devices.findIndex((_) => _.label == LOGI_CAMERA_LABLE);
    navigator.mediaDevices
      .getUserMedia({
        video: {
          groupId: devices[i].groupId,
          width: VIDEO_WIDTH,
          height: VIDEO_HEIGHT,
        },
      })
      .then((stream) => {
        video.value.srcObject = stream;
        mediaTrack.value = stream;
        video.onloadedmetadata = (e) => {
          video.play();
        };
      })
      .catch((err) => {
        console.log(err);
      })
      .finally(() => {
        loading.value = false;
      });
  });
};

const handleCrop = () => {
  ctx.drawImage(video.value, 0, 0, canvas.width, canvas.height);
  const imgURL = canvas.toDataURL('image/jpeg', 1);
  cropImg.value = imgURL;
};

const handleClearCrop = () => {
  cropImg.value = '';
};

const handleCloseCamera = () => {
  video.srcObject = null;
  console.log(mediaTrack);
  mediaTrack.value.getVideoTracks().forEach((track) => {
    track.stop();
  });
};
</script>

<template>
  <n-space vertical>
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
    <n-space>
      <n-button @click="handleOpenCamera"> 开启摄像头 </n-button>
      <n-button @click="handleCrop"> 截图 </n-button>
      <n-button @click="handleClearCrop"> 清除截图 </n-button>
      <n-button @click="handleCloseCamera"> 关闭摄像头 </n-button>
      <n-button type="primary" @click="handleUpload"> 开始检测 </n-button>
    </n-space>
    <n-space>
      <n-spin :show="loading">
        <video
          ref="video"
          class="n-video"
          autoplay
          :width="VIDEO_WIDTH"
          :height="VIDEO_HEIGHT"
        ></video>
      </n-spin>
      <n-image
        v-show="cropImg"
        :width="VIDEO_WIDTH"
        :height="VIDEO_HEIGHT"
        :src="cropImg"
      />
      <n-image v-for="(img, i) in response" :key="i" :src="img" width="200px" />
    </n-space>
  </n-space>
</template>

<style scoped>
.n-image,
.n-video {
  border-radius: 3px;
}
.n-video {
  background: #000;
}
</style>