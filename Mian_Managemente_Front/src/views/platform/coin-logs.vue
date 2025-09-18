<template>
  <div class="app-container">
    <div class="filter-container">
      <em>关键字:</em>
      <el-input
        v-model="listQuery.key_word"
        placeholder="Key Word"
        style="width: 200px;"
        class="filter-item"
      />

      <el-select v-model="listQuery.type" placeholder="type" clearable>
        <el-option v-for="item in AppOpType" :key="item.value" :label="item.name" :value="item.value">
        </el-option>
      </el-select>
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
      <el-table-column label="User" prop="USER_ACCOUNT" width="118px" align="center" />
      <el-table-column label="Match ID" prop="MATCH_ID" width="118px" align="center"/>
      <el-table-column label="Operate Time" prop="CREATE_TIME" width="188px" align="center"/>
      <el-table-column label="Before Change" prop="AMOUNT" :formatter="tableFormat" width="188px" align="center"/>
      <el-table-column label="Change Amount" :formatter="tableFormat" prop="change_amount" width="188px" align="center">
        <!--        <template slot-scope="{row}">-->
        <!--          <label>{{ row.BALANCE - row.AMOUNT }}</label>-->
        <!--        </template>-->
      </el-table-column>
      <el-table-column label="After Change" prop="BALANCE" :formatter="tableFormat" width="188px" align="center"/>
      <el-table-column label="Change Type" width="188px" align="center">
        <template slot-scope="{row}">
          <label>{{ type[row.TYPE] }}</label>
        </template>
      </el-table-column>
      <el-table-column label="Source Id" prop="SOURCE_ID" width="188px" align="center" />
      <el-table-column label="Description" prop="DESC" width="288px" align="center" />
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
import { getCoinLogs } from '@/api/coin-logs'
import {number_format} from "@/utils";

export default {
  name: 'OrderList',
  components: { Pagination },
  directives: { waves },
  data() {
    return {
      startTime: '',
      endTime: '',
      total: 0,
      type: ['charge', 'withdraw', 'bet', 'settlement', 'cancel'],
      list: [],
      tableKey: 0,
      listLoading: false,
      AppOpType:[
        {name:'charge' ,value: 0,},
        {name:'withdraw'  ,value:1,},
        {name:'bet'  ,value:2,},
        {name:'settle'  ,value:3,},
        // {name:'cancel'  ,value:4,},
        // {name:'reverse'  ,value:5,},
      ],
      listQuery: {
        page: 1,
        limit: 99,
        type:null,
      }
    }
  },
  created() {
    // this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      getCoinLogs(this.listQuery).then(response => {
        this.list = response.items
        this.total = response.total

        this.list.forEach(element => {})
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
    },
    tableFormat(row, column, index) {
      // console.log(row, column, index)
      let str = ''
      switch (column.property) {
        case 'change_amount':
          str = number_format(row.BALANCE - row.AMOUNT)
          break
        default:
          str = number_format(row[column.property])
          break
      }
      return str
    },
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
