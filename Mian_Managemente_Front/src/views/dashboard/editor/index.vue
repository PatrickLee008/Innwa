<template>
  <div class="dashboard-editor-container">

    <el-row>
      <el-date-picker v-model="start_time" placeholder="Start Date" />
      <el-date-picker v-model="end_time" placeholder="End Date" />
      <el-button type="primary" @click="getReport">GO</el-button>
    </el-row>

    <panel-group ref="child" />
  </div>
</template>

<script>
import PanelGroup from './components/PanelGroup'
import { dateToString2 } from '@/utils/date-format'

export default {
  name: 'DashboardAdmin',
  components: {
    PanelGroup
  },
  data() {
    return {
      start_time: '',
      end_time: ''
    }
  },
  methods: {
    getReport() {
      var para = {}

      if (this.start_time) {
        para.start_time = dateToString2(this.start_time)
      }
      if (this.end_time) {
        para.end_time = dateToString2(this.end_time)
      }

      this.$refs.child.getAgentReport(para)
    }
  },
  mounted(){
    this.getReport();
  }
}
</script>

<style lang="scss" scoped>
.dashboard-editor-container {
  padding: 32px;
  background-color: rgb(240, 242, 245);
  position: relative;

  .chart-wrapper {
    background: #fff;
    padding: 16px 16px 0;
    margin-bottom: 32px;
  }
}

@media (max-width: 1024px) {
  .chart-wrapper {
    padding: 8px;
  }
}
</style>
