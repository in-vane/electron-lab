<script setup>
import { ref } from 'vue';
import {
  NRadioGroup,
  NRadio,
  NIcon,
  NButton,
  NUpload,
  NUploadDragger,
  NText,
  NP,
  NImage,
  NImageGroup,
  NSpin,
  NSpace,
  NPopselect,
  useMessage,
} from 'naive-ui';
import { ArchiveOutline as ArchiveIcon } from '@vicons/ionicons5';
import { lyla } from '@/request';
import { mock_ocr_char } from '@/utils/mock_ocr_char';
import { mock_ocr_icon_1, mock_ocr_icon_2 } from '@/utils/mock_ocr_icon';
import camera_result from '@/assets/camera_result.jpeg';

const message = useMessage();
const upload = ref(null);
const fileList = ref([]);
const cropImg = ref('');
const cameras = ref([]);
const mediaTrack = ref(null);
const response = ref({
  error: true,
  result: [],
});

const MODE_CHAR = 0;
const MODE_ICON = 1;
const mode = ref(MODE_CHAR);
const options = [
  { label: '文字模式', value: MODE_CHAR },
  { label: '图标模式', value: MODE_ICON },
];

const loading = ref(false);

const VIDEO_WIDTH = 1080 / 3;
const VIDEO_HEIGHT = 1920 / 3;
const video = ref(null);
const canvas = document.createElement('canvas');
canvas.width = VIDEO_WIDTH;
canvas.height = VIDEO_HEIGHT;
const ctx = canvas.getContext('2d');

const handleChange = (data) => {
  fileList.value = data.fileList;
};

const handleUpload = () => {
  if (!fileList.value.length) {
    message.info('请选择文件');
    return;
  }
  loading.value = true;
  let url = '';
  const formData = new FormData();
  formData.append('mode', mode.value);
  if (mode.value == MODE_CHAR) {
    url = '/ocr_char';
    formData.append('file', fileList.value[0].file);
    formData.append('img_base64', cropImg.value.split(',')[1]);
  }
  if (mode.value == MODE_ICON) {
    url = '/ocr_icon';
    formData.append('img_1', fileList.value[0].file);
    formData.append('img_2', fileList.value[1].file);
  }
  // lyla
  //   .post(url, { body: formData })
  //   .then((res) => {
  //     response.value = res.json;
  //   })
  //   .catch((err) => {})
  //   .finally(() => {
  //     loading.value = false;
  //   });
  setTimeout(() => {
    if (mode.value == MODE_CHAR) {
      response.value.result = [camera_result];
    }
    if (mode.value == MODE_ICON) {
      response.value.result = [mock_ocr_icon_1, mock_ocr_icon_2];
    }

    loading.value = false;
  }, 1000);
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

const handleCloseCamera = () => {
  video.srcObject = null;
  mediaTrack.value.getVideoTracks().forEach((track) => {
    track.stop();
  });
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

const handleCrop = () => {
  ctx.drawImage(video.value, 0, 0, canvas.width, canvas.height);
  const imgURL = canvas.toDataURL('image/jpeg', 1);
  cropImg.value = imgURL;
};
</script>

<template>
  <n-space vertical>
    <n-upload
      multiple
      ref="upload"
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
      <n-button @click="handleOpenCamera"> 开启摄像头 </n-button>
      <n-popselect
        :options="cameras"
        :on-update:value="handleSwitchCamera"
        trigger="click"
      >
        <n-button :disabled="cameras.length == 0"> 切换摄像头 </n-button>
      </n-popselect>
      <n-button @click="handleCrop"> 截图 </n-button>
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
      <n-image v-show="cropImg" :src="cropImg" alt="image" width="200px" />
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
</template>

<style scoped>
.n-video {
  border-radius: 3px;
}
.n-image {
  border-radius: 3px;
  border: 1px solid rgb(224, 224, 230);
}
.n-video {
  background: #000;
}
</style>