import { createRouter, createWebHistory } from 'vue-router'
import CategoryGrid from '../components/CategoryGrid.vue'
import ProductDetail from '../components/ProductDetail.vue'

const routes = [
  {
    path: '/',
    redirect: '/market'
  },
  {
    path: '/market',
    name: 'Market',
    component: CategoryGrid
  },
  {
    path: '/market/:serverType',
    name: 'MarketWithServer',
    component: CategoryGrid,
    props: true
  },
  {
    path: '/market/:serverType/:productId',
    name: 'ProductDetail',
    component: ProductDetail,
    props: route => ({
      serverType: Number(route.params.serverType),
      productId: Number(route.params.productId)
    })
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.params.serverType) {
    const serverType = Number(to.params.serverType)
    if (isNaN(serverType) || ![0, 1].includes(serverType)) {
      next('/market')
      return
    }
  }

  if (to.params.productId) {
    const productId = Number(to.params.productId)
    if (isNaN(productId) || productId < 0) {
      next('/market')
      return
    }
  }

  next()
})

export default router 