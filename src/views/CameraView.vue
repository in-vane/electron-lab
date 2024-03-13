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
const response = ref('');
const loading = ref(false);
const cropImgs = ref([]);
const mediaTrack = ref(null);

const LOGI_CAMERA_LABLE = 'USB Camera VID:1133 PID:2085 (046d:0825)';
const VIDEO_WIDTH = 800;
const VIDEO_HEIGHT = 600;
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
  loading.value = true;
  lyla
    .post('/ce', { body: formData })
    .then((res) => {
      console.log(res);
      response.value = res.json.data;
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
      });
  });
};

const handleCrop = () => {
  ctx.drawImage(video.value, 0, 0, canvas.width, canvas.height);
  const imgURL = canvas.toDataURL('image/jpeg', 0.9);
  cropImgs.value.push(imgURL);
};

const handleCloseCamera = () => {
  video.srcObject = null;
  console.log(mediaTrack)
  mediaTrack.value.getVideoTracks().forEach((track) => {
    track.stop();
  });
};
</script>

<template>
  <n-space vertical>
    <n-space>
      <n-button @click="handleOpenCamera"> 开启摄像头 </n-button>
      <n-button @click="handleCrop"> 截图 </n-button>
      <n-button @click="handleCloseCamera"> 关闭摄像头 </n-button>
    </n-space>
    <video ref="video" autoplay width="400" height="300"></video>
    <n-image v-for="(img, i) in cropImgs" :key="i" :src="img" />
  </n-space>
</template>

<style scoped>
</style>