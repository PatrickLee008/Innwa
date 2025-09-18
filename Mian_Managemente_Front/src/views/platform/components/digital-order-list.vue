<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.key_word"
        placeholder="关键字"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-radio-group v-model="historyStatus" @change="handleFilter">
        <el-radio :label="true">Current</el-radio>
        <el-radio :label="false">History</el-radio>
      </el-radio-group>
      <em>Order Type:</em>
      <el-select v-model="ordertype" class="filter-item" placeholder>
        <el-option
          v-for="item in ordertype_option"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      <em>Bet Type:</em>
      <el-select v-model="bettype" class="filter-item" placeholder>
        <el-option
          v-for="item in bettype_option"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      <em>Mixed:</em>
      <el-select v-model="is_mix" class="filter-item" placeholder>
        <el-option
          v-for="item in is_mix_option"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      <em>Result:</em>
      <el-select v-model="is_win" class="filter-item" placeholder>
        <el-option
          v-for="item in is_win_option"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
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
      >Search
      </el-button>
      <span style="margin-right:15px;">Total Amount:{{ betTotal }}</span>
      <span>Total Bonus:{{ reword }}</span>
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
      <el-table-column type="index" width="50"/>
      <el-table-column label="Order Number" prop="ORDER_ID" align="center" width="100px"/>
      <el-table-column label="UserId" prop="USER_ID" max-width="8%" align="center"/>
      <el-table-column label="NickName" prop="USER_NAME" width="95px" align="center"/>
      <el-table-column label="Match Number" prop="MATCH_ID" width="95px" align="center"/>
      <el-table-column label="Order Desc" prop="ORDER_DESC" max-width="6%" align="center"/>
      <el-table-column label="Order Type" max-width="6%" align="center">
        <template slot-scope="{row}">
          <span>{{ OrderTypeLabel[row.ORDER_TYPE] }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Amount" prop="BET_MONEY" width="95px" align="center"/>
      <el-table-column label="Bet Type" max-width="6%" align="center">
        <template slot-scope="{row}">
          <div v-if="row.ORDER_TYPE==1 || row.ORDER_TYPE==4">
            <span v-if="row.BET_TYPE==1">Home</span>
            <span v-else>Away</span>
          </div>
          <div v-if="row.ORDER_TYPE==2 || row.ORDER_TYPE==5">
            <span v-if="row.BALL_TYPE==1">Over</span>
            <span v-else>Under</span>
          </div>
          <div v-if="row.ORDER_TYPE==6 || row.ORDER_TYPE==7">
            <span v-if="row.BET_TYPE==1">Odd</span>
            <span v-else>Even</span>
          </div>
          <div v-if="row.ORDER_TYPE==8 ||row.ORDER_TYPE==9 ">
            <span>{{row.BET_TYPE}}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="Order IP" prop="IP" width="80px" align="center"/>
      <el-table-column label="Create Time" prop="CREATE_TIME" :formatter="tableFormatter" width="95px" align="center"/>
      <el-table-column label="Update Time" prop="UPDATE_TIME" :formatter="tableFormatter" width="95px" align="center"/>
      <el-table-column label="Remark" prop="REMARK" width="80px" align="center"/>
      <el-table-column label="Status" width="50px" align="center">
        <template slot-scope="{row}">
          <span v-if="row.STATUS==1">effective</span>
          <span v-else>Valid</span>
        </template>
      </el-table-column>
<!--      <el-table-column label="Mixed" width="50px" align="center">-->
<!--        <template slot-scope="{row}">-->
<!--          <span v-if="row.IS_MIX==1">Yes</span>-->
<!--          <span v-else>No</span>-->
<!--        </template>-->
<!--      </el-table-column>-->
      <el-table-column label="Results" width="50px" align="center">
        <template slot-scope="{row}">
          <span v-if="row.IS_WIN==1">Win</span>
          <span v-if="row.IS_WIN==0">Lose</span>
          <span v-else>Not</span>
        </template>
      </el-table-column>
      <el-table-column label="Bonus" prop="BONUS" width="80px" align="center"/>
      <el-table-column label="Odds" prop="BET_ODDS" width="50px" align="center"/>
      <el-table-column label="Details" prop="MIX_DETAIL" width="80px" align="center">
        <template slot-scope="{row}">
          <el-button v-if="row.IS_MIX==1" type="info" @click="showDetails(row.ORDER_ID)">details</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total>0"
      :page-sizes="[20,50,99]"
      :page-size="99"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="getList"
    />

    <el-dialog
      :visible.sync="orderDetailsVisible"
      title="Orders Details"
      custom-class="dialogwidth"
      :modal="false"
    >
      <el-table
        :key="tableKey"
        v-loading="orderDetailsLoading"
        :data="orderDetails"
        border
        fit
        highlight-current-row
        style="width: 100%;"
      >
        <el-table-column label="#" type="index" width="50px"/>
        <el-table-column label="Order Number" prop="ORDER_ID" max-width="8%" align="center"/>
        <el-table-column label="User Id" prop="USER_ID" width="95px" align="center"/>
        <el-table-column label="Nickname" prop="USER_NAME" width="95px" align="center"/>
        <el-table-column label="Match ID" prop="MATCH_ID" max-width="6%" align="center"/>
        <el-table-column label="Order Desc" prop="ORDER_DESC" max-width="6%" align="center"/>
        <el-table-column label="Order Type" max-width="6%" align="center">
          <template slot-scope="{row}">
            <span>{{ OrderTypeLabel[row.ORDER_TYPE] }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Amount" prop="BET_MONEY" width="95px" align="center"/>
        <el-table-column label="Bet Type" prop="BET_TYPE" width="95px" align="center"/>
        <el-table-column label="Create Time" prop="CREATE_TIME" :formatter="tableFormatter" width="95px" align="center"/>
        <el-table-column label="Update Time" prop="UPDATE_TIME" :formatter="tableFormatter" width="95px" align="center"/>
        <el-table-column label="Remark" prop="REMARK" width="80px" align="center"/>
        <el-table-column label="Order Status" width="50px" align="center">
          <template slot-scope="{row}">
            <span v-if="row.STATUS==1">effective</span>
            <span v-else>invalid</span>
          </template>
        </el-table-column>
        <el-table-column label="Order Result" width="50px" align="center">
          <template slot-scope="{row}">
            <span v-if="row.IS_WIN==1">Win</span>
            <span v-if="row.IS_WIN==0">Lose</span>
          </template>
        </el-table-column>
        <el-table-column label="Bonus" prop="BONUS" width="80px" align="center"/>
        <el-table-column label="Odds" prop="BET_ODDS" width="50px" align="center"/>
      </el-table>
    </el-dialog>
  </div>
</template>

<script>
  import waves from '@/directive/waves' // waves directive
  import Pagination from '@/components/Pagination' // secondary package based on el-pagination
  import { getOrderList, getOrderHistoryList } from '@/api/order'
  import { dateToString, dateToString2 } from '@/utils/date-format'

  export default {
    name: 'DigitalOrderList',
    components: { Pagination },
    directives: { waves },
    data() {
      return {
        startTime: '',
        endTime: '',
        orderDetails: [], // 混合单详情
        orderDetailsLoading: false,
        orderDetailsVisible: false,
        historyStatus: true,
        total: 0,
        betTotal: 0,
        reword: 0,
        list: [],
        ordertype: 4,
        OrderTypeLabel: {
          1: 'B_Body',
          2: 'B_Goal',
          3: '波胆',
          4: 'M_Body',
          5: 'M_Goal',
          6: 'B_OE',
          7: 'M_OE',
          8: '2D',
          9: '3D',
        },
        ordertype_option: [
          {
            value: 4,
            label: 'All'
          },
          {
            value: 1,
            label: 'B_Body'
          },
          {
            value: 2,
            label: 'B_Goal'
          }
          // {
          //   value: 3,
          //   label: '波胆'
          // }
        ],
        bettype: 3,
        bettype_option: [
          {
            value: 3,
            label: 'All'
          },
          {
            value: 1,
            label: 'Home Win'
          },
          {
            value: 2,
            label: 'Away Win'
          }
        ],
        orderstatus: 3,
        orderstatus_option: [
          {
            value: 3,
            label: 'All'
          },
          {
            value: 1,
            label: 'Effective'
          },
          {
            value: 0,
            label: 'Valid'
          }
        ],
        is_mix: 3,
        is_mix_option: [
          {
            value: 3,
            label: 'All'
          },
          {
            value: 1,
            label: 'Yes'
          },
          {
            value: 0,
            label: 'No'
          }
        ],
        is_win: 3,
        is_win_option: [
          {
            value: 3,
            label: 'All'
          },
          {
            value: 0,
            label: 'Lose'
          },
          {
            value: 1,
            label: 'Win'
          },
          {
            value: 2,
            label: 'Not'
          }
        ],
        tableKey: 0,
        listLoading: true,
        listQuery: {
          page: 1,
          limit: 99,
          game_type:2,
          matchId: undefined
        }
      }
    },
    created() {
      this.getList()
    },
    methods: {
      getList() {
        this.listLoading = true
        this.listQuery.is_group = 1
        if (!this.historyStatus && !this.listQuery.end_time && !this.listQuery.start_time) {
          this.listQuery.start_time = this.startTime = dateToString2(new Date() - (30 * 24 * 3600 * 1000)).trim()
          this.listQuery.end_time = this.endTime = dateToString2(new Date()).trim()
        }
        (this.historyStatus ? getOrderList(this.listQuery) : getOrderHistoryList(this.listQuery)).then((response) => {
          this.listLoading = false
          this.list = response.items


          this.betTotal = response.total_bet
          this.reword = response.total_bonus
          this.total = response.total
        })
      },
      showDetails(order_id) {
        var _this = this
        var para = { order_id: order_id, is_group: 0,game_type:2,limit:1000 }
        _this.orderDetailsVisible = true;
        (_this.historyStatus ? getOrderList(para) : getOrderHistoryList(para)).then((res) => {
          _this.orderDetailsLoading = false
          if (res.code === 20000) {
            _this.orderDetails = []
            res.items.forEach((element) => {
              _this.orderDetails.push(element)
            })
          }

        })
      },
      tableFormatter(row, column, cellValue, index) {
        let str = ''
        switch (column.property) {
          case 'CREATE_TIME':
            str = this.$to_myan_time(row.CREATE_TIME)
            break
          case 'UPDATE_TIME':
            str = this.$to_myan_time(row.UPDATE_TIME)
            break
        }
        return str
      },
      handleFilter() {
        if (this.startTime !== '') {
          this.listQuery.start_time = this.startTime
        }
        if (this.endTime !== '') {
          this.listQuery.end_time = this.endTime
        }
        if (this.ordertype === 4) {
          delete this.listQuery.order_type
        } else {
          this.listQuery.order_type = this.ordertype
        }
        if (this.bettype === 3) {
          delete this.listQuery.bet_type
        } else {
          this.listQuery.bet_type = this.bettype
        }
        if (this.orderstatus === 3) {
          delete this.listQuery.status
        } else {
          this.listQuery.status = this.orderstatus
        }
        if (this.is_mix === 3) {
          delete this.listQuery.is_mix
        } else {
          this.listQuery.is_mix = this.is_mix
        }
        if (this.is_win === 3) {
          delete this.listQuery.is_win
        } else {
          this.listQuery.is_win = this.is_win
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
