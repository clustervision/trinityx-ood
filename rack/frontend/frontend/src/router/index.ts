import { createRouter, createWebHistory } from 'vue-router'
import RackView from '../views/RackView.vue'
import ManageView from '../views/ManageView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: RackView
    },

    {
      path: '/manage/:page', 
      name: 'manage',
      component: ManageView
    }
  ]
})

export default router