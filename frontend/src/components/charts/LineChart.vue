<template>
  <div class="chart-placeholder">
    <div class="placeholder-content">
      <h4>Line Chart</h4>
      <p>Chart data: {{ data ? 'Loaded' : 'Loading...' }}</p>
      <div class="mock-chart">
        <div class="line"></div>
        <div class="line"></div>
        <div class="line"></div>
        <div class="line"></div>
        <div class="line"></div>
        <div class="line"></div>
        <div class="line"></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LineChart',
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
  gap: 4px;
  height: 100px;
}

.line {
  width: 8px;
  height: 60px;
  background: linear-gradient(to top, #10b981, #34d399);
  border-radius: 4px;
  opacity: 0.8;
}

.line:nth-child(2) { height: 45px; }
.line:nth-child(3) { height: 70px; }
.line:nth-child(4) { height: 30px; }
.line:nth-child(5) { height: 55px; }
.line:nth-child(6) { height: 40px; }
.line:nth-child(7) { height: 65px; }
</style>