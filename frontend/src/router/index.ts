import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/plan/:id?',
    name: 'Plan',
    component: () => import('@/views/PlanDetail.vue'),
    props: true
  },
  {
    path: '/map',
    name: 'TripMap',
    component: () => import('@/views/TripMapView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

