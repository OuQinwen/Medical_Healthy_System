<template>
  <div>
    <div class="page-topbar">
      <h1>质控清洗</h1>
      <span class="badge badge-yellow">开发中</span>
    </div>

    <div class="page">
      <!-- Coming Soon Banner -->
      <div class="coming-soon gradient-border">
        <div class="cs-icon animate-pulse">🔧</div>
        <h3>功能开发中</h3>
        <p>质控清洗模块正在建设中，敬请期待</p>
        <div class="cs-progress">
          <div class="cs-step done"><span>✓</span> 需求分析</div>
          <div class="cs-step done"><span>✓</span> 架构设计</div>
          <div class="cs-step active"><span>⟳</span> 开发中</div>
          <div class="cs-step"><span>○</span> 测试上线</div>
        </div>
      </div>

      <!-- Preview Cards -->
      <div class="preview-title">功能预览</div>

      <div class="preview-grid">
        <div class="preview-card card" v-for="feature in previewFeatures" :key="feature.title">
          <div class="pf-icon" :style="{background: feature.color}">{{ feature.icon }}</div>
          <h4>{{ feature.title }}</h4>
          <p>{{ feature.desc }}</p>
          <span class="badge badge-purple">即将上线</span>
        </div>
      </div>

      <!-- Quality Dashboard Preview -->
      <div class="card dashboard-preview">
        <div class="section-header">
          <div class="section-icon">📊</div>
          <h2>数据质量仪表盘</h2>
        </div>
        <p class="preview-note">系统将提供实时数据质量监控，帮助您快速识别并处理数据问题。</p>
        <div class="dashboard-mock">
          <div class="mock-stat" v-for="s in mockStats" :key="s.label">
            <div class="mock-gauge">
              <svg width="60" height="60" viewBox="0 0 60 60">
                <circle cx="30" cy="30" r="24" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="6"/>
                <circle cx="30" cy="30" r="24" fill="none" :stroke="s.color" stroke-width="6"
                  stroke-dasharray="150.8" :stroke-dashoffset="150.8 * (1 - s.value/100)"
                  stroke-linecap="round" transform="rotate(-90 30 30)"/>
                <text x="30" y="34" text-anchor="middle" :fill="s.color" font-size="11" font-weight="bold">{{ s.value }}%</text>
              </svg>
            </div>
            <div class="mock-label">{{ s.label }}</div>
          </div>
        </div>
      </div>

      <!-- Anomaly Detection Preview -->
      <div class="card anomaly-preview">
        <div class="section-header">
          <div class="section-icon">⚠️</div>
          <h2>异常检测列表</h2>
        </div>
        <p class="preview-note">智能识别数据中的异常值、缺失值、逻辑错误等问题。</p>
        <div class="anomaly-mock">
          <div class="anomaly-row" v-for="row in anomalyRows" :key="row.field">
            <div class="arow-field">{{ row.field }}</div>
            <div class="arow-issue"><span class="badge" :class="row.badgeClass">{{ row.issue }}</span></div>
            <div class="arow-count">{{ row.count }}条</div>
          </div>
        </div>
      </div>

      <!-- Rules Preview -->
      <div class="card rules-preview">
        <div class="section-header">
          <div class="section-icon">⚙️</div>
          <h2>清洗规则配置</h2>
        </div>
        <p class="preview-note">灵活配置数据清洗规则，支持自动化批量处理。</p>
        <div class="rules-mock">
          <div class="rule-item" v-for="rule in mockRules" :key="rule.name">
            <div class="rule-icon">{{ rule.icon }}</div>
            <div class="rule-name">{{ rule.name }}</div>
            <div class="rule-toggle" :class="{on: rule.on}">{{ rule.on ? 'ON' : 'OFF' }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const previewFeatures = [
  { icon: '📊', title: '质量仪表盘', desc: '实时数据质量评分与分析', color: 'linear-gradient(135deg,#2563eb,#7c3aed)' },
  { icon: '🔍', title: '异常检测', desc: '智能识别数据异常与缺失', color: 'linear-gradient(135deg,#f59e0b,#ef4444)' },
  { icon: '⚙️', title: '清洗规则', desc: '自定义数据清洗策略', color: 'linear-gradient(135deg,#10b981,#06b6d4)' },
  { icon: '📋', title: '清洗报告', desc: '详细的清洗过程记录', color: 'linear-gradient(135deg,#7c3aed,#ec4899)' },
]

const mockStats = [
  { label: '完整性', value: 87, color: '#3b82f6' },
  { label: '准确性', value: 92, color: '#10b981' },
  { label: '一致性', value: 78, color: '#f59e0b' },
  { label: '时效性', value: 95, color: '#7c3aed' },
]

const anomalyRows = [
  { field: '血压值', issue: '超出范围', badgeClass: 'badge-red', count: 3 },
  { field: '年龄', issue: '缺失值', badgeClass: 'badge-yellow', count: 7 },
  { field: '诊断编码', issue: '格式错误', badgeClass: 'badge-purple', count: 2 },
  { field: '随访日期', issue: '逻辑错误', badgeClass: 'badge-yellow', count: 1 },
]

const mockRules = [
  { icon: '🔢', name: '数值范围检验', on: true },
  { icon: '📅', name: '日期格式统一', on: true },
  { icon: '❌', name: '缺失值填充', on: false },
  { icon: '🔄', name: '重复记录去除', on: true },
  { icon: '🏷️', name: '编码标准化', on: false },
]
</script>

<style scoped>
.coming-soon {
  padding: 32px 24px;
  text-align: center;
  margin-bottom: 20px;
}
.cs-icon { font-size: 48px; margin-bottom: 12px; display: block; }
.coming-soon h3 { font-size: 20px; font-weight: 700; margin-bottom: 8px; }
.coming-soon p { color: var(--text-secondary); font-size: 14px; margin-bottom: 20px; }
.cs-progress { display: flex; justify-content: center; gap: 6px; flex-wrap: wrap; }
.cs-step {
  display: flex; align-items: center; gap: 4px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  background: rgba(255,255,255,0.06);
  color: var(--text-muted);
  border: 1px solid var(--border);
}
.cs-step.done { color: var(--success); border-color: rgba(16,185,129,0.3); background: rgba(16,185,129,0.08); }
.cs-step.active { color: var(--primary-light); border-color: rgba(59,130,246,0.3); background: rgba(59,130,246,0.08); }

.preview-title { font-size: 14px; font-weight: 600; color: var(--text-secondary); margin-bottom: 12px; }
.preview-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
.preview-card { text-align: center; padding: 16px; }
.pf-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; margin: 0 auto 8px; }
.preview-card h4 { font-size: 13px; font-weight: 600; margin-bottom: 4px; }
.preview-card p { font-size: 11px; color: var(--text-secondary); margin-bottom: 8px; line-height: 1.4; }
.preview-note { font-size: 12px; color: var(--text-secondary); margin-bottom: 16px; line-height: 1.5; }

.dashboard-mock { display: flex; justify-content: space-around; padding: 8px 0; }
.mock-gauge { margin-bottom: 6px; display: flex; justify-content: center; }
.mock-label { font-size: 11px; color: var(--text-secondary); text-align: center; }

.anomaly-mock { display: flex; flex-direction: column; gap: 8px; }
.anomaly-row {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px;
  background: var(--bg-input);
  border-radius: 8px;
}
.arow-field { flex: 1; font-size: 13px; font-weight: 500; }
.arow-issue { flex: 1; }
.arow-count { font-size: 12px; color: var(--text-secondary); }

.rules-mock { display: flex; flex-direction: column; gap: 8px; }
.rule-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px;
  background: var(--bg-input);
  border-radius: 8px;
}
.rule-icon { font-size: 18px; }
.rule-name { flex: 1; font-size: 13px; }
.rule-toggle {
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  background: rgba(255,255,255,0.06);
  color: var(--text-muted);
}
.rule-toggle.on { background: rgba(16,185,129,0.15); color: #34d399; }

.dashboard-preview, .anomaly-preview, .rules-preview { margin-bottom: 16px; }
</style>