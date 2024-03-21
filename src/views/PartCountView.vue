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
  NDataTable,
  useMessage,
} from 'naive-ui';
import { ArchiveOutline as ArchiveIcon } from '@vicons/ionicons5';
import { lyla } from '@/request';
import VuePictureCropper, { cropper } from 'vue-picture-cropper';

const message = useMessage();
const upload = ref(null);
const ws = ref(null);

const fileList = ref([]);
const images = ref([]);
const current = ref(0);
const cropend = ref('');
const rect = ref([]);
const response = ref({
  error: false,
  result: [[]],
});

const loadingUpload = ref(false);
const loadingPartCount = ref(false);

const openWebsocket = () => {
  loadingUpload.value = true;
  const api_url = 'ws://localhost:4242/api';
  const websocket = new WebSocket(api_url);

  websocket.onopen = (e) => {
    console.log('connected: ', e);
    sendMessage();
  };
  websocket.onclose = (e) => {
    console.log('disconnected: ', e);
    loadingUpload.value = false;
  };
  websocket.onmessage = (e) => {
    const data = JSON.parse(e.data);
    if (data.type == 'sendFileClip') {
      images.value.push(data.img_base64);
      if (data.current == data.total) {
        ws.value.close();
      }
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
      const blob = reader.result;
      ws.value.send(
        JSON.stringify({
          type: 'sendFileClip',
          fileName: file.name,
          currentSlice: i + 1,
          totalSlice: shardCount,
          file: blob,
        })
      );
    };
    reader.readAsDataURL(fileClip);
  }
};

const handleChange = (data) => {
  fileList.value = data.fileList;
};

const handlePreviewClick = (selectedImg) => {
  current.value = selectedImg;
};

const handleGetCrop = () => {
  const base64 = cropper.getDataURL();
  const data = cropper.getData();
  rect.value = [data.x, data.y, data.width, data.height];
  cropend.value = base64;
};

const handleUpload = () => {
  if (!fileList.value.length) {
    message.info('请选择文件');
    return;
  }
  openWebsocket();
};

const handlePartCount = () => {
  loadingPartCount.value = true;
  const file = fileList.value[0].file;
  const formData = new FormData();
  formData.append('filename', file.name);
  // formData.append('rect', rect.value);
  const a = [20, 60, 550, 680];
  for (let i = 0; i < 4; i++) {
    formData.append('rect', a[i]);
  }
  formData.append('pageNumberExplore', 6);
  formData.append('pageNumberTable', 7);
  lyla
    .post('/partCount', { body: formData })
    .then((res) => {
      console.log(res);
      response.value = res.json;
    })
    .catch((error) => {})
    .finally(() => {
      loadingPartCount.value = false;
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

const boxStyle = {
  height: '400px',
  width: '100%',
  border: '1px dashed rgb(224, 224, 230)',
  borderRadius: '3px',
};

const options = {
  viewMode: 1,
  dragMode: 'move',
  autoCrop: true,
  cropend: handleGetCrop,
};

const columns = [
  {
    title: '零件序号',
    key: 'no',
    sorter: (a, b) => parseInt(a.no) - parseInt(b.no),
    render: (_) => parseInt(_.no),
  },
  {
    title: '计数正误',
    key: 'state',
    render: (_) => (_.state ? '正确' : '错误'),
  },
  {
    title: '检测计数',
    key: 'found',
    render: (_) => (_.found == null ? '-' : _.found),
  },
  {
    title: '表格计数',
    key: 'expected',
    render: (_) => (_.expected == null ? '-' : _.expected[0]),
  },
];

const mock = [
  { no: '1', state: true, found: null, expected: null },
  { no: '2', state: true, found: null, expected: null },
  { no: '8', state: true, found: null, expected: null },
  { no: '3', state: true, found: null, expected: null },
  { no: '4', state: true, found: null, expected: null },
  { no: '5', state: true, found: null, expected: null },
  { no: '6', state: true, found: null, expected: null },
  { no: '7', state: true, found: null, expected: null },
  { no: '9', state: true, found: null, expected: null },
  { no: '11', state: false, found: 0, expected: [1] },
  { no: '10', state: true, found: null, expected: null },
  { no: '12', state: true, found: null, expected: null },
  { no: '13', state: false, found: 1, expected: [2] },
  { no: '14', state: true, found: null, expected: null },
  { no: '15', state: true, found: null, expected: null },
  { no: '16', state: true, found: null, expected: null },
  { no: '17', state: true, found: null, expected: null },
  { no: '18', state: true, found: null, expected: null },
  { no: '19', state: false, found: 4, expected: [1] },
  { no: '20', state: true, found: null, expected: null },
  { no: '21', state: true, found: null, expected: null },
  { no: '22', state: true, found: null, expected: null },
  { no: '23', state: true, found: null, expected: null },
  { no: '24', state: true, found: null, expected: null },
];

const renderRowClass = (rowData) => (rowData.state ? '' : 'row-error');

onMounted(() => {
  document.addEventListener('keydown', handleKeyDownEsc);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDownEsc);
});
</script>

<template>
  <n-space vertical>
    <!-- upload -->
    <div>
      <n-h3 prefix="bar">1. 上传PDF</n-h3>
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
        <n-button type="primary" :ghost="true" @click="handleUpload">
          开始转换
        </n-button>
      </n-spin>
    </div>
    <!-- preview -->
    <n-spin :show="loadingPartCount">
      <n-h3 prefix="bar">2. 文件图像预览</n-h3>
      <n-button @click="handlePartCount">开始任务</n-button>
      <div class="scroll-box">
        <n-scrollbar class="n-scrollbar" x-scrollable>
          <div class="preview-box">
            <n-image
              v-for="(img, i) in images"
              :key="i"
              :src="img"
              alt="image"
              height="200px"
              @click="(e) => handlePreviewClick(i)"
            />
          </div>
        </n-scrollbar>
        <div class="preview-crop">
          <n-image
            v-show="cropend"
            :src="cropend"
            height="120px"
            width="100%"
            alt="image"
          />
        </div>
      </div>
      <vue-picture-cropper
        :boxStyle="boxStyle"
        :img="images[current]"
        :options="options"
      />
    </n-spin>
    <div>
      <n-h3 prefix="bar">3. 零件计数检测结果</n-h3>
      <n-data-table
        size="small"
        :columns="columns"
        :data="mock"
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
.scroll-box {
  display: flex;
  gap: 12px;
}
.n-scrollbar {
  flex: 1;
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
  /* background: rgb(250, 250, 252); */
  min-width: 150px;
  min-height: 200px;
}
:deep(.row-error td) {
  color: rgb(208, 48, 80);
  background: rgba(208, 48, 80, 0.2);
}
</style>