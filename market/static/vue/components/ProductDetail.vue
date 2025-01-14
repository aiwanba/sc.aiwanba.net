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
          <a href="/market" class="nav-link">市场</a>
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
          <!-- 左侧内容 -->
          <div class="detail-left">
            <!-- 基本信息 -->
            <div class="detail-section">
              <div class="section-header">基本信息</div>
              <div class="section-content">
                <table class="info-table">
                  <tr>
                    <td class="info-label">服务器</td>
                    <td class="info-value">{{ serverType === 0 ? '商业大亨' : '企业家' }}</td>
                  </tr>
                  <tr>
                    <td class="info-label">所属分组</td>
                    <td class="info-value">{{ getProductGroup() }}</td>
                  </tr>
                  <tr>
                    <td class="info-label">商品名称</td>
                    <td class="info-value">{{ PRODUCT_TYPES[productId] || '未知商品' }}</td>
                  </tr>
                  <tr>
                    <td class="info-label">商品ID</td>
                    <td class="info-value">{{ productId }}</td>
                  </tr>
                </table>
              </div>
            </div>

            <!-- 商品品质 -->
            <div class="detail-section">
              <div class="section-header">商品品质</div>
              <div class="section-content">
                <table class="info-table">
                  <thead>
                    <tr>
                      <th class="info-header">品质等级</th>
                      <th class="info-header">最新价格</th>
                      <th class="info-header">最低价格</th>
                      <th class="info-header">最高价格</th>
                      <th class="info-header">平均价格</th>
                      <th class="info-header">更新时间</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td class="info-label">Q0</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value time">-</td>
                    </tr>
                    <tr>
                      <td class="info-label">Q1</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value time">-</td>
                    </tr>
                    <tr>
                      <td class="info-label">Q2</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value time">-</td>
                    </tr>
                    <tr>
                      <td class="info-label">Q3</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value time">-</td>
                    </tr>
                    <tr>
                      <td class="info-label">Q4</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value time">-</td>
                    </tr>
                    <tr>
                      <td class="info-label">Q5</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value time">-</td>
                    </tr>
                    <tr>
                      <td class="info-label">Q6</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value time">-</td>
                    </tr>
                    <tr>
                      <td class="info-label">Q7</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value time">-</td>
                    </tr>
                    <tr>
                      <td class="info-label">Q8</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value time">-</td>
                    </tr>
                    <tr>
                      <td class="info-label">Q9</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value time">-</td>
                    </tr>
                    <tr>
                      <td class="info-label">Q10</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value time">-</td>
                    </tr>
                    <tr>
                      <td class="info-label">Q11</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value time">-</td>
                    </tr>
                    <tr>
                      <td class="info-label">Q12</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value price">-</td>
                      <td class="info-value time">-</td>
                    </tr>
                  </tbody>
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
  padding: 116px 20px 20px;
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
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
  margin: 0 auto;
  width: 100%;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.detail-section {
  padding: 8px;
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
  margin-bottom: 4px;
  padding-bottom: 4px;
  border-bottom: 2px solid #45b97c;
}

.section-content {
  padding: 4px;
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

.info-table td, .info-table th {
  padding: 4px 6px;
  border: 1px solid #ebeef5;
  font-size: 11px;
  line-height: 1.1;
  text-align: center;
}

.info-table th.info-header {
  background-color: #f8f9fa;
  color: #333;
  font-weight: bold;
  white-space: nowrap;
  font-size: 11px;
  padding: 4px 4px;
}

.info-table .info-label {
  width: 60px;
  color: #666;
  font-size: 11px;
  background-color: #f8f9fa;
  text-align: center;
}

.info-table .info-value {
  color: #333;
  font-size: 11px;
  text-align: center;
}

.info-table .info-value.price {
  font-family: Monaco, monospace;
  color: #45b97c;
  font-size: 11px;
}

.info-table .info-value.time {
  font-family: Monaco, monospace;
  color: #666;
  font-size: 10px;
}

/* 表格行悬停效果 */
.info-table tbody tr:hover {
  background-color: #f5f7fa;
}

/* 价格为空时的样式 */
.info-table .info-value.price:empty::before,
.info-table .info-value.price:contains("-")::before {
  content: "-";
  color: #999;
}

/* 左侧内容布局 */
.detail-layout {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  padding: 20px;
}

.detail-left {
  flex: 1;
  min-width: 320px;
  max-width: 100%;
  background-color: #fff;
}

/* 小屏幕适配 */
@media screen and (max-width: 768px) {
  .detail-content {
    padding: 96px 10px 10px;
  }
  
  .detail-layout {
    flex-direction: column;
    gap: 10px;
    padding: 10px;
  }
  
  .detail-left,
  .detail-right {
    flex: none;
    width: 100%;
    min-width: 100%;
    border: none;
  }
  
  .detail-section {
    margin-bottom: 10px;
  }
}

/* 中等屏幕适配 */
@media screen and (min-width: 769px) and (max-width: 1200px) {
  .detail-content {
    padding: 106px 15px 15px;
  }
  
  .detail-layout {
    gap: 15px;
    padding: 15px;
  }
  
  .detail-left {
    flex: 2;
    min-width: 300px;
  }
  
  .detail-right {
    flex: 3;
  }
}

/* 大屏幕优化 */
@media screen and (min-width: 1201px) {
  .detail-content {
    padding: 116px 20px 20px;
  }
  
  .detail-layout {
    gap: 20px;
    padding: 20px;
  }
  
  .detail-left {
    flex: 1;
    min-width: 400px;
    max-width: 600px;
  }
  
  .detail-right {
    flex: 2;
    min-width: 500px;
  }
}

/* 右侧内容布局 */
.detail-right {
  flex: 2;
  min-width: 320px;
  max-width: 100%;
  background-color: #fff;
}

.placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  border-radius: 4px;
  color: #999;
}

.price-chart,
.related-products {
  min-height: 200px;
}

/* 图表容器自适应 */
.price-chart {
  width: 100%;
  min-height: 300px;
  height: calc(100vh - 500px);
  max-height: 600px;
  background-color: #fff;
  border-radius: 4px;
  overflow: hidden;
}
</style>