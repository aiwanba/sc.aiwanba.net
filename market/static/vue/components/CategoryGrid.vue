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

    
    <div class="sub-nav">
      <div class="nav-section">
        <div class="nav-item active">市场</div>
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
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="grid-content">
      <div v-for="group in GROUP_ORDER" :key="group" class="product-group">
        <div class="group-header">{{ group }}</div>
        <div class="resources-grid">
          <router-link 
            v-for="id in PRODUCT_GROUPS[group]" 
            :key="id"
            :to="`/market/${serverType}/${id}`"
            class="resource-item">
            {{ PRODUCT_TYPES[id] }}
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
const PRODUCT_TYPES = {
  1: "电力",
  2: "水",
  3: "苹果",
  4: "橘子",
  5: "葡萄",
  6: "谷物",
  7: "牛排",
  8: "香肠",
  9: "鸡蛋",
  10: "原油",
  11: "汽油",
  12: "柴油",
  13: "运输单位",
  14: "矿物",
  15: "铝土矿",
  16: "硅材",
  17: "化合物",
  18: "铝材",
  19: "塑料",
  20: "处理器",
  21: "电子元件",
  22: "电池",
  23: "显示屏",
  24: "智能手机",
  25: "平板电脑",
  26: "笔记本电脑",
  27: "显示器",
  28: "电视机",
  29: "作物研究",
  30: "能源研究",
  31: "采矿研究",
  32: "电器研究",
  33: "畜牧研究",
  34: "化学研究",
  35: "软件",
  40: "棉花",
  41: "棉布",
  42: "铁矿石",
  43: "钢材",
  44: "沙子",
  45: "玻璃",
  46: "皮革",
  47: "车载电脑",
  48: "电动马达",
  49: "豪华车内饰",
  50: "基本内饰",
  51: "车身",
  52: "内燃机",
  53: "经济电动车",
  54: "豪华电动车",
  55: "经济燃油车",
  56: "豪华燃油车",
  57: "卡车",
  58: "汽车研究",
  59: "时装研究",
  60: "内衣",
  61: "手套",
  62: "裙子",
  63: "高跟鞋",
  64: "手袋",
  65: "运动鞋",
  66: "种子",
  67: "圣诞爆竹",
  68: "金矿石",
  69: "金条",
  70: "名牌手表",
  71: "项链",
  72: "甘蔗",
  73: "乙醇",
  74: "甲烷",
  75: "碳纤维",
  76: "碳纤复合材",
  77: "机身",
  78: "机翼",
  79: "精密电子元件",
  80: "飞行计算机",
  81: "座舱",
  82: "姿态控制器",
  83: "火箭燃料",
  84: "燃料储罐",
  85: "固体燃料助推器",
  86: "火箭发动机",
  87: "隔热板",
  88: "离子推进器",
  89: "喷气发动机",
  98: "无人机",
  100: "航空航天研究",
  101: "钢筋混凝土",
  102: "砖块",
  103: "水泥",
  104: "黏土",
  105: "石灰石",
  106: "木材",
  107: "钢筋",
  108: "木板",
  109: "窗户",
  110: "工具",
  111: "建筑预构件",
  112: "推土机",
  113: "材料研究",
  114: "机器人",
  115: "牛",
  116: "猪",
  117: "牛奶",
  118: "咖啡豆",
  119: "咖啡粉",
  120: "蔬菜",
  121: "面包",
  122: "芝士",
  123: "苹果派",
  124: "橙汁",
  125: "苹果汁",
  126: "姜汁汽水",
  127: "披萨",
  128: "面条",
  129: "汉堡包",
  130: "千层面",
  131: "肉丸",
  132: "混合果汁",
  133: "面粉",
  134: "黄油",
  135: "糖",
  136: "可可",
  137: "面团",
  138: "酱汁",
  139: "动物饲料",
  140: "巧克力",
  141: "植物油",
  142: "沙拉",
  143: "咖喱角",
  144: "圣诞装饰品",
  145: "食谱",
  146: "南瓜",
  147: "杰克灯笼",
  148: "女巫服",
  149: "南瓜汤",
  150: "树"
};

const PRODUCT_GROUPS = {
    '农业': [66, 3, 4, 5, 6, 72, 40, 115, 116, 118, 136, 120, 139],
    '食品加工业': [137, 138, 7, 8, 9, 117, 119, 133, 121, 123, 124, 125, 126, 127, 128, 134, 122, 140, 135, 129, 130, 131, 132, 141, 142, 143, 149],
    '建设': [106, 101, 102, 103, 104, 105, 107, 108, 109, 110, 111],
    '时装业': [41, 46, 60, 61, 62, 63, 64, 65, 70, 71],
    '能源行业': [1, 10, 11, 12, 73, 74, 83],
    '电子产品制造业': [20, 21, 22, 23, 24, 25, 26, 27, 28, 79, 98, 114] ,
    '汽车制造业': [47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 112] ,
    '航空航天制造业': [77, 78, 80, 81, 82, 84, 85, 86, 87, 88, 89]  ,
    '原材料加工业': [2, 13, 14, 15, 16, 17, 18, 19, 42, 43, 44, 45, 68, 69, 75, 76] ,
    '科研行业': [29, 30, 31, 32, 33, 34, 35, 58, 59, 100, 113, 145],
    '季节性': [146, 67, 144, 147, 148, 150]
};

const GROUP_ORDER = [
  '农业',
  '食品加工业',
  '建设',
  '时装业',
  '能源行业',
  '电子产品制造业',
  '汽车制造业',
  '航空航天制造业',
  '原材料加工业',
  '科研行业',
  '季节性'
];

export default {
  name: 'CategoryGrid',
  data() {
    return {
      serverType: parseInt(localStorage.getItem('serverType') || '0'),
      currentGroup: null,
      GROUP_ORDER,
      PRODUCT_GROUPS,
      PRODUCT_TYPES
    }
  },
  computed: {
    products() {
      if (!this.currentGroup) {
        return Object.entries(this.PRODUCT_TYPES).map(([id, name]) => ({
          id: parseInt(id),
          name
        }));
      }
      const groupIds = this.PRODUCT_GROUPS[this.currentGroup] || [];
      return groupIds.map(id => ({
        id,
        name: this.PRODUCT_TYPES[id]
      }));
    }
  },
  methods: {
    switchServer(type) {
      this.serverType = type;
      localStorage.setItem('serverType', type.toString());
    },
    selectProduct(product) {
      console.log('Selected product:', product);
    },
    switchGroup(group) {
      this.currentGroup = this.currentGroup === group ? null : group;
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

.nav-arrow {
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 24px 0 24px 24px;
  border-color: transparent transparent transparent #f0f0f0;
  margin-right: 20px;
}

/* 主内容区 */
.grid-content {
  padding: 116px 20px 20px;
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.product-group {
  margin: 0;
  background-color: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.group-header {
  background-color: #333;
  color: #fff;
  padding: 8px 12px;
  font-size: 16px;
  font-weight: bold;
  border-radius: 4px;
  margin-bottom: 12px;
}

.resources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
  padding: 0;
}

.resource-item {
  background-color: #45b97c;
  color: #fff;
  padding: 10px;
  text-align: center;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: 14px;
  text-decoration: none;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  word-break: break-word;
}

.resource-item:hover {
  background-color: #3da06b;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* 响应式布局 */
@media (max-width: 1440px) {
  .grid-content {
    padding: 116px 15px 15px;
  }
  
  .resources-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 10px;
  }
  
  .product-group {
    padding: 14px;
  }
}

@media (max-width: 1200px) {
  .grid-content {
    padding: 106px 12px 12px;
  }

  .resources-grid {
    grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
    gap: 8px;
  }
  
  .product-group {
    padding: 12px;
  }
  
  .group-header {
    font-size: 15px;
    padding: 7px 10px;
  }
  
  .resource-item {
    font-size: 13px;
    padding: 8px;
  }
}

@media (max-width: 768px) {
  .grid-content {
    padding: 96px 10px 10px;
  }

  .resources-grid {
    grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
    gap: 6px;
  }
  
  .product-group {
    padding: 10px;
  }
  
  .group-header {
    font-size: 14px;
    padding: 6px 8px;
    margin-bottom: 10px;
  }
  
  .resource-item {
    font-size: 12px;
    padding: 6px;
    min-height: 36px;
  }
}

@media (max-width: 480px) {
  .grid-content {
    padding: 96px 8px 8px;
  }

  .resources-grid {
    grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
    gap: 5px;
  }
  
  .product-group {
    padding: 8px;
  }
  
  .group-header {
    font-size: 13px;
    padding: 5px 7px;
    margin-bottom: 8px;
  }
  
  .resource-item {
    font-size: 11px;
    padding: 5px;
    min-height: 32px;
  }
}

/* 动画效果 */
.product-group {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.menu-icon {
  width: 24px;
  height: 24px;
  display: block;
}

.nav-btn:hover .menu-icon {
  opacity: 0.8;
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
</style> 