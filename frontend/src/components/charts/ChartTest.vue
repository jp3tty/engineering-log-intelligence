<template>
  <div class="chart-test-container p-6">
    <h2 class="text-2xl font-bold mb-6">Chart Components Test</h2>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Line Chart Test -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-semibold">Line Chart Test</h3>
        </div>
        <div class="card-body">
          <LineChart :data="testLineData" :options="testLineOptions" />
        </div>
      </div>

      <!-- Bar Chart Test -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-semibold">Bar Chart Test</h3>
        </div>
        <div class="card-body">
          <BarChart :data="testBarData" :options="testBarOptions" />
        </div>
      </div>

      <!-- Pie Chart Test -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-semibold">Pie Chart Test</h3>
        </div>
        <div class="card-body">
          <PieChart :data="testPieData" :options="testPieOptions" />
        </div>
      </div>

      <!-- Interactive Test -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-semibold">Interactive Test</h3>
        </div>
        <div class="card-body">
          <button 
            @click="updateTestData" 
            class="btn btn-primary mb-4"
          >
            Update Data
          </button>
          <LineChart :data="dynamicData" :options="testLineOptions" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * Chart Test Component
 * ===================
 * 
 * This component tests all our chart components to make sure they work correctly.
 * 
 * For beginners: This is a test page that helps us verify our charts are working.
 * It's like a quality check before we use the charts in the real dashboard.
 * 
 * Author: Engineering Log Intelligence Team
 * Date: September 22, 2025
 */

import { ref, onMounted } from 'vue'
import { LineChart, BarChart, PieChart } from './index'

export default {
  name: 'ChartTest',
  components: {
    LineChart,
    BarChart,
    PieChart
  },
  setup() {
    // Test data for line chart
    const testLineData = ref({
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      datasets: [{
        label: 'Test Data',
        data: [12, 19, 3, 5, 2, 3],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1
      }]
    })

    // Test data for bar chart
    const testBarData = ref({
      labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
      datasets: [{
        label: 'Test Values',
        data: [12, 19, 3, 5, 2, 3],
        backgroundColor: [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 205, 86, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(153, 102, 255, 0.8)',
          'rgba(255, 159, 64, 0.8)'
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 205, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(255, 159, 64, 1)'
        ],
        borderWidth: 1
      }]
    })

    // Test data for pie chart
    const testPieData = ref({
      labels: ['Desktop', 'Mobile', 'Tablet'],
      datasets: [{
        data: [60, 30, 10],
        backgroundColor: [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 205, 86, 0.8)'
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 205, 86, 1)'
        ],
        borderWidth: 2
      }]
    })

    // Dynamic data for interactive test
    const dynamicData = ref({
      labels: ['A', 'B', 'C', 'D', 'E'],
      datasets: [{
        label: 'Dynamic Data',
        data: [1, 2, 3, 4, 5],
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        tension: 0.1
      }]
    })

    // Chart options
    const testLineOptions = ref({
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'Test Line Chart'
        }
      }
    })

    const testBarOptions = ref({
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'Test Bar Chart'
        }
      }
    })

    const testPieOptions = ref({
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'Test Pie Chart'
        }
      }
    })

    // Function to update dynamic data
    const updateTestData = () => {
      // Generate random data
      const newData = Array.from({ length: 5 }, () => Math.floor(Math.random() * 20) + 1)
      
      dynamicData.value = {
        labels: ['A', 'B', 'C', 'D', 'E'],
        datasets: [{
          label: 'Dynamic Data',
          data: newData,
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          tension: 0.1
        }]
      }
    }

    onMounted(() => {
      console.log('Chart test component mounted')
    })

    return {
      testLineData,
      testBarData,
      testPieData,
      dynamicData,
      testLineOptions,
      testBarOptions,
      testPieOptions,
      updateTestData
    }
  }
}
</script>

<style scoped>
.chart-test-container {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
