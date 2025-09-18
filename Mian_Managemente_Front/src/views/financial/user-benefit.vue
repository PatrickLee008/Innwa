<template>
  <div class="app-container">
    <div class="filter-container" style="font-size:0">
      <el-input
        v-model="listQuery.key_word"
        placeholder="Key Word"
        style="width: 200px;"
        class="filter-item item-margin"
        @keyup.enter.native="handleFilter"
      />
      <el-date-picker
        v-model="listQuery.start_time"
        type="date"
        value-format="yyyy-MM-dd"
        placeholder="Start"
        class="item-margin"
      />
      <el-date-picker
        v-model="listQuery.end_time"
        type="date"
        value-format="yyyy-MM-dd"
        placeholder="End"
        class="item-margin"
      />
        <el-select v-model="listQuery.sort_key" placeholder="Sort" @change="handleFilter">
          <el-option  v-for="key in sortKey" :key="key.key" :label="key.label" :value="key.label"></el-option>
        </el-select>
      <el-button
        v-waves
        class="filter-item item-margin"
        type="primary"
        icon="el-icon-search"
        @click="handleFilter"
      >Search</el-button>
      <!--
      <el-button
        v-waves
        class="filter-item item-margin"
        type="primary"
        @click="settingAgentDialogVisible=true"
      >Setting Agent</el-button>
      -->
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
      <el-table-column label="UserId" prop="uid" sortable align="center" />
      <el-table-column label="Benefit percent" sortable prop="benefit_percent" align="center" />
      <el-table-column label="Win percent" sortable prop="win_percent" align="center"/>
      <el-table-column label="Order count" sortable prop="order_count" align="center" />
      <el-table-column label="Total bet" :formatter="tableFormat" sortable prop="total_bet" align="center" />
      <el-table-column label="Total bonus" :formatter="tableFormat" sortable prop="total_bonus" align="center" />
      <el-table-column label="Max Benefit" :formatter="tableFormat" sortable prop="max_benefit" align="center" />
      <el-table-column label="Total charge" :formatter="tableFormat" sortable prop="total_charge" align="center" />
      <el-table-column label="Total withdraw" :formatter="tableFormat" sortable prop="total_withdraw" align="center" />
<!--      <el-table-column-->
<!--        label="Operator"-->
<!--        align="center"-->
<!--        class-name="small-padding fixed-width"-->
<!--        width="200px"-->
<!--      >-->
<!--        <template slot-scope="{row}">-->
<!--          <el-button type="primary" circle icon="el-icon-edit" @click="handleUpdate(row)" />-->
<!--          <el-button-->
<!--            type="danger"-->
<!--            circle-->
<!--            icon="el-icon-delete"-->
<!--            @click="handleDelete(row,'deleted')"-->
<!--          />-->
<!--        </template>-->
<!--      </el-table-column>-->
    </el-table>

    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      :page-sizes="[20,50,99]"
      :page-size="99"
      @pagination="getList"
    />
  </div>
</template>

<script>
import waves from '@/directive/waves' // waves directive
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import {
  getUserBenefitReport,
} from '@/api/report'
import {dateToString, dateToString2} from '@/utils/date-format'
import { getAgentList } from '@/api/agent'
import {getInfo} from  '@/api/user'
import {number_format} from "@/utils";

export default {
  name: 'OrderList',
  components: { Pagination },
  directives: { waves },
  data() {
    return {
      noAgentUserStartTime: '',
      noAgentUserEndTime: '',
      betTotal: 0,
      reword: 0,
      roleselect: '',
      roles: ['全部'],
      noAgentUsers: [],
      textMap: {
        update: 'Edit',
        create: 'Create'
      },
      dialogStatus: '',
      settingAgentDialogVisible: false,
      list: [],
      agentOptions: [],
      deleteid: '',
      tableKey: 0,
      total: 0,
      noAgentUserTotal: 0, // 没有绑定代理的用户总数
      listLoading: true,
      noAgentUserLoading: false,
      dialogPvVisible: false,
      dialogFormVisible: false,
      sortKey:[
        {key:1,
          label:"benefit_percent",
        },
        {key:2,
          label:"max_benefit",
        },
        {key:3,
          label:"order_count",
        },
        {key:4,
          label:"total_bet",
        },
        {key:5,
          label:"total_bonus",
        },
        {key:6,
          label:"total_charge",
        },
        {key:7,
          label:"total_withdraw",
        },
        {key:8,
          label:"win_count",
        },
        {key:9,
          label:"win_percent",
        },
      ],
      listQuery: {
        page: 1,
        limit: 99,
        matchId: undefined,
        sort_key: 'benefit_percent',
        start_time:dateToString2(new Date()),
        end_time:dateToString2(new Date()),

      },
      noAgentUserlistQuery: {
        page: 1,
        limit: 50
      },
      STATE_OPTIONS: [
        {
          value: '0',
          label: '正常'
        },
        {
          value: '1',
          label: '禁用'
        }
      ],
      temp: {
        USER_ID: undefined,
        NICK_NAME: '',
        USER_PWD: '',
        REPEAT_PASSWORD: '',
        STATUS: '0',
        BANK_USER_NAME: '',
        BANK_CARD: '',
        AGENT_ID: '',
        PROVINCE: '',
        CITY: '',
        PHONE: '',
        AGENT_CODE: ''
      },
      agentInfo:{},
      is_agent:false,
      rules: {
        NICK_NAME: [
          { required: true, message: 'nickname is required', trigger: 'change' }
        ],
        PHONE: [
          { required: true, message: 'phone is required', trigger: 'change' }
        ],
        USER_PWD: [
          { required: true, message: 'password is required', trigger: 'change' }
        ]
      }
    }
  },
  created() {
    this.getList()
    // this.getAgent()
    // this.getUserInfo()
    // this.setDate()
  },
  methods: {
    getList: function() {
      this.listLoading = true
      this.listQuery.end_time = dateToString2(this.listQuery.end_time)
      this.listQuery.start_time = dateToString2(this.listQuery.start_time)
      getUserBenefitReport(this.listQuery).then(response => {
        this.listLoading = false
        this.list = response.items
        this.total = response.total
        this.list.forEach(element => {
          element.total_bonus = parseInt(element.total_bonus)
          element.max_benefit = parseInt(element.max_benefit)
          element.total_charge = parseInt(element.total_charge)
          element.total_withdraw = parseInt(element.total_withdraw)
          element.win_percent = (element.win_percent*100).toFixed(2) + "%"
          element.benefit_percent = (element.benefit_percent*100).toFixed(2) + "%"
        })
      })
    },
    setDate(){
      var today = dateToString2(new Date());
      this.listQuery.end_time = today;
      this.listQuery.start_time = today;
    },
    handleSort(val){
      // this.listQuery.sort_key = key
      this.getList()
    },
    handleFilter: function() {
      this.listQuery.page = 1
      this.getList()
    },
    tableFormat(row, column, index) {
      // console.log(row, column, index)
      let str = ''
      switch (column.property) {
        default:
          str = number_format(row[column.property])
          break
      }
      return str
    },
    // getAgent() {
    //   getAgentList().then(response => {
    //     response.items.forEach(element => {
    //       this.agentOptions.push({
    //         label: element.AGENT_NAME,
    //         value: element.AGENT_CODE
    //       })
    //     })
    //     setTimeout(() => {
    //       this.listLoading = false
    //     }, 1.5 * 1000)
    //   })
    // },
    // getUserInfo:function(){
    //   var _this =this;
    //   getInfo().then(res=>{
    //     if(res.code ===20000){
    //       _this.is_agent = res.data.is_agent;
    //       _this.agentInfo = res.data.agent_info;
    //     }
    //   })
    // },
  }
}
</script>
