import { createRouter, createWebHistory } from 'vue-router'
import RackView from '../views/RackView.vue'
import ManageView from '../views/ManageView.vue'
import AddRack from '@/views/AddRack.vue'
import EditRack from '@/views/EditRack.vue'

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
    },
    {
      path: '/edit/Rack',
      component: AddRack
    },
    {
      path: '/edit/rack/:id',
      component: EditRack
    }
  ]
})

export default router