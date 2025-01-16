<template>
  <div class="detail-section">
    <div class="section-header">商品品质信息</div>
    <div class="section-content">
      <div v-if="loading" class="loading-state">加载中...</div>
      <div v-if="error" class="error-state">{{ error }}</div>
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
          <template v-if="qualityData && qualityData.length > 0">
            <tr v-for="item in qualityData" :key="item.quality">
              <td class="info-label">Q{{ item.quality }}</td>
              <td class="info-value price">{{ formatPrice(item.latestPrice) }}</td>
              <td class="info-value price">{{ formatPrice(item.lowestPrice) }}</td>
              <td class="info-value price">{{ formatPrice(item.highestPrice) }}</td>
              <td class="info-value price">{{ formatPrice(item.averagePrice) }}</td>
              <td class="info-value time">{{ item.updateTime || '-' }}</td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="i in 13" :key="i-1">
              <td class="info-label">Q{{ i-1 }}</td>
              <td class="info-value price">-</td>
              <td class="info-value price">-</td>
              <td class="info-value price">-</td>
              <td class="info-value price">-</td>
              <td class="info-value time">-</td>
            </tr>
          </template>
        </tbody>
      </table>
      <div v-if="lastUpdateTime" class="update-time">
        最后更新: {{ lastUpdateTime }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'QualityInfo',
  props: {
    serverType: {
      type: Number,
      required: true,
      validator: value => !isNaN(value)
    },
    productId: {
      type: Number,
      required: true,
      validator: value => !isNaN(value)
    }
  },
  data() {
    return {
      qualityData: [],
      loading: false,
      error: null,
      lastUpdateTime: null,
      refreshInterval: null
    }
  },
  methods: {
    formatPrice(price) {
      if (price === null || price === undefined) return '-';
      return Number(price).toFixed(3);
    },
    async fetchQualityData() {
      if (this.serverType === null || this.productId === null) {
        return;
      }

      this.loading = true;
      this.error = null;
      try {
        const response = await fetch(
          `/market/api/v1/market/quality/${this.serverType}/${this.productId}`
        );
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('API返回数据:', result);
        
        if (result.code === 0 && result.data) {
          this.qualityData = result.data;
          // 更新最后更新时间
          if (this.qualityData.length > 0) {
            const latestTime = Math.max(
              ...this.qualityData
                .map(item => new Date(item.updateTime).getTime())
                .filter(time => !isNaN(time))
            );
            this.lastUpdateTime = new Date(latestTime).toLocaleString('zh-CN');
          }
        } else {
          throw new Error(result.msg || '获取数据失败');
        }
      } catch (e) {
        this.error = `获取数据失败: ${e.message}`;
        console.error('获取品质数据失败:', e);
      } finally {
        this.loading = false;
      }
    },
    
    startAutoRefresh() {
      // 每60秒刷新一次数据
      this.refreshInterval = setInterval(() => {
        this.fetchQualityData();
      }, 60000);
    },
    
    stopAutoRefresh() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
        this.refreshInterval = null;
      }
    }
  },
  mounted() {
    console.log('QualityInfo组件已挂载');
    this.fetchQualityData();
    this.startAutoRefresh();
  },
  beforeUnmount() {
    this.stopAutoRefresh();
  },
  watch: {
    serverType: {
      handler() {
        this.fetchQualityData();
      }
    },
    productId: {
      handler() {
        this.fetchQualityData();
      }
    }
  }
}
</script>

<style scoped>
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

.info-table {
  width: 100%;
  border-collapse: collapse;
  background-color: #fff;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 10px;
  border: 1px solid #ebeef5;
}

.info-table th,
.info-table td {
  padding: 8px;
  border: 1px solid #ebeef5;
  text-align: center;
}

.info-table .info-header {
  color: #333;
  font-size: 12px;
  background-color: #f8f9fa;
  border: 1px solid #ebeef5;
  font-weight: bold;
}

.info-table .info-label {
  background-color: #f8f9fa;
  color: #666;
  font-size: 12px;
  border: 1px solid #ebeef5;
}

.info-table .info-value {
  color: #333;
  font-size: 12px;
  border: 1px solid #ebeef5;
}

.info-table .info-value.price {
  font-family: Monaco, monospace;
  color: #45b97c;
  border: 1px solid #ebeef5;
  text-align: right;
  padding-right: 12px;
}

.info-table .info-value.time {
  font-family: Monaco, monospace;
  color: #666;
  font-size: 11px;
  border: 1px solid #ebeef5;
}

.info-table tbody tr:hover {
  background-color: #f5f7fa;
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
</style> 