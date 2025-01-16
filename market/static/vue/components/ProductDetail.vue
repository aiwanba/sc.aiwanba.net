<template>
  <div class="market-container">
    <!-- 顶部导航栏 -->
    <div class="nav-header">
      <div class="nav-brand">Simco Tools</div>
      <div class="nav-right">
        <button class="nav-btn">
          <span>主题</span>
        </button>
        <button class="nav-btn">
          <span>ZH</span>
        </button>
        <button class="nav-btn">
          <svg class="menu-icon" viewBox="0 0 24 24" width="24" height="24">
            <path fill="currentColor" d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- 子导航栏 -->
    <div class="sub-nav">
      <div class="nav-section">
        <div class="nav-item">
          <router-link to="/market" class="nav-link">市场</router-link>
        </div>
        <div class="nav-arrow"></div>
        <div v-if="serverType === 0" 
             class="nav-item"
             style="background-color: #fff; color: #333;"
             @click="switchServer(1)">
          商业大亨
        </div>
        <div v-else 
             class="nav-item"
             style="background-color: #fff; color: #333;"
             @click="switchServer(0)">
          企业家
        </div>
        <div class="nav-arrow"></div>
        <div class="nav-item active">商品详情</div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="detail-content">
      <div class="detail-container">
        <div class="detail-layout">
          <!-- 商品基本信息 -->
          <div class="detail-section">
            <div class="section-header">商品基本信息</div>
            <div class="section-content">
              <table class="info-table">
                <tr>
                  <td class="info-group">
                    <span class="info-label">服务器</span>
                    <span class="info-value">{{ serverType === 0 ? '商业大亨' : '企业家' }}</span>
                  </td>
                  <td class="info-group">
                    <span class="info-label">所属分组</span>
                    <span class="info-value">{{ getProductGroup() }}</span>
                  </td>
                  <td class="info-group">
                    <span class="info-label">商品名称</span>
                    <span class="info-value">{{ PRODUCT_TYPES[productId] || '未知商品' }}</span>
                  </td>
                  <td class="info-group">
                    <span class="info-label">商品ID</span>
                    <span class="info-value">{{ productId }}</span>
                  </td>
                </tr>
              </table>
            </div>
          </div>

          <!-- 商品品质信息 -->
          <quality-info 
            v-if="isValidProduct"
            :server-type="serverType"
            :product-id="productId"
          />

          <!-- 商品价格信息 -->
          <price-chart 
            v-if="isValidProduct"
            :server-type="serverType"
            :product-id="productId"
            :quality="currentQuality"
            :period="currentPeriod"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { PRODUCT_TYPES, PRODUCT_GROUPS } from '../config.js'
import PriceChart from './PriceChart.vue'
import QualityInfo from './QualityInfo.vue'

export default {
  name: 'ProductDetail',
  components: {
    PriceChart,
    QualityInfo
  },
  computed: {
    isValidProduct() {
      return typeof this.productId === 'number' && !isNaN(this.productId);
    },
    baseUrl() {
      return window.location.hostname === 'sc.aiwanba.net' 
        ? 'https://sc.aiwanba.net'
        : ''
    }
  },
  data() {
    return {
      serverType: parseInt(localStorage.getItem('serverType') || '0'),
      productId: null,
      currentQuality: 0,
      currentPeriod: '1h',
      PRODUCT_TYPES
    }
  },
  methods: {
    switchServer(type) {
      this.serverType = type;
      localStorage.setItem('serverType', type.toString());
      this.$router.push(`/market/${type}/${this.productId}`);
    },
    getProductGroup() {
      for (const [group, products] of Object.entries(PRODUCT_GROUPS)) {
        if (products.includes(this.productId)) {
          return group;
        }
      }
      return '未分类';
    }
  },
  mounted() {
    const pathParts = window.location.pathname.split('/');
    if (pathParts.length >= 4) {
      const serverType = parseInt(pathParts[2]);
      const productId = parseInt(pathParts[3]);
      
      if (!isNaN(serverType) && !isNaN(productId)) {
        this.serverType = serverType;
        this.productId = productId;
      } else {
        console.warn('无效的服务器类型或商品ID');
        this.$router.push('/market');
      }
    } else {
      this.$router.push('/market');
    }
  }
}
</script>

<style>
/* 基础样式 */
.market-container {
  min-height: 100vh;
  background-color: #f5f5f5;
}

/* 顶部导航栏 */
.nav-header {
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;
  display: flex;
  height: 48px;
  width: 100%;
  align-items: center;
  justify-content: space-between;
  background-color: #2d2d2d;
  padding: 0 20px;
  color: #fff;
}

.nav-brand {
  font-size: 20px;
  font-weight: bold;
  color: #45b97c;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-right: 20px;
}

.nav-btn {
  background: none;
  border: none;
  color: #fff;
  padding: 5px 10px;
  cursor: pointer;
  font-size: 14px;
}

/* 子导航栏 */
.sub-nav {
  position: fixed;
  top: 48px;
  left: 0;
  right: 0;
  height: 48px;
  background-color: #45b97c;
  display: flex;
  align-items: center;
  color: #fff;
  z-index: 999;
}

.nav-section {
  display: flex;
  align-items: center;
  height: 100%;
  margin-left: 20px;
}

.nav-item {
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 20px;
  font-size: 16px;
  font-weight: bold;
  position: relative;
  background-color: #f0f0f0;
  color: #333;
}

.nav-item.active {
  background-color: #45b97c;
  color: #fff;
}

.nav-link {
  color: inherit;
  text-decoration: none;
}

.nav-arrow {
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 24px 0 24px 24px;
  border-color: transparent transparent transparent #f0f0f0;
  margin-right: 20px;
}

/* 主内容区 */
.detail-content {
  padding: 116px 20px 20px;
  width: 100%;
  max-width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}

.detail-container {
  margin: 0 auto;
  width: 100%;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.menu-icon {
  width: 24px;
  height: 24px;
  display: block;
}

.nav-btn:hover .menu-icon {
  opacity: 0.8;
}

/* 服务器选择器样式 */
.server-selector {
  display: flex;
  height: 100%;
  background-color: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
  min-width: 100px;
}

.server-option {
  padding: 0 20px;
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: bold;
  color: #333;
  height: 100%;
  width: 100%;
  position: absolute;
  left: 0;
  top: 0;
}

.server-option.active {
  background-color: #45b97c;
  color: #fff;
}

/* 过渡动画 */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateX(30px);
  opacity: 0;
}

.slide-fade-enter-to,
.slide-fade-leave-from {
  transform: translateX(0);
  opacity: 1;
}

.detail-section {
  padding: 12px;
  background-color: #fff;
  margin-bottom: 0;
}

.section-header {
  font-size: 12px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
  padding-bottom: 4px;
  border-bottom: 2px solid #45b97c;
}

.section-content {
  padding: 0;
}

/* 基本信息表格样式 */
.info-table {
  width: 100%;
  border-collapse: collapse;
  background-color: #fff;
  font-size: 12px;
}

.info-table tr {
  display: flex;
  justify-content: space-between;
  gap: 1px;
  background-color: #f8f9fa;
}

.info-group {
  flex: 1;
  display: flex;
  align-items: center;
  background-color: #fff;
  min-width: 0;  /* 防止内容溢出 */
}

.info-label {
  padding: 8px;
  color: #666;
  background-color: #f8f9fa;
  white-space: nowrap;
  text-align: right;
  min-width: 60px;
}

.info-value {
  padding: 8px;
  color: #333;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 响应式调整 */
@media screen and (max-width: 768px) {
  .info-table tr {
    flex-direction: column;
    gap: 1px;
  }
  
  .info-group {
    width: 100%;
  }
  
  .info-label {
    min-width: 80px;
  }
}

.info-table tbody tr:hover {
  background-color: transparent;
}

.info-table .info-value.price {
  font-family: Monaco, monospace;
  color: #45b97c;
  border: 1px solid #ebeef5;
}

.info-table .info-value.time {
  font-family: Monaco, monospace;
  color: #666;
  font-size: 11px;
  border: 1px solid #ebeef5;
}

/* 价格为空时的样式 */
.info-table .info-value.price:empty::before,
.info-table .info-value.price:contains("-")::before {
  content: "-";
  color: #999;
}

/* 修改主内容区布局 */
.detail-layout {
  display: flex;
  flex-direction: column;  /* 改为纵向布局 */
  gap: 20px;
  padding: 20px;
  width: 100%;
  box-sizing: border-box;
}

.detail-section {
  width: 100%;  /* 占满宽度 */
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* 响应式布局调整 */
@media screen and (max-width: 768px) {
  .detail-content {
    padding: 96px 10px 10px;
  }
  
  .detail-layout {
    gap: 10px;
    padding: 10px;
  }
}

@media screen and (min-width: 769px) {
  .detail-content {
    max-width: 1200px;  /* 限制最大宽度 */
    margin: 0 auto;
  }
  
  .detail-layout {
    gap: 20px;
    padding: 20px;
  }
}

.loading-state,
.error-state {
  padding: 10px;
  text-align: center;
  margin-bottom: 10px;
  border-radius: 4px;
}

.loading-state {
  background-color: #f8f9fa;
  color: #666;
}

.error-state {
  background-color: #fff2f0;
  color: #dc3545;
}

.update-time {
  text-align: right;
  font-size: 11px;
  color: #666;
  margin-top: 4px;
}

/* 添加无数据样式 */
.no-data {
  text-align: center;
  padding: 20px;
  color: #999;
  font-size: 14px;
  background-color: #f8f9fa;
  border: 1px solid #ebeef5;
}

/* 右侧内容布局 */
.detail-right {
  flex: 2;
  min-width: 320px;
  max-width: 100%;
  background-color: #fff;
}

/* 小屏幕适配 */
@media screen and (max-width: 768px) {
  .detail-right {
    flex: none;
    width: 100%;
    min-width: 100%;
  }
}

/* 中等屏幕适配 */
@media screen and (min-width: 769px) and (max-width: 1200px) {
  .detail-right {
    flex: 2;
    min-width: 400px;
  }
}

/* 大屏幕优化 */
@media screen and (min-width: 1201px) {
  .detail-right {
    flex: 2;
    min-width: 600px;
  }
}

/* 响应式调整 */
@media screen and (max-width: 768px) {
  .info-table tr {
    flex-direction: column;  /* 在小屏幕上改为垂直布局 */
  }
  
  .info-table .info-label,
  .info-table .info-value {
    width: 100%;
    max-width: none;
    text-align: left;
  }
  
  .info-table .info-label {
    padding-bottom: 4px;
  }
  
  .info-table .info-value {
    padding-bottom: 8px;
  }
}
</style>