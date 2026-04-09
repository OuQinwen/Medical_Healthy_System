<template>
  <div>
    <div class="page-topbar">
      <h1>科研分析</h1>
      <button class="btn btn-icon">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 0 1 1.2 12.09l-4.24 4.24a10 10 0 0 1-12.1-1.2L1 17.07A10 10 0 0 1 4.93 4.93"/>
        </svg>
      </button>
    </div>

    <div class="page">
      <!-- Summary bar -->
      <div class="summary-bar">
        <div class="summary-item">
          <span class="s-val">{{ summaryData.patients }}</span>
          <span class="s-lbl">研究对象</span>
        </div>
        <div class="summary-divider"></div>
        <div class="summary-item">
          <span class="s-val">{{ summaryData.datasets }}</span>
          <span class="s-lbl">数据集</span>
        </div>
        <div class="summary-divider"></div>
        <div class="summary-item">
          <span class="s-val">{{ summaryData.reports }}</span>
          <span class="s-lbl">研究报告</span>
        </div>
        <div class="summary-divider"></div>
        <div class="summary-item">
          <span class="s-val">{{ summaryData.models }}</span>
          <span class="s-lbl">模型数</span>
        </div>
      </div>

      <!-- Feature Grid 2x2 -->
      <div class="feature-grid">
        <div
          v-for="feat in features"
          :key="feat.id"
          class="feature-card gradient-border"
          @click="activeFeat = feat.id"
          :class="{selected: activeFeat === feat.id}"
        >
          <div class="feat-top">
            <div class="feat-icon" :style="{background: feat.gradient}" v-html="feat.icon"></div>
            <h3 class="feat-title">{{ feat.title }}</h3>
          </div>
          <p class="feat-desc">{{ feat.desc }}</p>
          <div class="feat-stats">
            <span class="badge" :class="feat.badgeClass">{{ feat.stat }}</span>
          </div>
          <div class="feat-chart">
            <MiniBarChart v-if="feat.chartType === 'bar'" :data="feat.chartData || []" :color="feat.chartColor || '#3b82f6'"/>
            <MiniLineChart v-else-if="feat.chartType === 'line'" :data="feat.chartData || []" :color="feat.chartColor || '#06b6d4'"/>
            <MiniDonutChart v-else-if="feat.chartType === 'donut'" :data="feat.chartData || []"/>
          </div>
        </div>
      </div>

      <!-- Detail Panel -->
      <Transition name="collapse">
        <div v-if="activeFeat" class="card detail-panel animate-slide-up">
          <div class="detail-header">
            <div class="section-header" style="margin-bottom:0">
              <div class="section-icon" v-html="currentFeat?.icon"></div>
              <h2>{{ currentFeat?.title }}</h2>
            </div>
            <button class="btn btn-icon btn-sm" @click="activeFeat = null">✕</button>
          </div>
          <div class="divider"></div>

          <!-- Stats Analysis -->
          <template v-if="activeFeat === 'stats'">
            <div class="analysis-desc">{{ currentFeat?.longDesc }}</div>
            <div class="metrics-grid">
              <div v-for="m in statsMetrics" :key="m.name" class="metric-item">
                <div class="metric-val" :style="{color: m.color}">{{ m.val }}</div>
                <div class="metric-name">{{ m.name }}</div>
                <div class="progress-bar" style="margin-top:6px;height:4px">
                  <div class="progress-fill" :style="{width: m.pct+'%', background: m.color}"></div>
                </div>
              </div>
            </div>
          </template>

          <!-- Data Viz -->
          <template v-else-if="activeFeat === 'viz'">
            <div class="analysis-desc">{{ currentFeat?.longDesc }}</div>
            <div class="chart-type-grid">
              <div v-for="ct in chartTypes" :key="ct.name" class="chart-type-card" @click="selectedChart = ct.name" :class="{active: selectedChart === ct.name}">
                <div class="ct-icon">{{ ct.icon }}</div>
                <div class="ct-name">{{ ct.name }}</div>
              </div>
            </div>
          </template>

          <!-- Data Mining -->
          <template v-else-if="activeFeat === 'mining'">
            <div class="analysis-desc">{{ currentFeat?.longDesc }}</div>
            <div class="model-list">
              <div v-for="model in miningModels" :key="model.name" class="model-item">
                <div class="model-left">
                  <div class="model-icon">{{ model.icon }}</div>
                  <div>
                    <div class="model-name">{{ model.name }}</div>
                    <div class="model-type">{{ model.type }}</div>
                  </div>
                </div>
                <div class="model-right">
                  <div class="model-acc">{{ model.accuracy }}%</div>
                  <div class="model-label">准确率</div>
                </div>
              </div>
            </div>
          </template>

          <!-- Report Generation -->
          <template v-else-if="activeFeat === 'report'">
            <div class="analysis-desc">{{ currentFeat?.longDesc }}</div>
            <div class="template-list">
              <div v-for="tpl in reportTemplates" :key="tpl.name" class="template-item">
                <div class="tpl-icon">{{ tpl.icon }}</div>
                <div class="tpl-info">
                  <div class="tpl-name">{{ tpl.name }}</div>
                  <div class="tpl-meta">{{ tpl.meta }}</div>
                </div>
                <button class="btn btn-primary btn-sm">生成</button>
              </div>
            </div>
          </template>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import MiniBarChart from '../components/MiniBarChart.vue'
import MiniLineChart from '../components/MiniLineChart.vue'
import MiniDonutChart from '../components/MiniDonutChart.vue'

const activeFeat = ref<string|null>(null)
const selectedChart = ref('折线图')

const summaryData = { patients: 128, datasets: 24, reports: 16, models: 5 }

const features = [
  {
    id: 'stats', 
    icon: `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M2 20h20" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
      <path d="M2 2v18" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
      <rect x="4" y="12" width="3" height="6" rx="0.5" fill="white" opacity="0.9"/>
      <rect x="9" y="8" width="3" height="10" rx="0.5" fill="white" opacity="0.9"/>
      <rect x="14" y="10" width="3" height="8" rx="0.5" fill="white" opacity="0.9"/>
      <rect x="19" y="5" width="3" height="13" rx="0.5" fill="white" opacity="0.9"/>
      <path d="M5.5 10L10.5 6L15.5 8L20.5 3" stroke="white" stroke-width="1.5" stroke-linecap="round" fill="none"/>
      <path d="M20.5 3L20.5 6" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
      <path d="M20.5 3L17.5 3" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
    </svg>`, 
    title: '统计分析', 
    desc: '多维度统计检验与相关分析',
    gradient: 'linear-gradient(135deg,#1e40af 0%,#3b82f6 50%,#60a5fa 100%)',
    stat: '12项指标', 
    badgeClass: 'badge-blue',
    chartType: 'bar', 
    chartData: [65,78,45,82,90,55,70], 
    chartColor: '#3b82f6',
    longDesc: '提供描述性统计、t检验、ANOVA、卡方检验、相关分析等多种统计方法，适用于临床科研数据分析。',
  },
  {
    id: 'viz', 
    icon: `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M4 18A8 8 0 1 1 20 18" stroke="white" stroke-width="1.5" fill="none" stroke-linecap="round"/>
      <path d="M4 12h2" stroke="white" stroke-width="1" stroke-linecap="round" opacity="0.6"/>
      <path d="M6 6l1.5 1.5" stroke="white" stroke-width="1" stroke-linecap="round" opacity="0.6"/>
      <path d="M12 4v2" stroke="white" stroke-width="1" stroke-linecap="round" opacity="0.6"/>
      <path d="M18 6l-1.5 1.5" stroke="white" stroke-width="1" stroke-linecap="round" opacity="0.6"/>
      <path d="M20 12h-2" stroke="white" stroke-width="1" stroke-linecap="round" opacity="0.6"/>
      <path d="M12 12L12 7" stroke="white" stroke-width="2" stroke-linecap="round"/>
      <circle cx="12" cy="12" r="2" fill="white"/>
      <rect x="8" y="18" width="8" height="3" rx="0.5" fill="white" opacity="0.8"/>
    </svg>`, 
    title: '数据可视化', 
    desc: '多类型图表动态展示',
    gradient: 'linear-gradient(135deg,#7c3aed 0%,#a855f7 50%,#c084fc 100%)',
    stat: '8种图表', 
    badgeClass: 'badge-purple',
    chartType: 'line', 
    chartData: [30,45,60,40,70,55,80], 
    chartColor: '#06b6d4',
    longDesc: '支持折线图、柱状图、散点图、热力图、生存曲线、ROC曲线等多种可视化形式。',
  },
  {
    id: 'mining', 
    icon: `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 4L12 9" stroke="white" stroke-width="2" stroke-linecap="round"/>
      <path d="M12 9L6 14" stroke="white" stroke-width="2" stroke-linecap="round"/>
      <path d="M6 14L6 19" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
      <path d="M6 14L10 17" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
      <path d="M12 9L18 14" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-dasharray="3,2"/>
      <path d="M18 14L14 17" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-dasharray="3,2"/>
      <path d="M18 14L18 19" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-dasharray="3,2"/>
      <circle cx="12" cy="4" r="2.5" fill="white"/>
      <circle cx="12" cy="4" r="1" fill="#059669"/>
      <circle cx="12" cy="9" r="2" fill="white"/>
      <circle cx="12" cy="9" r="0.8" fill="#059669"/>
      <circle cx="6" cy="14" r="1.8" fill="white"/>
      <circle cx="6" cy="14" r="0.7" fill="#059669"/>
      <circle cx="18" cy="14" r="1.8" fill="white" opacity="0.6"/>
      <circle cx="18" cy="14" r="0.7" fill="#10b981"/>
      <circle cx="6" cy="19" r="1.2" fill="white" opacity="0.5"/>
      <circle cx="10" cy="17" r="1.2" fill="white" opacity="0.5"/>
      <circle cx="14" cy="17" r="1.2" fill="white" opacity="0.5"/>
      <circle cx="18" cy="19" r="1.2" fill="white" opacity="0.5"/>
    </svg>`, 
    title: '数据挖掘', 
    desc: 'AI模型预测与分类',
    gradient: 'linear-gradient(135deg,#059669 0%,#10b981 50%,#34d399 100%)',
    stat: '5个模型', 
    badgeClass: 'badge-green',
    chartType: 'donut', 
    chartData: [85,15],
    longDesc: '集成多种机器学习模型，支持疾病预测、风险分层、特征筛选等任务。',
  },
  {
    id: 'report', 
    icon: `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="3" width="14" height="18" rx="1.5" stroke="white" stroke-width="1.5" fill="none"/>
      <path d="M17 3v5h5" stroke="white" stroke-width="1.5" fill="none" stroke-linejoin="round"/>
      <path d="M6 9h8" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
      <path d="M6 12h6" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
      <path d="M6 15h4" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
      <circle cx="17" cy="17" r="5" fill="white" opacity="0.95"/>
      <path d="M14 17l2 2l4-4" stroke="#0891b2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
    </svg>`, 
    title: '报告生成', 
    desc: '一键生成专业科研报告',
    gradient: 'linear-gradient(135deg,#0891b2 0%,#06b6d4 50%,#22d3ee 100%)',
    stat: '6个模板', 
    badgeClass: 'badge-cyan',
    chartType: 'bar', 
    chartData: [3,5,4,6,4,5], 
    chartColor: '#0891b2',
    longDesc: '提供多种专业报告模板，自动整合分析结果，一键导出PDF/Word格式。',
  },
]

const currentFeat = computed(() => features.find(f => f.id === activeFeat.value))

const statsMetrics = [
  { name: '样本量', val: '128', pct: 80, color: '#3b82f6' },
  { name: '均值 ± SD', val: '45.2±8.3', pct: 60, color: '#7c3aed' },
  { name: 'P值', val: '0.023', pct: 40, color: '#10b981' },
  { name: '置信区间', val: '95% CI', pct: 70, color: '#06b6d4' },
]

const chartTypes = [
  { name: '折线图', icon: '📈' },
  { name: '柱状图', icon: '📊' },
  { name: '散点图', icon: '⚫' },
  { name: '热力图', icon: '🌡️' },
  { name: '生存曲线', icon: '📉' },
  { name: 'ROC曲线', icon: '🎯' },
]

const miningModels = [
  { name: '随机森林', type: '分类模型', icon: '🌲', accuracy: 91 },
  { name: 'XGBoost', type: '集成学习', icon: '⚡', accuracy: 93 },
  { name: '逻辑回归', type: '传统统计', icon: '📐', accuracy: 82 },
  { name: 'LSTM神经网络', type: '深度学习', icon: '🧠', accuracy: 88 },
  { name: 'SVM', type: '支持向量机', icon: '🎯', accuracy: 85 },
]

const reportTemplates = [
  { name: '临床研究报告', meta: '符合CONSORT标准', icon: '🏥' },
  { name: '病例对照研究', meta: '符合STROBE标准', icon: '🔬' },
  { name: '系统综述报告', meta: '符合PRISMA标准', icon: '📚' },
  { name: '生存分析报告', meta: '含KM曲线', icon: '📉' },
  { name: '多因素分析', meta: 'Cox回归结果', icon: '🔢' },
  { name: '自定义模板', meta: '灵活配置', icon: '⚙️' },
]
</script>

<style scoped>
.summary-bar {
  display: flex;
  align-items: center;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 16px;
  margin-bottom: 16px;
}
.summary-item { flex: 1; text-align: center; }
.s-val {
  display: block;
  font-size: 20px;
  font-weight: 700;
  background: var(--gradient-1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.s-lbl { font-size: 11px; color: var(--text-secondary); }
.summary-divider { width: 1px; height: 30px; background: var(--border); }

.feature-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
.feature-card {
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  border-radius: var(--radius-md);
}
.feature-card:hover { transform: translateY(-3px); }
.feature-card.selected { background: rgba(37,99,235,0.1); }
.feat-top { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.feat-icon { 
  width: 32px; 
  height: 32px; 
  border-radius: 8px; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  font-size: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}
.feat-icon svg {
  width: 100%;
  height: 100%;
}
.feat-title { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.feat-desc { font-size: 11px; color: var(--text-secondary); margin-bottom: 8px; line-height: 1.4; }
.feat-stats { margin-bottom: 8px; }
.feat-chart { height: 40px; }

.detail-panel { margin-bottom: 16px; }
.detail-header { display: flex; align-items: center; justify-content: space-between; }
.analysis-desc { font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 16px; }

.metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.metric-item { background: var(--bg-input); border-radius: 8px; padding: 12px; }
.metric-val { font-size: 18px; font-weight: 700; }
.metric-name { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }

.chart-type-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.chart-type-card {
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}
.chart-type-card:hover, .chart-type-card.active {
  border-color: var(--primary);
  background: rgba(37,99,235,0.1);
}
.ct-icon { font-size: 20px; margin-bottom: 4px; }
.ct-name { font-size: 11px; color: var(--text-secondary); }

.model-list { display: flex; flex-direction: column; gap: 8px; }
.model-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: var(--bg-input);
  border-radius: 8px;
}
.model-left { display: flex; align-items: center; gap: 10px; }
.model-icon { font-size: 22px; }
.model-name { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.model-type { font-size: 11px; color: var(--text-secondary); }
.model-right { text-align: right; }
.model-acc {
  font-size: 18px; font-weight: 700;
  background: var(--gradient-3);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.model-label { font-size: 11px; color: var(--text-muted); }

.template-list { display: flex; flex-direction: column; gap: 8px; }
.template-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-input);
  border-radius: 8px;
}
.tpl-icon { font-size: 22px; }
.tpl-info { flex: 1; }
.tpl-name { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.tpl-meta { font-size: 11px; color: var(--text-secondary); margin-top: 2px; }
</style>