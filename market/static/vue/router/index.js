import { createRouter, createWebHistory } from 'vue-router'
import CategoryGrid from '../components/CategoryGrid.vue'
import ProductDetail from '../components/ProductDetail.vue'

const router = createRouter({
  history: createWebHistory('/market'),
  routes: [
    {
      path: '/',
      name: 'Market',
      component: CategoryGrid
    },
    {
      path: '/:serverType/:productId',
      name: 'ProductDetail',
      component: ProductDetail,
      props: true
    }
  ]
})

export default router 