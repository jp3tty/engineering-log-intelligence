<template>
  <div class="chart-placeholder">
    <div class="placeholder-content">
      <h4>Bar Chart</h4>
      <p>Chart data: {{ data ? 'Loaded' : 'Loading...' }}</p>
      <div class="mock-chart">
        <div class="bar" style="height: 60%"></div>
        <div class="bar" style="height: 25%"></div>
        <div class="bar" style="height: 10%"></div>
        <div class="bar" style="height: 4%"></div>
        <div class="bar" style="height: 1%"></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BarChart',
  props: {
    data: {
      type: Object,
      required: true
    },
    options: {
      type: Object,
      default: () => ({})
    }
  }
}
</script>

<style scoped>
.chart-placeholder {
  height: 300px;
  width: 100%;
  border: 2px dashed #e5e7eb;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f9fafb;
}

.placeholder-content {
  text-align: center;
  color: #6b7280;
}

.placeholder-content h4 {
  margin: 0 0 8px 0;
  color: #374151;
}

.placeholder-content p {
  margin: 0 0 16px 0;
  font-size: 14px;
}

.mock-chart {
  display: flex;
  align-items: end;
  justify-content: center;
  gap: 8px;
  height: 100px;
}

.bar {
  width: 20px;
  background: linear-gradient(to top, #3b82f6, #60a5fa);
  border-radius: 4px 4px 0 0;
  min-height: 4px;
}
</style>
