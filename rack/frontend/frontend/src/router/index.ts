import { createRouter, createWebHistory } from 'vue-router'
import RackView from '../views/RackView.vue' // Import your view

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: RackView // Set RackView as the default component
    }
  ]
})

export default router