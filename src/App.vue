<script setup>
import { h, ref } from 'vue';
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
  NMessageProvider,
} from 'naive-ui';
import {
  HomeOutline as HomeIcon,
  LogoTableau as TableIcon,
  SparklesOutline as SparklesIcon,
  SquareOutline as SquareIcon,
  BookOutline as BookIcon,
  ConstructOutline as ConstructIcon,
  BuildOutline as BuildIcon,
  LanguageOutline as LanguageIcon,
} from '@vicons/ionicons5';
import agsun from '@/assets/agsun.jpeg';

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

function renderIcon(icon) {
  return () => h(NIcon, null, { default: () => h(icon) });
}

const menuOptions = [
  {
    label: () =>
      h(RouterLink, { to: { path: '/home' } }, { default: () => '首页' }),
    key: 'home',
    icon: renderIcon(HomeIcon),
  },
  {
    label: () =>
      h(RouterLink, { to: { path: '/ce' } }, { default: () => 'CE表对比' }),
    key: 'ce',
    icon: renderIcon(TableIcon),
    disabled: true,
  },
  {
    label: () =>
      h(
        RouterLink,
        { to: { path: '/explored' } },
        { default: () => '爆炸图对比' }
      ),
    key: 'explored',
    icon: renderIcon(SparklesIcon),
  },
  {
    label: () =>
      h(
        RouterLink,
        { to: { path: '/contour' } },
        { default: () => '爆炸图零件边缘检测' }
      ),
    key: 'contour',
    icon: renderIcon(SparklesIcon),
  },
  {
    label: () =>
      h(
        RouterLink,
        { to: { path: '/size' } },
        { default: () => '贴纸尺寸检查' }
      ),
    key: 'size',
    icon: renderIcon(SquareIcon),
  },
  {
    label: () =>
      h(
        RouterLink,
        { to: { path: '/pageNumber' } },
        { default: () => '页码检查' }
      ),
    key: 'pageNumber',
    icon: renderIcon(BookIcon),
  },
  {
    label: () =>
      h(
        RouterLink,
        { to: { path: '/table' } },
        { default: () => '明细表零件数量' }
      ),
    key: 'table',
    icon: renderIcon(ConstructIcon),
  },
  {
    label: () =>
      h(RouterLink, { to: { path: '/screw' } }, { default: () => '螺丝数量' }),
    key: 'screw',
    icon: renderIcon(BuildIcon),
  },
  {
    label: () =>
      h(
        RouterLink,
        { to: { path: '/language' } },
        { default: () => '语言前后顺序' }
      ),
    key: 'language',
    icon: renderIcon(LanguageIcon),
  },
  {
    label: () =>
      h(
        RouterLink,
        { to: { path: '/camera' } },
        { default: () => '摄像头测试' }
      ),
    key: 'camera',
    icon: renderIcon(LanguageIcon),
  },
];
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
        <n-message-provider>
          <RouterView />
        </n-message-provider>
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