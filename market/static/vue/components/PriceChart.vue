// @ts-nocheck
<template>
  <div class="detail-section">
    <div class="section-header">价格信息</div>
    <div class="section-content">
      <!-- 图表控制器 -->
      <div class="chart-controls">
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
      <div class="charts-container">
        <div class="price-chart">
          <div ref="priceChartContainer"></div>
        </div>
        <div class="volume-chart">
          <div ref="volumeChartContainer"></div>
        </div>
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
      required: true,
      validator: value => !isNaN(value)
    },
    productId: {
      type: Number,
      required: true,
      validator: value => !isNaN(value)
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
        if (this.priceSeries && this.volumeSeries) {
          this.updateCharts();
        }
      },
      immediate: true
    },
    period: {
      handler(newVal) {
        this.currentPeriod = newVal;
        if (this.priceSeries && this.volumeSeries) {
          this.updateCharts();
        }
      },
      immediate: true
    },
    serverType: {
      handler() {
        if (this.priceSeries && this.volumeSeries) {
          this.updateCharts();
        }
      }
    },
    productId: {
      handler(newVal) {
        if (typeof newVal === 'number' && !isNaN(newVal) && this.priceSeries && this.volumeSeries) {
          this.updateCharts();
        }
      }
    }
  },
  methods: {
    async fetchHistoryData() {
      try {
        if (!this.productId || isNaN(this.productId) || this.productId < 0) {
          console.warn('无效的商品ID:', this.productId);
          return [];
        }

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
        console.error('获取历史数据错误:', err);
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
        // 检查图表是否已初始化
        if (!this.priceSeries || !this.volumeSeries) {
          console.warn('图表尚未初始化');
          return;
        }

        if (!this.productId || isNaN(this.productId) || this.productId < 0) {
          this.priceSeries.setData([]);
          this.volumeSeries.setData([]);
          return;
        }

        const data = await this.fetchHistoryData();
        
        if (!data || data.length === 0) {
          this.priceSeries.setData([]);
          this.volumeSeries.setData([]);
          return;
        }

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
        if (this.priceSeries && this.volumeSeries) {
          this.priceSeries.setData([]);
          this.volumeSeries.setData([]);
        }
      }
    },

    initCharts() {
      try {
        // 检查DOM元素是否存在
        if (!this.$refs.priceChartContainer || !this.$refs.volumeChartContainer) {
          console.warn('图表容器未找到');
          return;
        }

        const commonOptions = {
          layout: {
            backgroundColor: '#ffffff',
            textColor: '#333',
          },
          grid: {
            vertLines: { color: '#f0f0f0' },
            horzLines: { color: '#f0f0f0' },
          },
          crosshair: {
            mode: 1,  // 十字准星模式
            vertLine: {
              width: 1,
              color: '#999',
              style: 1,  // 实线
              labelVisible: true,  // 显示标签
              labelBackgroundColor: '#fff',  // 标签背景色
            },
            horzLine: {
              visible: false,  // 隐藏水平线
            }
          },
          timeScale: {
            borderColor: '#ddd',
            timeVisible: true,
            secondsVisible: false,
            rightOffset: 0,
            barSpacing: 6,
            fixLeftEdge: true,
            fixRightEdge: true,
            rightBarStaysOnScroll: true,
            tickMarkFormatter: (time) => {
              const date = new Date(time * 1000);
              return date.getHours().toString().padStart(2, '0') + ':' + 
                     date.getMinutes().toString().padStart(2, '0');
            }
          }
        };

        // 初始化价格图表
        this.priceChart = createChart(this.$refs.priceChartContainer, {
          ...commonOptions,
          width: this.$refs.priceChartContainer.clientWidth,
          height: 400,
          leftPriceScale: {
            visible: true,
            borderColor: '#ddd',
            scaleMargins: {
              top: 0.1,
              bottom: 0.1,
            }
          },
          rightPriceScale: {
            visible: false
          }
        });

        // 初始化成交量图表
        this.volumeChart = createChart(this.$refs.volumeChartContainer, {
          ...commonOptions,
          width: this.$refs.volumeChartContainer.clientWidth,
          height: 200,
          leftPriceScale: {
            visible: true,
            borderColor: '#ddd',
            scaleMargins: {
              top: 0.1,
              bottom: 0.1,
            }
          },
          rightPriceScale: {
            visible: false
          }
        });

        // 添加价格数据系列
        this.priceSeries = this.priceChart.addLineSeries({
          color: '#ff7f50',
          lineWidth: 2,
          crosshairMarkerVisible: true,
          priceFormat: {
            type: 'price',
            precision: 3,
            minMove: 0.001,
          },
          lastValueVisible: true,
          priceLineVisible: false,
          priceScaleId: 'left',
        });

        // 添加成交量数据系列
        this.volumeSeries = this.volumeChart.addHistogramSeries({
          color: '#808080',
          priceFormat: {
            type: 'volume',
            precision: 0,
          },
          lastValueVisible: true,
          priceLineVisible: false,
          priceScaleId: 'left'
        });

        // 同步两个图表的十字准星
        this.priceChart.subscribeCrosshairMove((param) => {
          if (param.point && this.volumeChart) {
            this.volumeChart.setCrosshairPosition(param.point, param.time);
          }
        });

        this.volumeChart.subscribeCrosshairMove((param) => {
          if (param.point && this.priceChart) {
            this.priceChart.setCrosshairPosition(param.point, param.time);
          }
        });

        // 初始化完成后更新数据
        this.$nextTick(() => {
          if (this.productId && !isNaN(this.productId)) {
            this.updateCharts();
          }
        });

      } catch (err) {
        console.error('图表初始化错误:', err);
      }
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

.charts-container {
  display: flex;
  flex-direction: column;
  gap: 1px;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.price-chart {
  flex: 2;
  min-height: 400px;
  background-color: #fff;
}

.volume-chart {
  flex: 1;
  min-height: 200px;
  background-color: #fff;
}

.price-chart > div,
.volume-chart > div {
  width: 100%;
  height: 100%;
}
</style> 