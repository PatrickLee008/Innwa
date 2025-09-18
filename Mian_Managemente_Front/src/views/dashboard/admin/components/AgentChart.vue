<template>
  <div :class="className" :style="{height:height,width:width}" />
</template>

<script>
import echarts from "echarts";
require("echarts/theme/macarons"); // echarts theme
import resize from "./mixins/resize";
import { getAgentChargeReport } from "@/api/report";
import { dateToString2 } from "@/utils/date-format";

const animationDuration = 6000;

export default {
  mixins: [resize],
  props: {
    className: {
      type: String,
      default: "chart"
    },
    width: {
      type: String,
      default: "100%"
    },
    height: {
      type: String,
      default: "300px"
    }
  },
  data() {
    return {
      chart: null,
      agentList: [],
      chargeData: []
    };
  },
  mounted() {
    this.$nextTick(() => {
      this.initChart();
    });
  },
  beforeDestroy() {
    if (!this.chart) {
      return;
    }
    this.chart.dispose();
    this.chart = null;
  },
  methods: {
    initChart() {
      var _this = this;
      var today = dateToString2(new Date());
      getAgentChargeReport({ start_time: today }).then(res => {
        if (res.code === 20000) {
          res.info.forEach(element => {
            _this.agentList.push(element.agent_name);
            _this.chargeData.push(element.agent_charge_sum);
          });
          this.chart = echarts.init(this.$el, "macarons");
          this.chart.setOption({
            title: {
              text: "Agent Charge"
            },
            tooltip: {
              trigger: "axis",
              axisPointer: {
                type: "shadow"
              }
            },
            legend: {
              data: ["Agent Charge"]
            },
            grid: {
              left: "3%",
              right: "4%",
              bottom: "3%",
              containLabel: true
            },
            xAxis: {
              type: "value",
              boundaryGap: [0, 0.01]
            },
            yAxis: {
              type: "category",
              data: _this.agentList
            },
            series: [
              {
                name: "Total Report",
                type: "bar",
                data: _this.chargeData
              }
            ]
          });
        }
      });
    }
  }
};
</script>
