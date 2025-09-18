<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.key_word"
        placeholder="Key Word"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-date-picker v-model="startTime" type="date" placeholder="Start" />
      <el-date-picker v-model="endTime" type="date" placeholder="End" />

      <el-button
        v-waves
        class="filter-item"
        type="primary"
        icon="el-icon-search"
        @click="handleFilter"
      >Search</el-button>
      <span>Total Bet Amount:{{ betTotal }}</span>
      <span>Total Profit:{{ benefit }}</span>
      <span>Total Bonus:{{ bonus }}</span>
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
      <el-table-column label="Serial Number" prop="TRAN_ID" align="center" />
      <el-table-column label="Match Number" prop="MATCH_ID" align="center" />
      <el-table-column label="UserId" prop="USER_ID" align="center" />
      <el-table-column label="Nickname" prop="USER_NICK_NAME" align="center" />
      <el-table-column label="Bet Amount" prop="TRAN_MONEY" align="center" />
      <el-table-column label="Settle Type" prop="PROFIT_TYPE" align="center">
        <template slot-scope="row">
          <span>{{ row.PROFIT_TYPE==="1"?"Profit":"Match Settlement" }}</span>
        </template>
      </el-table-column>
      <el-table-column label="AgentId" prop="AGENT_ID" align="center" />
      <el-table-column label="Agent Name" prop="AGENT_NAME" align="center" />
      <el-table-column label="Odds" prop="AGENT_PROFIT_BL" align="center" />
      <el-table-column
        label="Agent Profit/Platform Commission"
        prop="AGENT_PROFIT_MONEY"
        align="center"
      />
      <el-table-column label="Transaction Content" prop="TRAN_CONTENT" align="center" />
      <el-table-column label="Order Type" prop="ORDER_TYPE" align="center">
        <template slot-scope="{row}">
          <span>{{ orderType[row.ORDER_TYPE] }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Result" prop="IS_WIN" align="center">
        <template slot-scope="{row}">
          <span>{{ row.IS_WIN==="0"?"Lose":"Win" }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Bonus" prop="BONUS" align="center" />
      <el-table-column label="Settle Time" prop="CREATE_TIME" align="center" />
    </el-table>

    <pagination
      v-show="total>0"
      :total="total"
      :page-sizes="[20,50,99]"
      :page-size="99"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="getList"
    />
  </div>
</template>

<script>
import waves from '@/directive/waves' // waves directive
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import { getSettlementList } from '@/api/financial'

export default {
  name: 'OrderList',
  components: { Pagination },
  directives: { waves },
  data() {
    return {
      startTime: '',
      endTime: '',
      nickName: '',
      betTotal: 0,
      bonus: 0,
      benefit: 0,
      list: [],
      tableKey: 0,
      total: 0,
      orderType: ['', 'B_Body', 'B_Goal', 'M_Body', 'M_Goal'],
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
      getSettlementList(this.listQuery).then(response => {
        this.list = response.items
        this.total = response.total
        this.bonus = response.bonus
        this.betTotal = response.total_bet
        this.benefit = response.benefit
        setTimeout(() => {
          this.listLoading = false
        }, 1.5 * 1000)
      })
    },
    handleFilter: function() {
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
</style>
