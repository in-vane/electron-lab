import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/ce',
      name: 'ce',
      component: () => import('../views/CEView.vue'),
    },
    {
      path: '/explored',
      name: 'explored',
      component: () => import('../views/ExploredView.vue'),
    },
    {
      path: '/size',
      name: 'size',
      component: () => import('../views/SizeView.vue'),
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
