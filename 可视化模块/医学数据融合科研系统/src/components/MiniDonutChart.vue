<template>
  <svg width="40" height="40" viewBox="0 0 40 40">
    <circle cx="20" cy="20" r="14" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="6"/>
    <circle
      cx="20" cy="20" r="14"
      fill="none"
      stroke="url(#donutGrad)"
      stroke-width="6"
      :stroke-dasharray="circumference"
      :stroke-dashoffset="circumference * (1 - (data[0] || 0) / 100)"
      stroke-linecap="round"
      transform="rotate(-90 20 20)"
    />
    <text x="20" y="24" text-anchor="middle" fill="#60a5fa" font-size="9" font-weight="bold">{{ data[0] }}%</text>
    <defs>
      <linearGradient id="donutGrad" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="#2563eb"/>
        <stop offset="100%" stop-color="#7c3aed"/>
      </linearGradient>
    </defs>
  </svg>
</template>

<script setup lang="ts">
defineProps<{ data: number[] }>()
const circumference = 2 * Math.PI * 14
</script>