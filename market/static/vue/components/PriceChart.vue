// @ts-nocheck
<template>
  <div class="detail-section">
    <div class="section-header">商品基本信息</div>
    <div class="section-content">
      <!-- 图表控制器 -->
      <div class="chart-controls">
        <div class="controls-left">
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
        </div>
        <div class="controls-right">
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

// 添加防抖函数
function debounce(fn, delay) {
  let timer = null;
  return function (...args) {
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => {
      fn.apply(this, args);
    }, delay);
  };
}

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
          const timeInSeconds = Math.floor(item.time / 1000);
          // 根据时间周期对齐时间戳
          let alignedTime = timeInSeconds;
          if (this.currentPeriod === '1d') {
            alignedTime = Math.floor(timeInSeconds / 3600) * 3600;
          } else if (this.currentPeriod === '1m') {
            alignedTime = Math.floor(timeInSeconds / 86400) * 86400;
          }

          // 如果是相同时间戳的数据，取平均值
          if (uniqueData.has(alignedTime)) {
            const existing = uniqueData.get(alignedTime);
            existing.value = (existing.value * existing.count + item.price) / (existing.count + 1);
            existing.volume += item.volume;
            existing.count += 1;
          } else {
            uniqueData.set(alignedTime, {
              time: alignedTime,
              value: item.price,
              volume: item.volume,
              count: 1
            });
          }
        });

        // 转换为数组并确保按时间升序排序
        const formattedData = Array.from(uniqueData.values())
          .sort((a, b) => a.time - b.time)
          .map(item => ({
            time: item.time,
            value: item.value,
            volume: item.volume
          }));

        // 更新价格图表数据
        const priceData = formattedData.map(item => ({
          time: item.time,
          value: item.value
        }));

        // 更新成交量图表数据
        const volumeData = formattedData.map((item, index) => {
          const prevItem = index > 0 ? formattedData[index - 1] : null;
          return {
            time: item.time,
            value: item.volume,
            color: prevItem ? (item.value >= prevItem.value ? '#26a69a' : '#ef5350') : '#808080'
          };
        });

        // 设置数据前先检查是否有重复时间戳
        const timeSet = new Set();
        const hasDuplicates = priceData.some(item => {
          if (timeSet.has(item.time)) return true;
          timeSet.add(item.time);
          return false;
        });

        if (hasDuplicates) {
          console.warn('数据中存在重复的时间戳，已进行合并处理');
        }

        this.priceSeries.setData(priceData);
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
      const baseOptions = {
        layout: {
          backgroundColor: '#ffffff',
          textColor: '#333333',
          fontSize: 11,
        },
        grid: {
          vertLines: {
            color: '#f0f0f0',
            style: 0,
            visible: true
          },
          horzLines: {
            color: '#f0f0f0',
            style: 0,
            visible: true
          }
        },
        // 移除右侧刻度
        rightPriceScale: {
          visible: false,
        },
        // 配置左侧刻度
        leftPriceScale: {
          visible: true,
          borderVisible: false,
          scaleMargins: {
            top: 0.1,
            bottom: 0.1,
          },
          ticksVisible: true,
          borderColor: '#f0f0f0',
          entireTextOnly: false,
          autoScale: true,
          alignLabels: true,
        },
        timeScale: {
          borderVisible: false,
          timeVisible: true,
          secondsVisible: false,
          tickMarkFormatter: (time) => {
            const date = new Date(time * 1000);
            // 根据不同的时间周期显示不同的格式
            if (this.currentPeriod === '1h') {
              // 1小时周期显示 HH:mm
              const hours = date.getHours().toString().padStart(2, '0');
              const minutes = date.getMinutes().toString().padStart(2, '0');
              return `${hours}:${minutes}`;
            } else if (this.currentPeriod === '1d') {
              // 1天周期显示 MM-DD HH:00
              const month = (date.getMonth() + 1).toString().padStart(2, '0');
              const day = date.getDate().toString().padStart(2, '0');
              const hours = date.getHours().toString().padStart(2, '0');
              return `${month}-${day} ${hours}:00`;
            } else {
              // 1月周期显示 MM-DD
              const month = (date.getMonth() + 1).toString().padStart(2, '0');
              const day = date.getDate().toString().padStart(2, '0');
              return `${month}-${day}`;
            }
          },
          rightOffset: 5,
          barSpacing: 3,
          minBarSpacing: 2
        }
      };

      // 价格图表配置
      if (type === 'price') {
        return {
          ...baseOptions,
          leftPriceScale: {
            ...baseOptions.leftPriceScale,
            formatter: (price) => price.toFixed(3)
          }
        };
      }

      // 成交量图表配置
      return {
        ...baseOptions,
        leftPriceScale: {
          ...baseOptions.leftPriceScale,
          formatter: (volume) => {
            if (volume >= 1000000) {
              return (volume / 1000000).toFixed(1) + 'M';
            } else if (volume >= 1000) {
              return (volume / 1000).toFixed(1) + 'K';
            }
            return volume.toString();
          }
        }
      };
    },

    // 抽取系列配置
    createSeriesOptions(type = 'price') {
      if (type === 'price') {
        return {
          color: '#ff7f50',
          lineWidth: 1,
          priceLineVisible: false,
          lastValueVisible: true,
          crosshairMarkerVisible: true,
          // 确保使用左侧刻度
          priceScaleId: 'left',
          priceFormat: {
            type: 'price',
            precision: 3,
            minMove: 0.001
          }
        };
      }

      return {
        color: (data) => data.value >= 0 ? '#26a69a' : '#ef5350',
        // 确保使用左侧刻度
        priceScaleId: 'left',
        priceFormat: {
          type: 'volume',
          formatter: (volume) => {
            if (volume >= 1000000) {
              return (volume / 1000000).toFixed(1) + 'M';
            } else if (volume >= 1000) {
              return (volume / 1000).toFixed(1) + 'K';
            }
            return volume.toString();
          }
        }
      };
    },

    async initCharts() {
      try {
        if (!this.$refs.priceChartContainer || !this.$refs.volumeChartContainer) {
          console.warn('图表容器未找到');
          return;
        }

        const containerWidth = this.$refs.priceChartContainer.clientWidth;
        const priceHeight = this.$refs.priceChartContainer.clientHeight;
        const volumeHeight = this.$refs.volumeChartContainer.clientHeight;

        // 创建价格图表
        this.priceChart = createChart(
          this.$refs.priceChartContainer, 
          {
            ...this.createChartOptions('price'),
            width: containerWidth,
            height: priceHeight
          }
        );

        // 创建成交量图表
        this.volumeChart = createChart(
          this.$refs.volumeChartContainer, 
          {
            ...this.createChartOptions('volume'),
            width: containerWidth,
            height: volumeHeight
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

    handleResize: debounce(function() {
      if (this.priceChart && this.volumeChart) {
        const containerWidth = this.$refs.priceChartContainer.clientWidth;
        const priceHeight = this.$refs.priceChartContainer.clientHeight;
        const volumeHeight = this.$refs.volumeChartContainer.clientHeight;

        this.priceChart.resize(containerWidth, priceHeight);
        this.volumeChart.resize(containerWidth, volumeHeight);
        
        // 重新适应内容
        this.priceChart.timeScale().fitContent();
        this.volumeChart.timeScale().fitContent();
      }
    }, 250), // 250ms 的防抖延迟
  },
  mounted() {
    this.$nextTick(() => {
      this.initCharts().then(() => {
        this.updateCharts();
      });
      // 添加 resize 事件监听
      window.addEventListener('resize', this.handleResize);
    });
  },
  beforeUnmount() {
    // 移除事件监听
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
  padding: 8px;
  border-bottom: 1px solid #eee;
  background-color: #fff;
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
}

.section-header {
  font-size: 12px;
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
  padding-bottom: 4px;
  border-bottom: 2px solid #45b97c;
}

.sub-section-header {
  font-size: 12px;
  padding: 8px 12px;
  color: #333;
  border-bottom: 1px solid #f0f0f0;
}

.charts-container {
  display: flex;
  flex-direction: column;
  border: none;
  border-radius: 0;
  height: calc(100vh - 300px);
  min-height: 400px;
  max-height: 600px;
  background-color: #fff;
}

.price-chart {
  flex: 7;
  height: 70%;
  border-bottom: 1px solid #f0f0f0;
}

.volume-chart {
  flex: 3;
  height: 30%;
}

.price-chart > div,
.volume-chart > div {
  width: 100%;
  height: 100% !important;
}

/* 按钮样式 */
.chart-controls {
  padding: 8px 12px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.controls-left,
.controls-right {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.quality-selector,
.time-selector {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.quality-btn,
.time-btn {
  padding: 4px 8px;
  border: 1px solid #f0f0f0;
  background: #fff;
  border-radius: 2px;
  font-size: 12px;
  color: #666;
  cursor: pointer;
}

.quality-btn:hover,
.time-btn:hover {
  background: #f8f8f8;
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

/* 添加媒体查询以适应小屏幕 */
@media screen and (max-width: 768px) {
  .chart-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .controls-left,
  .controls-right {
    justify-content: center;
  }

  .quality-btn,
  .time-btn {
    flex: 1;
    min-width: 40px;
    text-align: center;
  }
  
  .charts-container {
    height: calc(100vh - 400px);
  }
}

@media screen and (max-width: 480px) {
  .quality-selector,
  .time-selector {
    justify-content: center;
    width: 100%;
  }
  
  .charts-container {
    height: calc(100vh - 450px);
  }
}
</style> 