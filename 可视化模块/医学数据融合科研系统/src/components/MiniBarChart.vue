<template>
  <svg :width="width" :height="height" :viewBox="`0 0 ${width} ${height}`" preserveAspectRatio="none">
    <defs>
      <linearGradient :id="gradId" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" :stop-color="color" stop-opacity="0.9"/>
        <stop offset="100%" :stop-color="color" stop-opacity="0.3"/>
      </linearGradient>
    </defs>
    <rect
      v-for="(val, i) in data"
      :key="i"
      :x="i * barStep + 2"
      :y="height - (val / maxVal) * (height - 4)"
      :width="barWidth"
      :height="(val / maxVal) * (height - 4)"
      :fill="`url(#${gradId})`"
      rx="2"
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
}>(), { color: '#3b82f6', width: 120, height: 40 })

const gradId = `bar-${Math.random().toString(36).slice(2)}`
const maxVal = computed(() => Math.max(...props.data, 1))
const barStep = computed(() => props.width / props.data.length)
const barWidth = computed(() => barStep.value - 3)
</script>
