<template>
  <div class="app-container">
    <div class="filter-container" style="font-size:0">
      <el-input
        v-model="listQuery.key_word"
        placeholder="关键字"
        style="width: 200px;"
        class="filter-item item-margin"
        @keyup.enter.native="handleFilter"
      />
      <el-date-picker
        v-model="startTime"
        type="date"
        value-format="yyyy-MM-dd"
        placeholder="开始日期"
        class="item-margin"
      />
      <el-date-picker
        v-model="endTime"
        type="date"
        value-format="yyyy-MM-dd"
        placeholder="结束日期"
        class="item-margin"
      />
      <el-button
        v-waves
        class="filter-item item-margin"
        type="primary"
        icon="el-icon-search"
        @click="handleFilter"
      >Search</el-button>
      <el-button
        v-waves
        class="filter-item item-margin"
        type="primary"
        icon="el-icon-add"
        @click="open"
      >Add</el-button>
      <span
        style="font-size:18px;color:#555;font-weight:bold;margin-left:15px"
      >Total Charge Amount: {{ total_amount }}</span>
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
      <el-table-column label="Charge ID" prop="RECHARGE_ID" align="center" />
      <el-table-column label="Agent Name" prop="NICK_NAME" align="center" />
      <el-table-column label="Before Charge" prop="BEFORE_MONEY" align="center" />
      <el-table-column label="Amount" prop="MONEY" align="center" />
      <el-table-column label="After Charge" prop="AFTER_MONEY" align="center" />
      <el-table-column label="Remark" prop="REMARK" align="center" />
      <el-table-column label="Operator" prop="CREATOR" align="center" />
      <el-table-column label="Operating Time" prop="CREATOR_TIME" align="center" />
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

    <el-dialog :title="dialogTitle" :visible.sync="dialogFormVisible" custom-class="dialogwidth">
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="temp"
        label-position="left"
        label-width="150px"
      >
        <el-row :gutter="25">
          <el-col :span="8">
            <el-form-item label="Agent Account" prop="ACCOUNT">
              <el-input v-model="temp.ACCOUNT" placeholder="Please Input Agent Account" @blur="getAgentInfo" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Agent Name">
              <el-input v-model="temp.AGENT_NAME" :disabled="true"/>
            </el-form-item>
          </el-col>
            <el-col :span="8">
            <el-form-item label="Agent Money">
              <el-input v-model="temp.SURPLUS_MONEY" :disabled="true" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="25">
          <el-col :span="8">
            <el-form-item label="Charge Amount" prop="MONEY">
              <el-input v-model="temp.MONEY" placeholder="Please Input Charge Amount" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Remark">
              <el-input v-model="temp.REMARK" placeholder="Please Input Remark"  />
            </el-form-item>
          </el-col>
        </el-row>

      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">Cancel</el-button>
        <el-button type="primary" @click="add">Confirm</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import waves from '@/directive/waves' // waves directive
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import { getAgent, addAgentRecharge } from '@/api/agent'
import { getRechargeList } from '@/api/player'


export default {
  name: 'PlayersRecharge',
  components: { Pagination },
  directives: { waves },
  data() {
    return {
      startTime: '',
      endTime: '',
      total: 0,
      reword: 0,
      keyword: '',
      dialogTitle: 'New Charge',
      list: [],
      tableKey: 0,
      total_amount: '',
      listLoading: false,
      dialogFormVisible: false,
      listQuery: {
        page: 1,
        limit: 99
      },
      temp: {
        AGENT_CODE:'',
        ACCOUNT: '',
        AGENT_NAME: '',
        MONEY: '',
        REMARK: ''
      },
      rules: {
        ACCOUNT: [
          { required: true, message: 'ACCOUNT is required', trigger: 'change' }
        ],
        MONEY: [
          {
            required: true,
            message: 'MONEY is required',
            trigger: 'change'
          }
        ]
      }
    }
  },
  created() {
    this.getList();
  },
  methods: {
    getList: function() {
      this.listLoading = true
      this.listQuery.charge_type = '1';
      getRechargeList(this.listQuery).then((response) => {
        this.list = response.items
        this.total = response.total
        this.total_amount = response.total_amount
        setTimeout(() => {
          this.listLoading = false
        }, 1.5 * 1000)
      })
    },
    getAgentInfo: function() {
      var _this = this
      var para = {
        account: _this.temp.ACCOUNT
      }
      
      getAgent(para).then((res) => {
        if (res.code === 20000) {
          if (res.agent) {
            _this.temp.AGENT_NAME =res.agent.AGENT_NAME
            _this.temp.SURPLUS_MONEY = res.agent.SURPLUS_MONEY
            _this.temp.AGENT_CODE = res.agent.AGENT_CODE
          } else {
            _this.$message({
              message: 'agent does not exist',
              type: 'error'
            })
          }
        }
      })
      
    },
    open: function() {
      this.temp.AGENT_CODE = ''
      this.temp.MONEY = ''
      this.dialogFormVisible = true
    },
    add: function() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          this.temp.MONEY = parseInt(this.temp.MONEY)
        } else {
          return
        }
      })
      this.dialogFormVisible = false
      addAgentRecharge(this.temp).then((response) => {
        if (response.code === 20000) {
          this.$message({
            message: response.message,
            type: 'success'
          })
          this.getList()
        }
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
.item-margin {
  margin-left: 5px;
  margin-right: 5px;
}
</style>
