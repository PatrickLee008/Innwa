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
        class="filter-item item-margin"
        type="primary"
        icon="el-icon-search"
        @click="handleFilter"
      >Search</el-button>
      <el-button
        v-waves
        class="filter-item item-margin"
        type="primary"
        icon="el-icon-plus"
        @click="handleCreate"
      >Add</el-button>
    </div>

    <el-table :key="tableKey" :data="list" border fit highlight-current-row style="width: 100%;">
      <el-table-column type="index" width="50" />
      <el-table-column label="ACCOUNT" prop="ACCOUNT" align="center" />
      <el-table-column label="Agent Name" prop="AGENT_NAME" align="center" />
      <el-table-column label="Money" prop="SURPLUS_MONEY" align="center" />
      <el-table-column label="Status" prop="STATUS" align="center">
        <template slot-scope="{row}">
          <span>{{ row.STATUS=='0'?'Disable':'Enable' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Phone" prop="PHONE_NO" align="center" />
      <el-table-column label="Total Amount" prop="TOTAL_MONEY" align="center" />
      <el-table-column label="Cash" prop="CASH_MONEY" align="center" />
      <el-table-column label="Creator" prop="CREATOR" align="center" />
      <el-table-column label="Create Time" prop="CREATOR_TIME" align="center" />
      <el-table-column label="Remark" prop="REMARK" align="center" />
      <el-table-column
        label="Operate"
        align="center"
        class-name="small-padding fixed-width"
        width="200px"
      >
        <template slot-scope="{row}">
          <el-button type="primary" circle icon="el-icon-edit" @click="handleUpdate(row)" />
          <el-button type="primary" circle icon="el-icon-plus" @click="handleRecharge(row)" />
          <el-button
            type="danger"
            circle
            icon="el-icon-delete"
            @click="handleDelete(row,'deleted')"
          />
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="getList"
    />

    <el-dialog
      :title="textMap[dialogStatus]"
      :visible.sync="dialogFormVisible"
      custom-class="dialogwidth"
    >
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="temp"
        label-position="left"
        label-width="150px"
      >
        <div class="lb">
          <!-- <el-form-item v-if="dialogStatus=='create'" label="角色">
            <el-checkbox-group v-model="temp.ROLES" class="checkGroup">
              <el-checkbox v-for="operate in operation" :key="operate.value" :label="operate.value" @change="handleChecked">{{ operate.label }}</el-checkbox>
            </el-checkbox-group>
          </el-form-item> -->

          <el-form-item label="Account" prop="ACCOUNT">
            <el-input v-model="temp.ACCOUNT" />
          </el-form-item>

          <el-form-item label="Password" prop="USER_PWD">
            <el-input v-model="temp.USER_PWD" type="password" />
          </el-form-item>

          <el-form-item label="Password Confirm" prop="repassword">
            <el-input v-model="temp.repassword" type="password" />
          </el-form-item>

          <el-form-item label="Agent Name" prop="AGENT_NAME">
            <el-input v-model="temp.AGENT_NAME" />
          </el-form-item>
          

          <el-form-item v-if="dialogStatus=='update'" label="Status">
            <el-select v-model="temp.STATUS">
              <el-option
                v-for="item in STATE_OPTIONS"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="Phone" prop="PHONE">
            <el-input v-model="temp.PHONE_NO" placeholder="Please input" />
          </el-form-item>

          <el-form-item label="Remark">
            <el-input v-model="temp.REMARK" placeholder="Please input" />
          </el-form-item>
        </div>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">Cancel</el-button>
        <el-button type="primary" @click="dialogStatus==='create'?createData():updateData()">Confirm</el-button>
      </div>
    </el-dialog>

    <el-dialog
      :title="textMap[dialogStatus]"
      :visible.sync="dialogRecVisible"
      custom-class="dialogwidth"
    >
      <el-form
        ref="dataForm1"
        :rules="rules"
        :model="recharge"
        label-position="left"
        label-width="100px"
      >
        <div class="lb">
          <el-form-item label="User Id">
            <el-input v-model="recharge.USER_ID" />
          </el-form-item>

          <el-form-item label="Nickname">
            <el-input v-model="recharge.NICK_NAME" />
          </el-form-item>

          <el-form-item label="Charge">
            <el-input v-model="recharge.MONEY" placeholder="Please input" />
          </el-form-item>

          <el-form-item label="Remark">
            <el-input v-model="recharge.REMARK" placeholder="Please input" />
          </el-form-item>
        </div>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogRecVisible = false">Cancel</el-button>
        <el-button type="primary" @click="doRecharge">Confirm</el-button>
      </div>
    </el-dialog>

    <el-dialog :visible.sync="dialogPvVisible" title>
      <h2 style="text-align:center">Are you sure you want to delete this user?</h2>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogPvVisible = false">Cancel</el-button>
        <el-button type="primary" @click="deleteAgent()">Confirm</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import waves from '@/directive/waves' // waves directive
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import { getAgentList, editAgent, delAgent, addAgent } from '@/api/agent'
// import { dateToString } from '@/utils/date-format'
import { addRecharge } from '@/api/player'
import { getRoles } from '@/api/role'

export default {
  name: 'AgentList',
  components: { Pagination },
  directives: { waves },
  data() {
    const USER_PWD_REP = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('Please enter the password again'))
      } else if (value !== this.temp.USER_PWD) {
        callback(new Error('Incorrect password entered twice'))
      } else {
        callback()
      }
    }
    return {
      startTime: '',
      endTime: '',
      betTotal: 0,
      reword: 0,
      roleselect: '',
      roles: ['All'],
      textMap: {
        update: 'Edit',
        create: 'Create'
      },
      dialogStatus: '',
      list: [],
      deleteid: [],
      tableKey: 0,
      total: 0,
      listLoading: true,
      dialogPvVisible: false,
      dialogFormVisible: false,
      dialogRecVisible: false,
      listQuery: {
        page: 1,
        limit: 99,
        matchId: undefined
      },
      STATE_OPTIONS: [
        {
          value: '1',
          label: 'Enable'
        },
        {
          value: '0',
          label: 'Disable'
        }
      ],
      operation: [],
      temp: {
        AGENT_CODE: undefined,
        AGENT_NAME: '',
        STATUS: '1',
        PROFIT: '',
        PHONE_NO: '',
        REMARK: '',
        ROLES: [],
        AGENT_ID: '',
        ACCOUNT: '',
        USER_PWD: '',
        PHONE: '',
        repassword: ''
      },
      recharge: {
        USER_ID: '',
        NICK_NAME: '',
        MONEY: 0,
        REMARK: ''
      },
      players: [],
      rules: {
        ACCOUNT: [
          { required: true, message: 'please enter account', trigger: 'blur' }
        ],
        AGENT_NAME: [
          { required: true, message: 'agent name is required', trigger: 'change' }
        ],
        PHONE: [
          { required: true, message: 'phone is required', trigger: 'change' }
        ],
        USER_PWD: [
          { required: true, message: 'please enter password', trigger: 'blur' }
        ],
        repassword: [
          { required: true, validator: USER_PWD_REP, trigger: 'blur' }
        ]
      }

    }
  },
  created() {
    this.getList()
    this.getRoles()
  },
  methods: {
    getRoles: function() {
      getRoles().then(res => {
        // 这里转换角色格式
        res.items.forEach(element => {
          this.operation.push({ value: element.role_id, label: element.role_name })
        })
      })
    },
    getList: function() {
      this.listLoading = true
      this.list = []
      getAgentList(this.listQuery).then(response => {
        response.items.forEach(element => {
          element.ACCOUNT = element.ACCOUNT.ACCOUNT
          this.list.push(element)
        })
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
    },
    resetTemp: function() {
      this.temp = {
        AGENT_CODE: undefined,
        AGENT_NAME: '',
        STATUS: '1',
        PROFIT: '',
        PHONE_NO: '',
        REMARK: '',
        ROLES: [],
        AGENT_ID: '',
        ACCOUNT: '',
        USER_PWD: '',
        PHONE: '',
        repassword: ''
      }
    },
    handleChecked: function(element) {},
    handleCreate() {
      this.resetTemp()
      this.dialogStatus = 'create'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    createData() {
      const _this = this
      this.$refs['dataForm'].validate(valid => {
        if (valid) {
          console.log()
        } else {
          return
        }
      })

      this.dialogFormVisible = false
      const para = {
        AGENT_NAME: _this.temp.AGENT_NAME,
        ACCOUNT: _this.temp.ACCOUNT,
        PROFIT: _this.temp.PROFIT,
        PASSWORD: _this.temp.USER_PWD,
        // ROLES: _this.temp.ROLES,
        PHONE_NO: _this.temp.PHONE_NO,
        REMARK: _this.temp.REMARK
      }

      addAgent(para).then(response => {
        _this.$message({
          message: response.message,
          type: 'success'
        })
        _this.getList()
      })
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row) // copy obj
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      const _this = this
      // if (valid) {
      // } else {
      //   return
      // }
      const para = {
        AGENT_CODE: _this.temp.AGENT_CODE,
        AGENT_NAME: _this.temp.AGENT_NAME,
        PHONE_NO: _this.temp.PHONE_NO,
        PROFIT: _this.temp.PROFIT,
        PASSWORD: _this.temp.USER_PWD
      }
      editAgent(para).then(response => {
        this.$message({
          message: response.message,
          type: 'success'
        })
      })
      this.getList()
      _this.dialogFormVisible = false
    },
    handleDelete(row) {
      this.dialogPvVisible = true
      this.deleteid = row
    },
    deleteAgent() {
      delAgent({ AGENT_CODE: this.deleteid.AGENT_CODE }).then(response => {
        setTimeout(() => {
          this.listLoading = false
        }, 1.5 * 1000)
        this.$notify({
          title: 'Success',
          message: 'Delete Successfully',
          type: 'success',
          duration: 2000
        })
        const index = this.list.indexOf(this.deleteid)
        this.list.splice(index, 1)
        this.dialogPvVisible = false
      })
    },
    handleRecharge: function(row) {
      this.dialogRecVisible = true
      this.recharge.USER_ID = row.AGENT_CODE
      this.recharge.NICK_NAME = row.AGENT_NAME
    },
    doRecharge: function() {
      this.dialogRecVisible = false
      addRecharge(this.recharge).then(response => {
        this.$message({
          message: response.message,
          type: 'success'
        })
      })
    }
  }
}
</script>
