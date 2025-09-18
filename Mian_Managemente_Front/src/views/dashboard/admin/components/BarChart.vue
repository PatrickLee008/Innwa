<template>
  <div :class="className" :style="{height:height,width:width}" />
</template>

<script>
import echarts from 'echarts'
require('echarts/theme/macarons') // echarts theme
import resize from './mixins/resize'
import { getToTalReport } from '@/api/report'
import { dateToString2 } from '@/utils/date-format'

export default {
  mixins: [resize],
  props: {
    className: {
      type: String,
      default: 'chart'
    },
    width: {
      type: String,
      default: '100%'
    },
    height: {
      type: String,
      default: '300px'
    }
  },
  data() {
    return {
      chart: null,
      bonus_sum: 0,
      company_benefit: 0,
      charge_sum: 0,
      withdraw_sum: 0
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.initChart()
    })
  },
  beforeDestroy() {
    if (!this.chart) {
      return
    }
    this.chart.dispose()
    this.chart = null
  },
  methods: {
    initChart() {
      var _this = this

      getToTalReport({ 'start_time': dateToString2(new Date()) }).then(res => {
        if (res.code === 20000) {
          _this.bonus_sum = res.bonus_sum
          _this.company_benefit = res.company_profit
          _this.charge_sum = res.charge_sum
          _this.withdraw_sum = res.withdraw_sum
        }
        this.chart = echarts.init(this.$el, 'macarons')

        this.chart.setOption({
          title: {
            text: 'Today Report'
          },
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow'
            }
          },
          legend: {
            data: ['Today Report']
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
          },
          xAxis: {
            type: 'value',
            boundaryGap: [0, 0.01]
          },
          yAxis: {
            type: 'category',
            data: [
              'Total Charge',
              'Total Cash',
              'Total Amount',
              'Company Benefit'
            ]
          },
          series: [
            {
              name: 'Total Report',
              type: 'bar',
              data: [
                _this.charge_sum,
                _this.withdraw_sum,
                _this.bonus_sum,
                _this.company_benefit
              ]
            }
          ]
        })
      })
    }
  }
}
</script>
