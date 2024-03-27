import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/home',
    },
    {
      path: '/home',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/ce',
      name: 'ce',
      component: () => import('../views/CEView.vue'),
    },
    {
      path: '/explore',
      name: 'explore',
      component: () => import('../views/ExploreView.vue'),
    },
    {
      path: '/count',
      name: 'count',
      component: () => import('../views/PartCountView.vue'),
    },
    {
      path: '/size',
      name: 'size',
      component: () => import('../views/SizeView.vue'),
    },
    {
      path: '/pageNo',
      name: 'pageNo',
      component: () => import('../views/PageNumberView.vue'),
    },
    {
      path: '/table',
      name: 'table',
      component: () => import('../views/TableView.vue'),
    },
    {
      path: '/screw',
      name: 'screw',
      component: () => import('../views/ScrewView.vue'),
    },
    {
      path: '/lang',
      name: 'lang',
      component: () => import('../views/LanguageView.vue'),
    },
    {
      path: '/camera',
      name: 'camera',
      component: () => import('../views/CameraView.vue'),
    },
    // {
    //   path: '/about',
    //   name: 'about',
    //   // route level code-splitting
    //   // this generates a separate chunk (About.[hash].js) for this route
    //   // which is lazy-loaded when the route is visited.
    //   component: () => import('../views/AboutView.vue')
    // }
  ],
});

export default router;
