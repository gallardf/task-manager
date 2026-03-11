<template>
  <div class="stats-chart">
    <div
      v-for="(item, index) in data"
      :key="index"
      class="stat-card"
      :style="{ borderTopColor: item.color || defaultColors[index % defaultColors.length] }"
    >
      <div class="stat-value">{{ item.value }}</div>
      <div class="stat-label">{{ item.label }}</div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  data: {
    type: Array,
    default: () => []
  }
})

const defaultColors = ['#3b82f6', '#16a34a', '#f59e0b', '#dc2626', '#8b5cf6', '#06b6d4']
</script>

<style scoped>
.stats-chart {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.stat-card {
  flex: 1;
  min-width: 140px;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  border-top: 4px solid #3b82f6;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.stat-label {
  font-size: 0.85rem;
  color: #64748b;
  margin-top: 6px;
  text-transform: capitalize;
}
</style>
