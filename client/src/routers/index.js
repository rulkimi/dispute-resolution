import { createWebHistory, createRouter } from 'vue-router';

import HomeView from '@/views/home-view.vue'

const routes = [
  { path: '/', component: HomeView },
  { path: '/buyer', component: () => import('@/views/buyer-view.vue') },
  { path: '/seller', component: () => import('@/views/seller-view.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router;