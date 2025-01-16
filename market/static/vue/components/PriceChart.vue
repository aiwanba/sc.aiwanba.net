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
                'disabled': period.value !== '1h' && !period.isActivated
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
      default: '1h'
    }
  },
  data() {
    return {
      priceChart: null,
      volumeChart: null,
      priceSeries: null,
      volumeSeries: null,
      currentQuality: 0,
      currentPeriod: '1h',
      // 保留原有的数据结构
      qualities: Array.from({ length: 13 }, (_, i) => ({
        label: `Q${i}`,
        value: i,
        isActivated: i === 0
      })),
      timePeriods: [
        { label: '1小时', value: '1h', isActivated: true },
        { label: '1天', value: '1d', isActivated: false },
        { label: '1月', value: '1m', isActivated: false }
      ],
      productName: '电力',
    }
  },
  watch: {
    quality: {
      handler(newVal) {
        this.currentQuality = newVal;
        if (newVal === 0 || this.qualities[newVal].isActivated) {
          this.updateCharts();
        }
      },
      immediate: true
    },
    period: {
      handler(newVal) {
        this.currentPeriod = newVal;
        if (newVal === '1h' || this.timePeriods.find(p => p.value === newVal).isActivated) {
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
        // 构建 API URL
        const url = `/market/api/v1/market/history/${this.serverType}/${this.productId}/${this.currentQuality}?period=${this.currentPeriod}`;
        console.log('请求 API URL:', url);  // 添加日志

        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error(`获取数据失败: ${response.status}`);
        }

        const result = await response.json();
        console.log('API 响应数据:', result);  // 添加日志
        
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
      if (quality.value === 0) {
        this.currentQuality = quality.value;
        this.updateCharts();
      } else if (quality.isActivated) {
        this.currentQuality = quality.value;
        this.updateCharts();
      } else {
        quality.isActivated = true;
        this.currentQuality = quality.value;
        this.updateCharts();
      }
    },

    handlePeriodClick(period) {
      if (period.value === '1h') {
        this.currentPeriod = period.value;
        this.updateCharts();
      } else if (period.isActivated) {
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
        // 等待图表初始化完成
        if (!this.priceSeries || !this.volumeSeries) {
          await this.initCharts();  // 确保图表已初始化
        }

        if (!this.productId || isNaN(this.productId) || this.productId < 0) {
          this.priceSeries?.setData([]);
          this.volumeSeries?.setData([]);
          return;
        }

        const data = await this.fetchHistoryData();
        console.log('从API获取的原始数据:', data);
        
        if (!data || data.length === 0) {
          console.warn('没有获取到数据');
          this.priceSeries.setData([]);
          this.volumeSeries.setData([]);
          return;
        }

        const uniqueData = new Map();
        data.forEach(item => {
          const time = item.time;
          console.log('处理数据项:', {
            原始时间戳: item.time,
            价格: item.price,
            数量: item.volume
          });

          if (!uniqueData.has(time) || item.time > uniqueData.get(time).time) {
            uniqueData.set(time, {
              time: time,
              value: item.price,
              volume: item.volume
            });
          }
        });

        const formattedData = Array.from(uniqueData.values())
          .sort((a, b) => a.time - b.time);
        
        console.log('格式化后的数据:', formattedData);

        // 更新价格图表数据
        const priceData = formattedData.map(item => {
          const timeInSeconds = Math.floor(item.time / 1000);
          console.log('价格数据转换:', {
            原始时间戳: item.time,
            转换后时间戳: timeInSeconds,
            对应时间: new Date(timeInSeconds * 1000).toLocaleString(),
            价格: item.value
          });
          return {
            time: timeInSeconds,
            value: item.value
          };
        });

        this.priceSeries.setData(priceData);

        // 更新成交量图表数据
        const volumeData = formattedData.map((item, index) => {
          const prevItem = index > 0 ? formattedData[index - 1] : null;
          const timeInSeconds = Math.floor(item.time / 1000);
          console.log('成交量数据转换:', {
            原始时间戳: item.time,
            转换后时间戳: timeInSeconds,
            对应时间: new Date(timeInSeconds * 1000).toLocaleString(),
            成交量: item.volume,
            涨跌: prevItem ? (item.value >= prevItem.value ? '涨' : '跌') : '首条'
          });
          return {
            time: timeInSeconds,
            value: item.volume,
            color: prevItem ? (item.value >= prevItem.value ? '#26a69a' : '#ef5350') : '#808080'
          };
        });

        this.volumeSeries.setData(volumeData);

        console.log('图表数据更新完成');

        // 同步两个图表的时间轴
        this.priceChart.timeScale().fitContent();
        this.volumeChart.timeScale().fitContent();

      } catch (err) {
        console.error('图表数据更新错误:', err);
        console.error('错误堆栈:', err.stack);
      }
    },

    // 抽取公共配置
    createChartOptions(type = 'price') {
      return {
        layout: {
          backgroundColor: '#ffffff',
          textColor: '#333',
        },
        grid: {
          vertLines: { color: '#f0f0f0' },
          horzLines: { color: '#f0f0f0' },
        },
        crosshair: {
          vertLine: {
            visible: true,
            labelVisible: true,
            style: 2,
            color: '#999999',
            width: 1,
            labelBackgroundColor: '#ffffff',
            axisLabelFormatter: (param) => {
              if (param.price) {
                return {
                  text: `${Number(param.price).toFixed(3)}`,
                  fontSize: 12,
                  color: '#333'
                };
              }
              return '';
            }
          },
          horzLine: {
            visible: true,
            labelVisible: true,
            style: 2,
            color: '#999999',
            width: 1
          }
        },
        leftPriceScale: {
          visible: true,
          borderColor: '#ddd',
          entireTextOnly: true,
          scaleMargins: {
            top: 0.1,
            bottom: 0.1,
          },
          formatter: (price) => price.toFixed(3),
          borderVisible: false
        },
        rightPriceScale: {
          visible: false
        },
        timeScale: {
          visible: true,
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
            const hours = date.getHours().toString().padStart(2, '0');
            const minutes = date.getMinutes().toString().padStart(2, '0');
            return `${date.getDate()}日 ${hours}:${minutes}`;
          }
        }
      };
    },

    // 抽取系列配置
    createSeriesOptions(type = 'price', title = '') {
      const baseOptions = {
        lastValueVisible: false,
        priceScaleId: 'left',
      };

      if (type === 'price') {
        return {
          ...baseOptions,
          color: '#ff7f50',
          lineWidth: 2,
          priceFormat: {
            type: 'price',
            precision: 3,
            minMove: 0.001
          },
          crosshairMarkerVisible: true,
          // 添加基准线配置
          baseLineVisible: true,
          baseLineColor: '#f0f0f0',
          baseLineWidth: 1,
          baseLineStyle: 1  // 虚线样式
        };
      }

      return {
        ...baseOptions,
        color: '#808080',
        priceFormat: {
          type: 'volume',
          precision: 0
        }
      };
    },

    async initCharts() {
      try {
        if (!this.$refs.priceChartContainer || !this.$refs.volumeChartContainer) {
          console.warn('图表容器未找到');
          return;
        }

        // 创建价格图表
        this.priceChart = createChart(
          this.$refs.priceChartContainer, 
          {
            ...this.createChartOptions('price'),
            width: this.$refs.priceChartContainer.clientWidth,
            height: 300
          }
        );

        // 创建成交量图表
        this.volumeChart = createChart(
          this.$refs.volumeChartContainer, 
          {
            ...this.createChartOptions('volume'),
            width: this.$refs.volumeChartContainer.clientWidth,
            height: 150
          }
        );

        // 添加价格系列
        this.priceSeries = this.priceChart.addLineSeries(
          this.createSeriesOptions('price', `${this.productName} Q${this.currentQuality}`)
        );

        // 添加成交量系列
        this.volumeSeries = this.volumeChart.addHistogramSeries(
          this.createSeriesOptions('volume', '成交量')
        );

        // 设置十字准星同步
        this.setupCrosshairSync();

        // 更新数据
        await this.updateCharts();
      } catch (err) {
        console.error('图表初始化错误:', err);
      }
    },

    // 抽取十字准星同步逻辑
    setupCrosshairSync() {
      this.priceChart.subscribeCrosshairMove((param) => {
        if (this.volumeChart && param && param.point) {
          this.volumeChart.setCrosshairPosition(param.point, param.time || undefined);
        }
      });

      this.volumeChart.subscribeCrosshairMove((param) => {
        if (this.priceChart && param && param.point) {
          this.priceChart.setCrosshairPosition(param.point, param.time || undefined);
        }
      });
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

.charts-container {
  display: flex;
  flex-direction: column;
  gap: 1px;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
  height: 450px;  /* 设置固定总高度 */
}

.price-chart {
  flex: 2;
  height: 300px;  /* 固定高度 */
  background-color: #fff;
  position: relative;
  overflow: hidden;  /* 防止内容溢出 */
}

.volume-chart {
  flex: 1;
  height: 150px;  /* 固定高度 */
  background-color: #fff;
  position: relative;
  overflow: hidden;  /* 防止内容溢出 */
}

.price-chart > div,
.volume-chart > div {
  width: 100%;
  height: 100%;
}

/* 图表控制器样式 */
.chart-controls {
  display: flex;
  gap: 20px;
  margin-bottom: 12px;  /* 减小底部间距 */
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