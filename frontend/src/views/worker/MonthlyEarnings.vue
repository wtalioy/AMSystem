<template>
    <div class="monthly-earnings">
      <h2>月度收入图表</h2>
      <v-chart :option="chartOption" autoresize style="height: 400px" />
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { use } from 'echarts/core'
  import { CanvasRenderer } from 'echarts/renderers'
  import { BarChart } from 'echarts/charts'
  import { TitleComponent, TooltipComponent, GridComponent, LegendComponent } from 'echarts/components'
  import VChart from 'vue-echarts'
  import workerOrdersAPI from '@/api/workerOrders'
  
  use([CanvasRenderer, BarChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent])
  
  const chartOption = ref({})
  
  const fetchData = async () => {
    const res = await workerOrdersAPI.getEarningsHistory() // 假设返回数组形式
    const months = res.map((r) => r.month)
    const totals = res.map((r) => r.total_earnings)
  
    chartOption.value = {
      title: { text: '月收入统计图' },
      tooltip: {},
      xAxis: { type: 'category', data: months },
      yAxis: { type: 'value' },
      series: [{ name: '总收入', type: 'bar', data: totals }]
    }
  }
  
  onMounted(fetchData)
  </script>
  