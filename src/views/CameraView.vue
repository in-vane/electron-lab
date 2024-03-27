<script setup>
import { onUnmounted, ref } from 'vue';
import {
  NButton,
  NUpload,
  NImage,
  NImageGroup,
  NSpin,
  NSpace,
  NPopselect,
  NH3,
  NScrollbar,
  NBadge,
  NSelect,
  NDivider,
  useMessage,
} from 'naive-ui';
import { lyla } from '@/request';
import { CONST } from '@/utils'

const message = useMessage();
const ws = ref(null);

const fileList = ref([]);
const images = ref([]);
const current = ref(0);
const cameras = ref([]);
const mediaTrack = ref(null);
const response = ref({ error: true, result: [] });

const MODE_CHAR = 0;
const MODE_ICON = 1;
const mode = ref(MODE_CHAR);
const options = [
  { label: '文字模式', value: MODE_CHAR },
  { label: '图标模式', value: MODE_ICON },
];
const cropBase64 = ref('');

const loadingWebsocket = ref(false);
const loadingUpload = ref(false);

const VIDEO_WIDTH = 1080 / 3;
// const VIDEO_HEIGHT = 1920 / 3;
const VIDEO_HEIGHT = VIDEO_WIDTH * 1.414;
const video = ref(null);
const canvas = document.createElement('canvas');
canvas.width = VIDEO_WIDTH;
canvas.height = VIDEO_HEIGHT;
const ctx = canvas.getContext('2d');

const openWebsocket = () => {
  const api_url = 'ws://localhost:4242/api';
  const websocket = new WebSocket(api_url);

  websocket.onopen = (e) => {
    console.log('connected: ', e);
    loadingUpload.value = true;
    sendMessage();
  };
  websocket.onclose = (e) => {
    console.log('disconnected: ', e);
    loadingUpload.value = false;
  };
  websocket.onmessage = (e) => {
    const data = JSON.parse(e.data);
    const { img_base64, total, current } = data;
    if (img_base64) {
      images.value.push(img_base64);
      current == total && ws.value.close();
    }
  };
  websocket.onerror = (e) => {
    console.log('error: ', e);
  };

  ws.value = websocket;
};

const sendMessage = () => {
  const file = fileList.value[0].file;
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
        options: { mode: CONST.MODE_PDF2IMG.MODE_NORMAL },
      };
      ws.value.send(JSON.stringify(message));
    };
    reader.readAsDataURL(fileClip);
  }
};

const handleUploadPDF = () => {
  if (!fileList.value.length) {
    message.info('请选择文件');
    return;
  }
  openWebsocket();
};

const handleCrop = () => {
  ctx.drawImage(video.value, 0, 0, canvas.width, canvas.height);
  const imgURL = canvas.toDataURL('image/jpeg', 1);
  cropBase64.value = imgURL;
};

const handleCompare = () => {
  if (!fileList.value.length) {
    message.info('请选择文件');
    return;
  }
  handleCrop();
  loadingWebsocket.value = true;
  let url = mode.value == MODE_CHAR ? '/ocr_char' : '/ocr_icon';
  const formData = new FormData();
  formData.append('mode', mode.value);
  formData.append('page', current.value + 1);
  formData.append('crop', cropBase64.value);
  lyla
    .post(url, { body: formData })
    .then((res) => {
      response.value = res.json;
    })
    .catch((err) => {})
    .finally(() => {
      loadingWebsocket.value = false;
    });
};

const handleOpenCamera = () => {
  navigator.mediaDevices
    .getUserMedia({ video: { width: VIDEO_WIDTH, height: VIDEO_HEIGHT } })
    .then((stream) => {
      video.value.srcObject = stream;
      mediaTrack.value = stream;
      video.onloadedmetadata = (e) => {
        video.play();
      };
      navigator.mediaDevices.enumerateDevices().then((devices) => {
        const map = new Map();
        devices.forEach((_) => {
          map.set(_.groupId, _.label);
        });
        const options = [];
        for (let [key, value] of map) {
          options.push({ label: value, value: key });
        }
        cameras.value = options;
      });
    })
    .catch((err) => {});
};

const handleSwitchCamera = (groupId) => {
  handleCloseCamera();
  navigator.mediaDevices
    .getUserMedia({
      video: { groupId, width: VIDEO_WIDTH, height: VIDEO_HEIGHT },
    })
    .then((stream) => {
      video.value.srcObject = stream;
      mediaTrack.value = stream;
      video.onloadedmetadata = (e) => {
        video.play();
      };
    })
    .catch((err) => {});
};

onUnmounted(() => {
  video.srcObject = null;
  if (mediaTrack.value) {
    mediaTrack.value.getVideoTracks().forEach((track) => {
      track.stop();
    });
  }
});
</script>

<template>
  <div>
    <!-- upload -->
    <n-spin :show="loadingUpload" content-class="upload-spin-content">
      <n-h3 prefix="bar">1. 上传PDF</n-h3>
      <n-upload
        :max="1"
        :default-upload="false"
        v-model:file-list="fileList"
        @change="(data) => (fileList = data.fileList)"
      >
        <n-button>选择文件</n-button>
      </n-upload>
      <n-button class="upload-btn" @click="handleUploadPDF">
        开始转换
      </n-button>
      <n-scrollbar x-scrollable>
        <div class="preview-box">
          <div class="preview-item" v-for="(img, i) in images" :key="i">
            <n-badge :value="i + 1" :color="current == i ? '#18a058' : 'gray'">
              <n-image
                :src="img"
                alt="image"
                height="200px"
                preview-disabled
                @click="() => (current = i)"
              />
            </n-badge>
          </div>
        </div>
      </n-scrollbar>
    </n-spin>
    <n-divider />
    <!-- 操作栏 -->
    <n-space vertical>
      <n-h3 prefix="bar">2. 拍摄对比</n-h3>
      <n-space>
        <n-button @click="handleOpenCamera"> 开启摄像头 </n-button>
        <n-popselect
          :options="cameras"
          :on-update:value="handleSwitchCamera"
          trigger="click"
        >
          <n-button :disabled="cameras.length == 0"> 切换摄像头 </n-button>
        </n-popselect>
        <!-- <n-button @click="handleCrop"> 截图 </n-button> -->
        <!-- <n-button @click="handleCloseCamera"> 关闭摄像头 </n-button> -->
        <n-select v-model:value="mode" :options="options" />
        <n-button type="primary" @click="handleCompare"> 开始检测 </n-button>
      </n-space>
      <!-- video区域 -->
      <n-space>
        <video
          ref="video"
          class="n-video"
          autoplay
          :width="VIDEO_WIDTH"
          :height="VIDEO_HEIGHT"
        ></video>
        <n-image
          v-show="images.length"
          :src="images[current]"
          alt="image"
          :height="VIDEO_HEIGHT"
        />
        <n-image-group>
          <n-space>
            <n-image
              v-for="(img, i) in response.result"
              :key="i"
              :src="img"
              alt="image"
              width="200px"
            />
          </n-space>
        </n-image-group>
      </n-space>
    </n-space>
  </div>
</template>

<style scoped>
.upload-spin-content {
  position: relative;
}
.upload-btn {
  position: absolute;
  top: 49px;
  left: 91px;
}
.preview-box {
  display: flex;
  gap: 12px;
  margin-top: 8px;
  min-height: 200px;
  border-radius: 3px;
  border: 1px dashed rgb(224, 224, 230);
  border-radius: 3px;
}
.n-video {
  border-radius: 3px;
  background: #000;
}
.n-image {
  border-radius: 3px;
  border: 1px solid rgb(224, 224, 230);
  cursor: pointer;
}
.n-select {
  width: 160px;
}
</style>