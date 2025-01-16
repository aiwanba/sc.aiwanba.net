// @ts-nocheck
<template>
  <div class="detail-section">
    <div class="section-header">价格信息</div>
    <div class="section-content">
      <!-- 图表控制器 -->
      <div class="chart-controls">
        <!-- 品质等级选择 -->
        <div class="quality-selector">
          <button 
            v-for="q in qualities" 
            :key="q.value"
            :class="[
              'quality-btn', 
              { 
                'active': currentQuality === q.value,
                'disabled': q.value > 0 && !q.isActivated
              }
            ]"
            @click="handleQualityClick(q)"
          >
            {{ q.label }}
          </button>
        </div>
        <!-- 时间周期选择 -->
        <div class="time-selector">
          <button 
            v-for="period in timePeriods" 
            :key="period.value"
            :class="[
              'time-btn', 
              { 
                'active': currentPeriod === period.value,
                'disabled': period.value !== '1d' && !period.isActivated
              }
            ]"
            @click="handlePeriodClick(period)"
          >
            {{ period.label }}
          </button>
        </div>
      </div>
      <!-- 图表容器 -->
      <div class="price-section">
        <div ref="priceChartContainer" class="chart"></div>
      </div>
      <div class="volume-section">
        <div ref="volumeChartContainer" class="chart"></div>
      </div>
    </div>
  </div>
</template>

<script>
import { createChart } from 'lightweight-charts';

export default {
  name: 'PriceChart',
  props: {
    serverType: {
      type: Number,
      required: true
    },
    productId: {
      type: Number,
      required: true
    },
    quality: {
      type: Number,
      default: 0
    },
    period: {
      type: String,
      default: '1d'
    }
  },
  data() {
    return {
      priceChart: null,
      volumeChart: null,
      priceSeries: null,
      volumeSeries: null,
      currentQuality: 0,
      currentPeriod: '1d',
      // 保留原有的数据结构
      qualities: Array.from({ length: 13 }, (_, i) => ({
        label: `Q${i}`,
        value: i,
        isActivated: i === 0
      })),
      timePeriods: [
        { label: '1小时', value: '1h', isActivated: false },
        { label: '1天', value: '1d', isActivated: true },
        { label: '1月', value: '1m', isActivated: false }
      ]
    }
  },
  watch: {
    quality: {
      handler(newVal) {
        this.currentQuality = newVal;
        this.updateCharts();
      },
      immediate: true
    },
    period: {
      handler(newVal) {
        this.currentPeriod = newVal;
        this.updateCharts();
      },
      immediate: true
    },
    serverType: {
      handler() {
        this.updateCharts();
      }
    },
    productId: {
      handler() {
        this.updateCharts();
      }
    }
  },
  methods: {
    async fetchHistoryData() {
      try {
        const response = await fetch(
          `/market/api/v1/market/history/${this.serverType}/${this.productId}/${this.currentQuality}?period=${this.currentPeriod}`,
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

        const result = await response.json();
        if (result.code === 0) {
          return result.data;
        } else {
          throw new Error(result.message || '获取数据失败');
        }
      } catch (err) {
        console.error('Error fetching history data:', err);
        return [];
      }
    },

    handleQualityClick(quality) {
      if (quality.value === 0 || quality.isActivated) {
        this.currentQuality = quality.value;
        this.updateCharts();
      } else {
        quality.isActivated = true;
        this.currentQuality = quality.value;
        this.updateCharts();
      }
    },

    handlePeriodClick(period) {
      if (period.value === '1d' || period.isActivated) {
        this.currentPeriod = period.value;
        this.updateCharts();
      } else {
        period.isActivated = true;
        this.currentPeriod = period.value;
        this.updateCharts();
      }
    },

    async updateCharts() {
      try {
        const data = await this.fetchHistoryData();
        
        // 数据预处理：按时间排序并去重
        const uniqueData = new Map();
        data.forEach(item => {
          const time = Math.floor(item.time / 1000); // 转换为秒
          if (!uniqueData.has(time) || item.time > uniqueData.get(time).time) {
            uniqueData.set(time, {
              time: time,
              value: item.price,
              volume: item.volume
            });
          }
        });

        // 转换为数组并排序
        const formattedData = Array.from(uniqueData.values())
          .sort((a, b) => a.time - b.time);

        // 更新价格图表
        this.priceSeries.setData(formattedData.map(item => ({
          time: item.time,
          value: item.value
        })));

        // 更新成交量图表
        this.volumeSeries.setData(formattedData.map(item => ({
          time: item.time,
          value: item.volume
        })));

        // 同步两个图表的时间轴
        this.priceChart.timeScale().fitContent();
        this.volumeChart.timeScale().fitContent();

      } catch (err) {
        console.error('图表数据更新错误:', err);
      }
    },

    initCharts() {
      // 初始化价格图表
      this.priceChart = createChart(this.$refs.priceChartContainer, {
        width: this.$refs.priceChartContainer.clientWidth,
        height: 300,
        layout: {
          backgroundColor: '#ffffff',
          textColor: '#333',
        },
        grid: {
          vertLines: { color: '#f0f0f0' },
          horzLines: { color: '#f0f0f0' },
        },
        crosshair: {
          mode: 1,
          vertLine: {
            width: 1,
            color: '#999',
            style: 2,
          },
          horzLine: {
            width: 1,
            color: '#999',
            style: 2,
          }
        },
        timeScale: {
          borderColor: '#ddd',
          timeVisible: true,
          secondsVisible: false
        },
        rightPriceScale: {
          borderColor: '#ddd',
        }
      });

      // 初始化成交量图表
      this.volumeChart = createChart(this.$refs.volumeChartContainer, {
        width: this.$refs.volumeChartContainer.clientWidth,
        height: 200,
        layout: {
          backgroundColor: '#ffffff',
          textColor: '#333',
        },
        grid: {
          vertLines: { color: '#f0f0f0' },
          horzLines: { color: '#f0f0f0' },
        },
        timeScale: {
          borderColor: '#ddd',
          timeVisible: true,
          secondsVisible: false
        },
        rightPriceScale: {
          borderColor: '#ddd',
        }
      });

      // 添加数据系列
      this.priceSeries = this.priceChart.addLineSeries({
        color: '#ff7f50',
        lineWidth: 2,
        crosshairMarkerVisible: true,
        priceFormat: {
          type: 'price',
          precision: 3,
          minMove: 0.001,
        },
      });

      this.volumeSeries = this.volumeChart.addHistogramSeries({
        color: '#808080',
        priceFormat: {
          type: 'volume',
        },
      });

      this.updateCharts();
    },

    handleResize() {
      if (this.priceChart && this.volumeChart) {
        this.priceChart.resize(
          this.$refs.priceChartContainer.clientWidth,
          this.$refs.priceChartContainer.clientHeight
        );
        this.volumeChart.resize(
          this.$refs.volumeChartContainer.clientWidth,
          this.$refs.volumeChartContainer.clientHeight
        );
      }
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.initCharts();
      window.addEventListener('resize', this.handleResize);
    });
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize);
    if (this.priceChart) {
      this.priceChart.remove();
    }
    if (this.volumeChart) {
      this.volumeChart.remove();
    }
  }
}
</script>

<style scoped>
.detail-section {
  padding: 12px;
  background-color: #fff;
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

.price-section,
.volume-section {
  margin-bottom: 20px;
}

.chart {
  width: 100%;
  height: 100%;
  min-height: 200px;
}

/* 添加图表控制器样式 */
.chart-controls {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.quality-selector,
.time-selector {
  display: flex;
  gap: 5px;
}

.quality-btn,
.time-btn {
  padding: 4px 8px;
  border: 1px solid #ddd;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  color: #333;
}

.quality-btn.active,
.time-btn.active {
  background: #45b97c;
  color: #fff;
  border-color: #45b97c;
}

.quality-btn.disabled,
.time-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style> 