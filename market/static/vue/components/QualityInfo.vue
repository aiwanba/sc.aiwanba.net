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
              <td class="info-value price">{{ item.latestPrice || '-' }}</td>
              <td class="info-value price">{{ item.lowestPrice || '-' }}</td>
              <td class="info-value price">{{ item.highestPrice || '-' }}</td>
              <td class="info-value price">{{ item.averagePrice || '-' }}</td>
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
  watch: {
    serverType: {
      handler(newVal) {
        if (newVal !== null && this.productId !== null) {
          this.fetchQualityData();
        }
      },
      immediate: true
    },
    productId: {
      handler(newVal) {
        if (newVal !== null && this.serverType !== null) {
          this.fetchQualityData();
        }
      },
      immediate: true
    }
  },
  methods: {
    async fetchQualityData() {
      if (this.serverType === null || this.productId === null) {
        return;
      }

      this.loading = true;
      this.error = null;
      try {
        const response = await fetch(
          `/market/api/v1/market/quality/${this.serverType}/${this.productId}`,
          {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            }
          }
        );

        if (!response.ok) {
          throw new Error(`获取数据失败: ${response.status}`);
        }

        const data = await response.json();
        if (data.code === 0) {
          this.qualityData = this.processQualityData(data.data);
          this.lastUpdateTime = new Date().toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
          });
        } else {
          throw new Error(data.message || '获取数据失败');
        }
      } catch (err) {
        console.error('Error details:', err);
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    },
    processQualityData(data) {
      const qualities = Array.from({ length: 13 }, (_, i) => ({
        quality: i,
        latestPrice: '-',
        lowestPrice: '-',
        highestPrice: '-',
        averagePrice: '-',
        updateTime: '-'
      }));

      data.forEach(item => {
        if (item.quality >= 0 && item.quality <= 12) {
          qualities[item.quality] = {
            quality: item.quality,
            latestPrice: this.formatPrice(item.latest_price),
            lowestPrice: this.formatPrice(item.lowest_price),
            highestPrice: this.formatPrice(item.highest_price),
            averagePrice: this.formatPrice(item.average_price),
            updateTime: this.formatTime(item.update_time)
          };
        }
      });

      return qualities;
    },
    formatPrice(price) {
      if (!price || price === '-') return '-';
      return new Intl.NumberFormat('zh-CN', {
        minimumFractionDigits: 3,
        maximumFractionDigits: 3
      }).format(price);
    },
    formatTime(time) {
      if (!time || time === '-') return '-';
      return this.getRelativeTime(new Date(time));
    },
    getRelativeTime(date) {
      const now = new Date();
      const diffInSeconds = Math.floor((now - date) / 1000);
      
      if (diffInSeconds < 60) {
        if (diffInSeconds < 10) {
          return '几秒前';
        }
        return `${Math.floor(diffInSeconds / 10) * 10}秒前`;
      }
      
      const diffInMinutes = Math.floor(diffInSeconds / 60);
      if (diffInMinutes < 60) {
        return `${diffInMinutes}分钟前`;
      }
      
      const diffInHours = Math.floor(diffInMinutes / 60);
      if (diffInHours < 24) {
        return `${diffInHours}小时前`;
      }
      
      const diffInDays = Math.floor(diffInHours / 24);
      if (diffInDays < 30) {
        return `${diffInDays}天前`;
      }
      
      return date.toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      });
    },
    startAutoRefresh() {
      this.refreshInterval = setInterval(() => {
        this.fetchQualityData();
      }, 60000);
    },
    stopAutoRefresh() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
      }
    }
  },
  mounted() {
    if (this.serverType !== null && this.productId !== null) {
      this.startAutoRefresh();
    }
  },
  beforeUnmount() {
    this.stopAutoRefresh();
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