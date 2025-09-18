<template>
  <div class="app-container">
    <div class="filter-container">
      <em>关键字:</em>
      <el-input
        v-model="listQuery.key_word"
        placeholder="Key Word"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />

      <el-date-picker
        v-model="startTime"
        type="date"
        value-format="yyyy-MM-dd"
        placeholder="Start"
        class="item-margin"
      />
      <el-date-picker
        v-model="endTime"
        type="date"
        value-format="yyyy-MM-dd"
        placeholder="End"
        class="item-margin"
      />
      <el-button
        v-waves
        class="filter-item"
        type="primary"
        icon="el-icon-search"
        @click="handleFilter"
      >Search</el-button>
    </div>

    <el-table
      :key="tableKey"
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%;"
    >
      <el-table-column type="index" width="50" />
      <el-table-column label="Operator" prop="USER_ACCOUNT" width="88px" align="center" />
      <el-table-column label="Login Time" prop="LOGIN_TIME" width="188px" align="center" />
      <el-table-column label="Login IP" prop="IP" align="left" />
    </el-table>

    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="listQuery.page"
      :page-sizes="[20,50,99]"
      :page-size="99"
      :limit.sync="listQuery.limit"
      @pagination="getList"
    />
  </div>
</template>

<script>
import waves from '@/directive/waves' // waves directive
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import { getLoginLogs } from '@/api/operation-logs'

export default {
  name: 'OrderList',
  components: { Pagination },
  directives: { waves },
  data() {
    return {
      startTime: '',
      endTime: '',
      total: 0,
      list: [],
      tableKey: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 99
      }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      getLoginLogs(this.listQuery).then((response) => {
        this.list = response.items
        this.total = response.total

        setTimeout(() => {
          this.listLoading = false
        }, 1.5 * 1000)
      })
    },
    handleFilter() {
      if (this.startTime !== '') {
        this.listQuery.start_time = this.startTime
      }
      if (this.endTime !== '') {
        this.listQuery.end_time = this.endTime
      }
      this.listQuery.page = 1
      this.getList()
    }
  }
}
</script>
<style>
.dialogwidth {
  width: 80%;
}
.lb {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  justify-content: space-between;
}
.lb .el-form-item {
  display: inline-block;
  width: 500px;
  margin-left: 50px;
  margin-right: 50px;
}
.lb .el-input--medium .el-input__inner {
  max-width: 400px;
  display: inline-block;
}
.sublist {
  display: flex;
  align-items: center;
}
</style>
