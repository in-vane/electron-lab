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
  NDropdown,
  NAvatar,
} from 'naive-ui';
import {
  HomeOutline as IHome,
  LogoTableau as ITable,
  SparklesOutline as ISpark,
  CropOutline as ICrop,
  BookOutline as IBook,
  ListOutline as IList,
  BuildOutline as IBuild,
  LanguageOutline as ILang,
  CogOutline as ICog,
  CameraOutline as ICamera,
  AccessibilityOutline as UserIcon,
} from '@vicons/ionicons5';

import agsun from '@/assets/agsun.jpeg';

const l = (path, label) => () =>
  h(RouterLink, { to: { path } }, { default: () => label });
const ri = (icon) => () => h(NIcon, null, { default: () => h(icon) });
const menuOptions = [
  { label: l('/home', '首页'), key: 'home', icon: ri(IHome) },
  { label: l('/ce', 'CE表对比'), key: 'ce', icon: ri(ITable) },
  { label: l('/explore', '爆炸图'), key: 'explore', icon: ri(ISpark) },
  { label: l('/count', '零件计数'), key: 'count', icon: ri(ICog) },
  { label: l('/size', '贴纸尺寸'), key: 'size', icon: ri(ICrop) },
  { label: l('/pageNo', '页码检查'), key: 'pageNo', icon: ri(IBook) },
  { label: l('/table', '明细表'), key: 'table', icon: ri(IList) },
  { label: l('/screw', '螺丝包'), key: 'screw', icon: ri(IBuild) },
  { label: l('/lang', '语言顺序'), key: 'lang', icon: ri(ILang) },
  { label: l('/camera', '实物检测'), key: 'camera', icon: ri(ICamera) },
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
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
    }"
  >
    <n-layout-header bordered>
      <!-- <n-image :src="agsun" /> -->
      <!-- <n-dropdown
        trigger="hover"
        @select="avatarSelect"
        :options="avatarOptions"
      >
        <div class="avatar">
          <n-avatar round>
            <n-icon>
              <user-icon />
            </n-icon>
          </n-avatar>
        </div>
      </n-dropdown> -->
    </n-layout-header>
    <n-layout has-sider>
      <n-layout-sider
        bordered
        default-collapsed
        collapse-mode="width"
        :collapsed-width="64"
        :width="200"
        show-trigger="arrow-circle"
        :native-scrollbar="false"
      >
        <n-menu
          :options="menuOptions"
          :value="routeName"
          :collapsed-width="64"
          :collapsed-icon-size="22"
        />
      </n-layout-sider>
      <n-layout-content
        content-style="padding: 24px;"
        :native-scrollbar="false"
      >
        <n-message-provider>
          <router-view />
        </n-message-provider>
      </n-layout-content>
    </n-layout>
    <!-- <n-layout-footer bordered>Made by NBU</n-layout-footer> -->
  </n-layout>
</template>

<style scoped>
.n-layout-header {
  padding: 0 24px;
}
.n-layout-footer {
  padding: 8px;
  color: rgb(118, 124, 130);
  background: none;
  text-align: center;
}
</style>