<template>
  <nav class="bottom-nav">
    <router-link
      v-for="item in navItems"
      :key="item.path"
      :to="item.path"
      class="nav-item"
      :class="{active: isActive(item.path)}"
    >
      <div class="nav-icon-wrap">
        <component :is="item.iconComponent" class="nav-icon"/>
        <div v-if="isActive(item.path)" class="nav-indicator"></div>
      </div>
      <span class="nav-label">{{ item.label }}</span>
    </router-link>
  </nav>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { computed, defineComponent, h } from 'vue'

const route = useRoute()

function isActive(path: string) {
  return route.path.startsWith(path)
}

const DataIcon = defineComponent({ render: () => h('svg', { width: '22', height: '22', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('rect', { x: '3', y: '3', width: '18', height: '18', rx: '3' }),
  h('path', { d: 'M3 9h18M9 21V9' }),
]) })

const FollowupIcon = defineComponent({ render: () => h('svg', { width: '22', height: '22', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('path', { d: 'M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2' }),
  h('circle', { cx: '9', cy: '7', r: '4' }),
  h('path', { d: 'M23 21v-2a4 4 0 0 0-3-3.87' }),
  h('path', { d: 'M16 3.13a4 4 0 0 1 0 7.75' }),
]) })

const ResearchIcon = defineComponent({ render: () => h('svg', { width: '22', height: '22', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('polyline', { points: '22 12 18 12 15 21 9 3 6 12 2 12' }),
]) })

const ProfileIcon = defineComponent({ render: () => h('svg', { width: '22', height: '22', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('path', { d: 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2' }),
  h('circle', { cx: '12', cy: '7', r: '4' }),
]) })

const navItems = [
  { path: '/data', label: '数据', iconComponent: DataIcon },
  { path: '/visit', label: '随访', iconComponent: FollowupIcon },
  { path: '/science', label: '科研', iconComponent: ResearchIcon },
  { path: '/mine', label: '我的', iconComponent: ProfileIcon },
]
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px;
  height: 64px;
  display: flex;
  align-items: center;
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(20px);
  border-top: 1px solid var(--border);
  z-index: 100;
  padding: 0 8px;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  padding: 8px 4px;
  text-decoration: none;
  color: var(--text-muted);
  transition: color 0.2s;
  position: relative;
}

.nav-item.active { color: var(--primary-light); }

.nav-icon-wrap { position: relative; }
.nav-icon { display: block; }

.nav-indicator {
  position: absolute;
  top: -2px; right: -2px;
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--primary-light);
}

.nav-label { font-size: 10px; font-weight: 500; }

.nav-item.active .nav-label { font-weight: 600; }
</style>
