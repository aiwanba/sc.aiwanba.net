import { createRouter, createWebHistory } from 'vue-router'
import CategoryGrid from '../components/CategoryGrid.vue'
import ProductDetail from '../components/ProductDetail.vue'

const routes = [
  {
    path: '/',
    name: 'Market',
    component: CategoryGrid
  },
  {
    path: '/:serverType/:productId',
    name: 'ProductDetail',
    component: ProductDetail,
    props: route => ({
      serverType: parseInt(route.params.serverType),
      productId: parseInt(route.params.productId)
    })
  }
]

const router = createRouter({
  history: createWebHistory('/market'),
  routes
})

export default router 