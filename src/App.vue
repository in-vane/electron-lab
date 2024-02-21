<script setup>
import { h } from 'vue';
import { RouterLink, RouterView } from 'vue-router';
import {
  NLayout,
  NLayoutHeader,
  NLayoutContent,
  NLayoutFooter,
  NLayoutSider,
  NMenu,
  NIcon,
  NImage,
} from 'naive-ui';
import {
  LaptopOutline as WorkIcon,
  LogOutOutline as HomeIcon,
} from '@vicons/ionicons5';
import agsun from '@/assets/agsun.jpeg';

function renderIcon(icon) {
  return () => h(NIcon, null, { default: () => h(icon) });
}

const menuOptions = [
  {
    label: () =>
      h(RouterLink, { to: { path: '/' } }, { default: () => '首页' }),
    key: 'go-back-home',
    icon: renderIcon(HomeIcon),
  },
  {
    label: () =>
      h(RouterLink, { to: { path: '/ce' } }, { default: () => 'CE表对比' }),
    key: 'go-to-ce',
    icon: renderIcon(WorkIcon),
  },
  {
    label: () =>
      h(RouterLink, { to: { path: '/explored' } }, { default: () => '爆炸图对比' }),
    key: 'go-to-explored',
    icon: renderIcon(WorkIcon),
  },
  {
    label: () =>
      h(RouterLink, { to: { path: '/size' } }, { default: () => '尺寸对比' }),
    key: 'go-to-size',
    icon: renderIcon(WorkIcon),
  },
];

// const url = 'http://127.0.0.1:4242/';
// const api_url = 'ws://localhost:4242/api';
// let apiWebSocket = new WebSocket(api_url);

// apiWebSocket.onmessage = function (event) {
//   console.log(event.data);
//   showMessage(JSON.parse(event.data), 'input1');
// };

// function showMessage(message, id) {
//   let inputElement = document.getElementById(id);
//   if (inputElement != null) {
//     inputElement.value = message['data'];
//   }
// }

// function getWebsocketMessage() {
//   apiWebSocket.send(JSON.stringify({ data: 'helloworld' }));
// }

// function getHttpMessage() {
//   fetch(url, {
//     mode: 'cors', // 跨域
//     credentials: 'include', // 发送时携带cookies
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json',
//     },
//     body: JSON.stringify({ data: 'test' }),
//   })
//     .then((response) => response.json())
//     .then((data) => {
//       showMessage(data, 'input2');
//     })
//     .catch((error) => {
//       console.error(error);
//     });
// }
</script>

<template>
  <n-layout
    :content-style="{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
    }"
  >
    <n-layout-header bordered>
      <n-image :src="agsun" />
    </n-layout-header>
    <n-layout has-sider>
      <n-layout-sider content-style="padding: 24px;">
        <n-menu :options="menuOptions" />
      </n-layout-sider>
      <n-layout-content content-style="padding: 24px;">
        <RouterView />
      </n-layout-content>
    </n-layout>
    <n-layout-footer bordered>Made by NBU</n-layout-footer>
  </n-layout>
</template>

<style scoped>
.n-layout-header {
  padding: 0 24px;
}
.n-layout-footer {
  padding: 24px;
  color: rgb(118, 124, 130);
  background: none;
  text-align: center;
}
</style>