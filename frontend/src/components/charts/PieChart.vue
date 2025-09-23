<template>
  <div class="chart-placeholder">
    <div class="placeholder-content">
      <h4>Pie Chart</h4>
      <p>Chart data: {{ data ? 'Loaded' : 'Loading...' }}</p>
      <div class="mock-chart">
        <div class="pie-slice" style="--rotation: 0deg; --size: 60%; background: #10b981;"></div>
        <div class="pie-slice" style="--rotation: 216deg; --size: 25%; background: #f59e0b;"></div>
        <div class="pie-slice" style="--rotation: 270deg; --size: 10%; background: #ef4444;"></div>
        <div class="pie-slice" style="--rotation: 288deg; --size: 4%; background: #6b7280;"></div>
        <div class="pie-slice" style="--rotation: 295deg; --size: 1%; background: #8b5cf6;"></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PieChart',
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
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: conic-gradient(
    #10b981 0deg 216deg,
    #f59e0b 216deg 270deg,
    #ef4444 270deg 288deg,
    #6b7280 288deg 295deg,
    #8b5cf6 295deg 360deg
  );
}
</style>