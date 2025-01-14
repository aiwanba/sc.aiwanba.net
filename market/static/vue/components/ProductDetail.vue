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
                </table>
              </div>
            </div>

            <!-- 当天价格 -->
            <div class="detail-section">
              <div class="section-header">当天价格</div>
              <div class="section-content">
                <div v-for="(priceData, index) in pricesByQuality" :key="index" class="quality-price-info">
                  <div class="quality-header">品质 Q{{ priceData.quality }}</div>
                  <table class="price-table">
                    <tr>
                      <td class="price-label">最新价格</td>
                      <td class="price-value">{{ priceData.latest_price || '暂无数据' }}</td>
                      <td class="price-label">今日最高</td>
                      <td class="price-value">{{ priceData.highest || '暂无数据' }}</td>
                      <td class="price-label">今日最低</td>
                      <td class="price-value">{{ priceData.lowest || '暂无数据' }}</td>
                    </tr>
                    <tr>
                      <td class="price-label">今日均价</td>
                      <td class="price-value">{{ priceData.average || '暂无数据' }}</td>
                      <td class="price-label">日涨跌</td>
                      <td class="price-value" :class="getTrendClass(priceData.daily_trend)">{{ priceData.daily_trend || '暂无数据' }}</td>
                      <td class="price-label">数据条数</td>
                      <td class="price-value">{{ priceData.count }}</td>
                    </tr>
                    <tr>
                      <td class="price-label">更新时间</td>
                      <td class="price-value" colspan="5">{{ priceData.last_update || '暂无数据' }}</td>
                    </tr>
                  </table>
                </div>
                <div v-if="!pricesByQuality.length" class="no-data">暂无价格数据</div>
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
                  <!-- 这里后续添加价格趋势图 -->
                  <div class="placeholder">价格趋势图</div>
                </div>
              </div>
            </div>

            <!-- 交易信息 -->
            <div class="detail-section">
              <div class="section-header">交易信息</div>
              <div class="section-content">
                <div class="trade-stats">
                  <!-- 这里后续添加交易统计信息 -->
                  <div class="placeholder">交易统计</div>
                </div>
              </div>
            </div>

            <!-- 生产信息 -->
            <div class="detail-section">
              <div class="section-header">生产信息</div>
              <div class="section-content">
                <div class="production-info">
                  <!-- 这里后续添加生产相关信息 -->
                  <div class="placeholder">生产信息</div>
                </div>
              </div>
            </div>

            <!-- 相关商品 -->
            <div class="detail-section">
              <div class="section-header">相关商品</div>
              <div class="section-content">
                <div class="related-products">
                  <!-- 这里后续添加相关商品列表 -->
                  <div class="placeholder">相关商品</div>
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
      PRODUCT_TYPES,
      // 当天价格数据
      pricesByQuality: [], // 按品质分类的价格数据
    }
  },
  computed: {
    getDailyTrendClass() {
      // 如果是字符串（暂无数据）或者 null，返回空类名
      if (typeof this.dailyTrend === 'string' || this.dailyTrend === null) return '';
      
      const trend = parseFloat(this.dailyTrend);
      return {
        'trend-up': trend > 0,
        'trend-down': trend < 0,
        'trend-equal': trend === 0
      }
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
    },
    // 获取趋势样式类
    getTrendClass(trend) {
      if (typeof trend === 'string' || trend === null) return '';
      return {
        'trend-up': trend > 0,
        'trend-down': trend < 0,
        'trend-equal': trend === 0
      };
    },
    // 添加格式化时间的方法
    formatTimeAgo(timestamp) {
      if (!timestamp) return '暂无数据';
      
      // 将 YYYY-MM-DD HH:mm:ss 转换为 ISO 格式并添加 UTC 标识
      const utcTime = timestamp.replace(' ', 'T') + 'Z';
      const date = new Date(utcTime);
      const now = new Date();
      const diffMinutes = Math.floor((now - date) / (1000 * 60));
      
      // 小于1分钟显示为0分钟前
      if (diffMinutes < 1) return '0分钟前';
      if (diffMinutes < 60) return `${diffMinutes}分钟前`;
      
      const diffHours = Math.floor(diffMinutes / 60);
      if (diffHours < 24) return `${diffHours}小时前`;
      
      // 如果超过24小时，显示具体时间
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      });
    },
    // 修改获取当天价格数据的方法
    async fetchTodayPrices() {
      try {
        const response = await fetch(`/market/api/prices/today/${this.serverType}/${this.productId}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        // 更新价格数据
        this.pricesByQuality = data.map(item => ({
          ...item,
          latest_price: item.latest_price?.toFixed(3),
          highest: item.highest?.toFixed(3),
          lowest: item.lowest?.toFixed(3),
          average: item.average?.toFixed(3),
          daily_trend: item.daily_trend?.toFixed(3),
          last_update: this.formatTimeAgo(item.last_update)
        }));
      } catch (error) {
        this.pricesByQuality = [];
      }
    }
  },
  mounted() {
    const pathParts = window.location.pathname.split('/');
    if (pathParts.length >= 4) {
      this.serverType = parseInt(pathParts[2]);
      this.productId = parseInt(pathParts[3]);
      // 获取当天价格数据
      this.fetchTodayPrices();
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
  margin: 0;  /* 移除容器外边距 */
  border-radius: 0;  /* 移除圆角 */
  box-shadow: none;  /* 移除阴影 */
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

.info-item {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
}

.label {
  width: 100px;
  color: #999;
}

.value {
  color: #333;
  font-weight: 500;
}

.placeholder {
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 4px;
  text-align: center;
  color: #999;
}

.price-chart,
.trade-stats,
.production-info,
.related-products {
  min-height: 200px;
}

/* 当天价格样式 */
.price-info {
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.price-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.price-item {
  text-align: center;
  padding: 15px;
  background-color: white;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.price-label {
  color: #666;
  font-size: 14px;
  margin-bottom: 8px;
}

.price-value {
  color: #333;
  font-size: 20px;
  font-weight: bold;
}

.price-trend {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background-color: white;
  border-radius: 6px;
}

.trend-item {
  display: flex;
  align-items: center;
}

.trend-label {
  color: #666;
  margin-right: 8px;
}

.trend-value {
  font-weight: 500;
  font-size: 16px;
}

.trend-value.trend-up {
  color: #f56c6c !important;
  font-size: 12px;
}

.trend-value.trend-down {
  color: #67c23a !important;
  font-size: 12px;
}

.trend-value.trend-equal {
  color: #909399 !important;
  font-size: 12px;
}

.quality-price-info {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.quality-price-info:last-child {
  margin-bottom: 0;
}

.quality-header {
  font-size: 12px;
  font-weight: bold;
  margin-bottom: 4px;
  color: #409eff;
  padding: 0 4px;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  gap: 4px;
}

.no-data {
  text-align: center;
  color: #909399;
  padding: 20px;
}

/* 新增左右布局样式 */
.detail-layout {
  display: flex;
  gap: 0;  /* 移除间距 */
  flex-wrap: wrap;
}

.detail-left {
  flex: 1;
  min-width: 300px;
  max-width: 400px;
  background-color: #fff;  /* 添加背景色 */
  border-right: 1px solid #dcdfe6;  /* 添加右侧分隔线 */
}

.detail-right {
  flex: 2;
  min-width: 300px;
  background-color: #fff;  /* 添加背景色 */
  padding-left: 20px;  /* 添加左侧内边距 */
}

/* 调整价格信息卡片在左侧时的样式 */
.detail-left .price-row {
  grid-template-columns: repeat(2, 1fr);  /* 改为两列布局 */
}

.detail-left .price-trend {
  flex-direction: column;
  gap: 10px;
}

.detail-left .trend-item {
  width: 100%;
  justify-content: space-between;
}

/* 小屏幕适配 */
@media screen and (max-width: 768px) {
  .main-content {
    padding: 96px 0 0;  /* 调整顶部内边距,移除左右内边距 */
  }
  
  .detail-layout {
    flex-direction: column;
  }
  
  .detail-left {
    max-width: 100%;
    border-right: none;  /* 移除右侧分隔线 */
    border-bottom: 1px solid #dcdfe6;  /* 添加底部分隔线 */
  }
  
  .detail-right {
    width: 100%;
    padding-left: 0;  /* 移除左侧内边距 */
  }
  
  .price-row {
    grid-template-columns: repeat(2, 1fr) !important;  /* 强制两列布局 */
    gap: 10px;
  }
  
  .price-trend {
    flex-direction: column;
    gap: 10px;
  }
  
  .trend-item {
    width: 100%;
    justify-content: space-between;
  }
  
  .section-header {
    font-size: 16px;
  }
  
  .price-value {
    font-size: 16px;
  }
  
  .detail-section {
    padding: 15px;  /* 减小内边距 */
  }
}

/* 中等屏幕适配 */
@media screen and (min-width: 769px) and (max-width: 1200px) {
  .main-content {
    padding: 106px 0 0;  /* 调整顶部内边距,移除左右内边距 */
  }
  
  .detail-left {
    flex: 0 0 350px;
  }
  
  .price-row {
    gap: 15px;
  }
}

/* 大屏幕优化 */
@media screen and (min-width: 1201px) {
  .main-content {
    padding: 116px 0 0;  /* 调整顶部内边距,移除左右内边距 */
  }
  
  .detail-container {
    margin: 0 auto;
  }
  
  .detail-left {
    flex: 0 0 400px;
  }
}

/* 价格表格样式 */
.price-table {
  width: 100%;
  border-collapse: collapse;
  background-color: #fff;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.price-table td {
  padding: 4px 6px;  /* 进一步减小内边距 */
  border: 1px solid #ebeef5;
  font-size: 12px;
  line-height: 1.1;  /* 减小行高 */
}

.price-table .price-label {
  width: 16.66%;  /* 每行6个单元格,平均分配 */
  color: #666;
  font-size: 12px;
  background-color: #f8f9fa;
  white-space: nowrap;  /* 防止文字换行 */
}

.price-table .price-value {
  width: 16.66%;
  color: #333;
  font-weight: 500;
  text-align: right;
  font-size: 12px;
}

.quality-price-info {
  margin-bottom: 8px;  /* 进一步减小间距 */
  padding: 4px;  /* 减小内边距 */
}

.quality-header {
  font-size: 12px;
  font-weight: bold;
  margin-bottom: 4px;
  color: #409eff;
  padding: 0 4px;
  text-transform: uppercase;
}

/* 保持涨跌颜色样式但调整大小 */
.price-value.trend-up {
  color: #f56c6c !important;
  font-size: 12px;
}

.price-value.trend-down {
  color: #67c23a !important;
  font-size: 12px;
}

.price-value.trend-equal {
  color: #909399 !important;
  font-size: 12px;
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
</style> 