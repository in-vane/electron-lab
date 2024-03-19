<script setup>
import { h, onMounted, ref, watchEffect } from 'vue';
import { RouterLink, RouterView, useRoute } from 'vue-router';
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
  HomeOutline as IHome,
  LogoTableau as ITable,
  SparklesOutline as ISpark,
  SquareOutline as ISquare,
  BookOutline as IBook,
  ConstructOutline as IConstruct,
  BuildOutline as IBuild,
  LanguageOutline as ILang,
} from '@vicons/ionicons5';

import agsun from '@/assets/agsun.jpeg';

const renderL = (path, label) => () =>
  h(RouterLink, { to: { path } }, { default: () => label });
const renderI = (icon) => () => h(NIcon, null, { default: () => h(icon) });
const menuOptions = [
  { label: renderL('/home', '首页'), key: 'home', icon: renderI(IHome) },
  { label: renderL('/ce', 'CE表对比'), key: 'ce', icon: renderI(ITable) },
  {
    label: renderL('/explore', '爆炸图'),
    key: 'explore',
    icon: renderI(ISpark),
  },
  {
    label: renderL('/contour', '爆炸图零件计数'),
    key: 'contour',
    icon: renderI(ISpark),
  },
  { label: renderL('/size', '贴纸尺寸'), key: 'size', icon: renderI(ISquare) },
  {
    label: renderL('/pageNumber', '页码检查'),
    key: 'pageNumber',
    icon: renderI(IBook),
  },
  {
    label: renderL('/table', '明细表'),
    key: 'table',
    icon: renderI(IConstruct),
  },
  { label: renderL('/screw', '螺丝包'), key: 'screw', icon: renderI(IBuild) },
  {
    label: renderL('/language', '语言顺序'),
    key: 'language',
    icon: renderI(ILang),
  },
  {
    label: renderL('/camera', '摄像头测试'),
    key: 'camera',
    icon: renderI(ILang),
  },
];
const routeName = ref('');
const route = useRoute();
watchEffect(() => {
  routeName.value = route.name;
});
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
      <n-layout-sider
        collapse-mode="width"
        :collapsed-width="96"
        :width="240"
        show-trigger="arrow-circle"
        bordered
        content-style="padding: 24px;"
      >
        <n-menu :options="menuOptions" :value="routeName" />
      </n-layout-sider>
      <n-layout-content content-style="padding: 24px;">
        <n-message-provider>
          <router-view />
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