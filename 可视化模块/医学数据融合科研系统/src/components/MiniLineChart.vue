<template>
  <svg :width="width" :height="height" :viewBox="`0 0 ${width} ${height}`" preserveAspectRatio="none">
    <defs>
      <linearGradient :id="gradId" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" :stop-color="color" stop-opacity="0.3"/>
        <stop offset="100%" :stop-color="color" stop-opacity="0"/>
      </linearGradient>
    </defs>
    <path :d="areaPath" :fill="`url(#${gradId})`"/>
    <path :d="linePath" :stroke="color" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    <circle
      v-for="(pt, i) in points"
      :key="i"
      :cx="pt.x"
      :cy="pt.y"
      r="2"
      :fill="color"
    />
  </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  data: number[]
  color?: string
  width?: number
  height?: number
}>(), { color: '#06b6d4', width: 120, height: 40 })

const gradId = `line-${Math.random().toString(36).slice(2)}`
const pad = 4

const points = computed(() => {
  const maxVal = Math.max(...props.data, 1)
  const step = (props.width - pad * 2) / (props.data.length - 1)
  return props.data.map((v, i) => ({
    x: pad + i * step,
    y: pad + (1 - v / maxVal) * (props.height - pad * 2),
  }))
})

const linePath = computed(() => {
  if (points.value.length < 2) return ''
  return points.value.map((p, i) => (i === 0 ? `M${p.x},${p.y}` : `L${p.x},${p.y}`)).join(' ')
})

const areaPath = computed(() => {
  if (points.value.length < 2) return ''
  const pts = points.value
  const last = pts[pts.length - 1]
  const first = pts[0]
  if (!last || !first) return ''
  return pts.map((p, i) => (i === 0 ? `M${p.x},${p.y}` : `L${p.x},${p.y}`)).join(' ')
    + ` L${last.x},${props.height} L${first.x},${props.height} Z`
})
</script>