<template>
  <div class="dashboard-editor-container">
    <el-row>
<!--      <el-date-picker v-model="start_time" placeholder="Start Date" />-->
<!--      <el-date-picker v-model="end_time" placeholder="End Date" />-->
      <el-date-picker
        v-model="date"
        type="daterange"
        range-separator="To"
        start-placeholder="Start Date"
        end-placeholder="End Date">
      </el-date-picker>
      <el-button type="primary" @click="getReport">GO</el-button>
    </el-row>
    <panel-group ref="child" />
  </div>
</template>

<script>
import PanelGroup from './components/PanelGroup'
import { dateToString2 } from '@/utils/date-format'

export default {
  name: 'digitReport',
  components: {
    PanelGroup
  },
  data() {
    return {
      date:'',
      start_time: '',
      end_time: ''
    }
  },
  methods: {
    getReport() {
      var para = {game_type:2,}
      if (this.date[0]) {
        para.start_time = dateToString2(this.date[0])
      }
      if (this.date[1]) {
        para.end_time = dateToString2(this.date[1])
      }

      this.$refs.child.getPlaysTotal(para)
    }
  }
}
</script>

<style lang="scss" scoped>
.list_title {
  margin-left: 8px;
  color: #606266;
  font-size: 16px;
  height: 8px;
}
.dashboard-editor-container {
  padding: 32px;
  background-color: rgb(240, 242, 245);
  position: relative;

  .github-corner {
    position: absolute;
    top: 0px;
    border: 0;
    right: 0;
  }

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
