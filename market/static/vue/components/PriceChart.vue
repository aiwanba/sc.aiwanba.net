// @ts-nocheck
<template>
  <div class="detail-section">
    <div class="section-header">商品价格信息</div>
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
      <div ref="priceChart" class="price-chart"></div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

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
    }
  },
  data() {
    return {
      currentPeriod: '1d',
      currentQuality: 0,
      chart: null,
      qualities: Array.from({ length: 13 }, (_, i) => ({
        label: `Q${i}`,
        value: i,
        isActivated: i === 0
      })),
      timePeriods: [
        { label: '1小时', value: '1h', isActivated: false },
        { label: '1天', value: '1d', isActivated: true },
        { label: '1个月', value: '1m', isActivated: false }
      ]
    }
  },
  methods: {
    formatPrice(price) {
      if (!price || price === '-') return '-';
      return new Intl.NumberFormat('zh-CN', {
        minimumFractionDigits: 3,
        maximumFractionDigits: 3
      }).format(price);
    },
    initChart() {
      if (this.chart) {
        this.chart.dispose();
      }
      this.chart = echarts.init(this.$refs.priceChart);
      this.updateChart();
    },
    async updateChart() {
      try {
        const data = await this.fetchHistoryData();
        
        const formattedData = data.map(item => ({
          time: item.time,
          price: parseFloat(item.price),
          volume: item.volume
        })).filter(item => (
          item.time > 0 &&
          !isNaN(item.price) &&
          !isNaN(item.volume) &&
          item.price >= 0 &&
          item.volume >= 0
        ));

        const option = {
          backgroundColor: '#fff',
          animation: false,
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'cross',
              snap: true,
              animation: false,
              crossStyle: {
                color: '#999',
                width: 1,
                type: 'dashed'
              },
              label: {
                show: true,
                backgroundColor: '#505765',
                color: '#fff',
                formatter: function (params) {
                  if (params.axisDimension === 'x') {
                    const date = new Date(params.value);
                    return date.toLocaleString('zh-CN', { 
                      hour: '2-digit', 
                      minute: '2-digit',
                      second: '2-digit'
                    });
                  }
                  if (params.axisDimension === 'y') {
                    if (params.axisIndex === 0) {
                      return params.value.toFixed(3);
                    }
                    if (params.axisIndex === 1) {
                      return Math.round(params.value).toLocaleString();
                    }
                  }
                  return '';
                }
              }
            }
          },
          grid: [{
            left: 80,
            right: 60,
            top: 40,
            height: '45%'
          }, {
            left: 80,
            right: 60,
            top: '60%',
            height: '30%'
          }],
          xAxis: [
            {
              type: 'time',
              boundaryGap: false,
              axisLine: { 
                show: true,
                lineStyle: { 
                  color: '#ddd',
                  width: 1
                }
              },
              splitLine: {
                show: true,
                lineStyle: {
                  color: '#f5f5f5',
                  width: 1,
                  type: 'solid'
                }
              },
              axisLabel: {
                show: true,
                color: '#999',
                fontSize: 11,
                formatter: (value) => {
                  const date = new Date(value);
                  if (this.currentPeriod === '1h') {
                    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
                  } else if (this.currentPeriod === '1d') {
                    return date.toLocaleString('zh-CN', { hour: '2-digit', minute: '2-digit' });
                  } else {
                    return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' });
                  }
                }
              },
              axisPointer: {
                show: true,
                type: 'line'
              }
            },
            {
              type: 'time',
              gridIndex: 1,
              boundaryGap: false,
              axisLine: { 
                show: true,
                lineStyle: { 
                  color: '#ddd',
                  width: 1
                }
              },
              axisTick: { show: false },
              axisLabel: { show: false },
              splitLine: { show: false },
              axisPointer: {
                show: true,
                type: 'line'
              }
            }
          ],
          yAxis: [
            {
              scale: true,
              position: 'left',
              splitLine: { 
                show: true,
                lineStyle: {
                  color: '#f5f5f5',
                  type: 'dashed'
                }
              },
              axisLabel: {
                color: '#999',
                fontSize: 11,
                formatter: (value) => this.formatPrice(value)
              },
              axisPointer: {
                show: true,
                type: 'line'
              }
            },
            {
              scale: true,
              gridIndex: 1,
              position: 'left',
              splitLine: { show: false },
              axisLabel: {
                color: '#999',
                fontSize: 11,
                formatter: (value) => Math.round(value).toLocaleString()
              },
              axisPointer: {
                show: true,
                type: 'line'
              }
            }
          ],
          dataZoom: [
            {
              type: 'inside',
              xAxisIndex: [0, 1],
              start: 0,
              end: 100,
              minValueSpan: 3600 * 1000 * 1,
              maxValueSpan: 3600 * 1000 * 24 * 30
            },
            {
              show: true,
              xAxisIndex: [0, 1],
              type: 'slider',
              bottom: 8,
              start: 0,
              end: 100,
              height: 20,
              borderColor: 'transparent',
              backgroundColor: '#f8f9fa',
              fillerColor: 'rgba(69, 185, 124, 0.1)',
              handleIcon: 'path://M-9.35,34.56V42m0-40V9.5m-2,0h4a2,2,0,0,1,2,2v21a2,2,0,0,1-2,2h-4a2,2,0,0,1-2-2v-21A2,2,0,0,1-11.35,9.5Z',
              handleSize: '120%',
              handleStyle: {
                color: '#45b97c',
                borderColor: '#45b97c'
              },
              textStyle: {
                color: '#999',
                fontSize: 11
              }
            }
          ],
          series: [
            {
              name: '价格',
              type: 'line',
              data: formattedData.map(item => [item.time, item.price]),
              smooth: false,
              symbol: 'circle',
              symbolSize: 6,
              showSymbol: true,
              showAllSymbol: true,
              sampling: 'none',
              connectNulls: false,
              label: {
                show: false
              },
              emphasis: {
                scale: true,
                focus: 'series',
                blurScope: 'coordinateSystem'
              },
              lineStyle: { 
                width: 2,
                color: '#ff7f50'
              },
              itemStyle: { 
                color: '#ff7f50',
                borderWidth: 2,
                borderColor: '#fff',
                shadowBlur: 4,
                shadowColor: 'rgba(0, 0, 0, 0.1)'
              }
            },
            {
              name: '成交量',
              type: 'bar',
              xAxisIndex: 1,
              yAxisIndex: 1,
              data: formattedData.map(item => [item.time, item.volume]),
              label: {
                show: false
              },
              itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: 'rgba(128, 128, 128, 0.8)' },
                  { offset: 1, color: 'rgba(128, 128, 128, 0.3)' }
                ]),
                borderRadius: [3, 3, 0, 0]
              },
              barWidth: '70%',
              barGap: '0%'
            }
          ]
        };

        this.chart.setOption(option);
      } catch (err) {
        console.error('图表数据处理错误:', err);
      }
    },
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
    handleResize() {
      if (this.chart) {
        this.chart.resize();
      }
    },
    handleQualityClick(quality) {
      if (quality.value === 0 || quality.isActivated) {
        this.currentQuality = quality.value;
        this.updateChart();
      } else {
        quality.isActivated = true;
        this.currentQuality = quality.value;
        this.updateChart();
      }
    },
    handlePeriodClick(period) {
      if (period.value === '1d' || period.isActivated) {
        this.currentPeriod = period.value;
        this.updateChart();
      } else {
        period.isActivated = true;
        this.currentPeriod = period.value;
        this.updateChart();
      }
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.initChart();
      window.addEventListener('resize', this.handleResize);
    });
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize);
    if (this.chart) {
      this.chart.dispose();
    }
  }
}
</script>

<style scoped>
/* 图表控制器样式 */
.chart-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px 16px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #ebeef5;
}

.quality-selector {
  display: flex;
  gap: 6px;
  margin-right: 24px;
  flex-wrap: wrap;
}

.quality-btn {
  padding: 6px 12px;
  border: 1px solid #e4e7ed;
  background-color: #fff;
  color: #606266;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s ease;
  font-weight: 500;
}

.quality-btn:hover:not(.disabled) {
  background-color: #f5f7fa;
  border-color: #45b97c;
  color: #45b97c;
}

.quality-btn.active {
  background-color: #45b97c;
  color: #fff;
  border-color: #45b97c;
  box-shadow: 0 2px 4px rgba(69, 185, 124, 0.2);
}

.quality-btn.disabled {
  background-color: #f5f7fa;
  color: #c0c4cc;
  cursor: not-allowed;
  border-color: #e4e7ed;
}

/* 时间周期选择器样式 */
.time-selector {
  display: flex;
  gap: 6px;
}

.time-btn {
  padding: 6px 12px;
  border: 1px solid #e4e7ed;
  background-color: #fff;
  color: #606266;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s ease;
  font-weight: 500;
}

.time-btn:hover:not(.disabled) {
  background-color: #f5f7fa;
  border-color: #45b97c;
  color: #45b97c;
}

.time-btn.active {
  background-color: #45b97c;
  color: #fff;
  border-color: #45b97c;
  box-shadow: 0 2px 4px rgba(69, 185, 124, 0.2);
}

.time-btn.disabled {
  background-color: #f5f7fa;
  color: #c0c4cc;
  cursor: not-allowed;
  border-color: #e4e7ed;
}

/* 图表容器样式 */
.price-chart {
  width: 100%;
  min-height: 585px;
  height: calc(100vh - 400px);
  max-height: 800px;
  background-color: #fff;
  border-radius: 8px;
  border: 1px solid #ebeef5;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  padding: 16px;
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

.detail-section {
  padding: 8px;
  border-bottom: 1px solid #eee;
  background-color: #fff;
}

.detail-section:last-child {
  border-bottom: none;
}
</style> 