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
        <div class="server-selector">
          <transition name="slide-fade">
            <div v-if="serverType === 0" 
                 class="server-option active"
                 @click="switchServer(1)">
              商业大亨
            </div>
            <div v-else 
                 class="server-option active"
                 @click="switchServer(0)">
              企业家
            </div>
          </transition>
        </div>
        <div class="nav-arrow"></div>
        <div class="nav-item">
          <a href="/market" class="nav-link">市场</a>
        </div>
        <div class="nav-arrow"></div>
        <div class="nav-item active">商品详情</div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="detail-content">
      <div class="detail-container">
        <div class="detail-layout">
          <!-- 左侧内容 -->
          <div class="detail-left">
            <!-- 基本信息 -->
            <div class="detail-section">
              <div class="section-header">基本信息</div>
              <div class="section-content">
                <table class="info-table">
                  <tr>
                    <td class="info-label">商品名称</td>
                    <td class="info-value">{{ PRODUCT_TYPES[productId] || '未知商品' }}</td>
                  </tr>
                  <tr>
                    <td class="info-label">商品ID</td>
                    <td class="info-value">{{ productId }}</td>
                  </tr>
                  <tr>
                    <td class="info-label">服务器</td>
                    <td class="info-value">{{ serverType === 0 ? '商业大亨' : '企业家' }}</td>
                  </tr>
                  <tr>
                    <td class="info-label">所属分组</td>
                    <td class="info-value">{{ getProductGroup() }}</td>
                  </tr>
                  <tr>
                    <td class="info-label">商品品质</td>
                    <td class="info-value">{{ quality || '-' }}</td>
                  </tr>
                </table>
              </div>
            </div>
          </div>

          <!-- 右侧内容 -->
          <div class="detail-right">
            <!-- 价格信息 -->
            <div class="detail-section">
              <div class="section-header">价格信息</div>
              <div class="section-content">
                <div class="price-chart">
                  <div class="placeholder">价格趋势图</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { PRODUCT_TYPES, PRODUCT_GROUPS } from '../config.js'

export default {
  name: 'ProductDetail',
  data() {
    return {
      serverType: parseInt(localStorage.getItem('serverType') || '0'),
      productId: null,
      PRODUCT_TYPES
    }
  },
  methods: {
    switchServer(type) {
      this.serverType = type;
      localStorage.setItem('serverType', type.toString());
      window.location.href = `/market/${type}/${this.productId}`;
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
      this.serverType = parseInt(pathParts[2]);
      this.productId = parseInt(pathParts[3]);
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
  padding: 116px 0 0;
  width: 100%;
  max-width: 100%;
  margin: 0;
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

.detail-container {
  margin: 0;
  border-radius: 0;
  box-shadow: none;
}

.detail-section {
  padding: 12px;
  border-bottom: 1px solid #eee;
  background-color: #fff;
}

.detail-section:last-child {
  border-bottom: none;
}

.section-header {
  font-size: 12px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 2px solid #45b97c;
}

.section-content {
  padding: 8px;
}

/* 基本信息表格样式 */
.info-table {
  width: 100%;
  border-collapse: collapse;
  background-color: #fff;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.info-table td {
  padding: 6px 8px;
  border: 1px solid #ebeef5;
  font-size: 12px;
  line-height: 1.2;
}

.info-table .info-label {
  width: 30%;
  color: #666;
  font-size: 12px;
  background-color: #f8f9fa;
}

.info-table .info-value {
  color: #333;
  font-size: 12px;
}

/* 左侧内容布局 */
.detail-layout {
  display: flex;
  gap: 0;
}

.detail-left {
  flex: 1;
  min-width: 300px;
  max-width: 400px;
  background-color: #fff;
  border-right: 1px solid #dcdfe6;
}

/* 小屏幕适配 */
@media screen and (max-width: 768px) {
  .main-content {
    padding: 96px 0 0;
  }
  
  .detail-layout {
    flex-direction: column;
  }
  
  .detail-left {
    max-width: 100%;
    border-right: none;
    border-bottom: 1px solid #dcdfe6;
  }
  
  .section-header {
    font-size: 16px;
  }
  
  .detail-section {
    padding: 15px;
  }
}

/* 中等屏幕适配 */
@media screen and (min-width: 769px) and (max-width: 1200px) {
  .main-content {
    padding: 106px 0 0;
  }
  
  .detail-left {
    flex: 0 0 350px;
  }
}

/* 大屏幕优化 */
@media screen and (min-width: 1201px) {
  .main-content {
    padding: 116px 0 0;
  }
  
  .detail-container {
    margin: 0 auto;
  }
  
  .detail-left {
    flex: 0 0 400px;
  }
}

/* 右侧内容布局 */
.detail-right {
  flex: 2;
  min-width: 300px;
  background-color: #fff;
  padding-left: 20px;
}

.placeholder {
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 4px;
  text-align: center;
  color: #999;
}

.price-chart,
.related-products {
  min-height: 200px;
}
</style>