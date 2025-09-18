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

      <el-input
        v-model="listQuery.cash_code"
        placeholder="Cash Code"
        style="width: 200px;"
        class="filter-item item-margin"
        @keyup.enter.native="handleFilter"
      />


      <el-select v-model="listQuery.order_by_select" placeholder="order by">
        <el-option value="create_time" label="Create Time"></el-option>
        <el-option value="total_money"  label="Total Money"></el-option>
        <el-option value="cash_code"  label="Cash Code"></el-option>
        <el-option value="login_time"  label="Login Time"></el-option>
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
        class="filter-item item-margin"
        type="primary"
        icon="el-icon-search"
        @click="handleFilter"
      >Search
      </el-button>
      <el-button v-waves class="filter-item item-margin" type="primary" @click="handleCreate">Add</el-button>
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

      <el-table-column type="index" width="50"/>
      <el-table-column label="UserId" prop="USER_ID" align="center"/>
      <el-table-column label="NickName" prop="NICK_NAME" align="center"/>
      <el-table-column label="VIP" prop="STATUS" align="center" width="45px">
        <template slot-scope="{row}">
          <span>{{ row.IS_VIP?'Yes':'No' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Limit" prop="STATUS" align="center" width="55px">
        <template slot-scope="{row}">
          <span>{{ row.HIGHER_LIMIT?'Yes':'No' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Status" prop="STATUS" align="center" width="65px">
        <template slot-scope="{row}">
          <span>{{ row.STATUS=='1'?'Disable':'Enable' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Real Name" prop="BANK_USER_NAME" align="center"/>
      <el-table-column label="Bank card number" prop="BANK_CARD" align="center"/>
      <el-table-column label="Phone" prop="PHONE" align="center"/>
      <el-table-column label="Owned Agent" prop="AGENT_ID" align="center"/>
      <el-table-column label="Cash Code" prop="CASH_CODE" align="center"/>
      <el-table-column label="Total Amount" :formatter="tableFormat" prop="TOTAL_MONEY" align="center"/>
      <el-table-column label="Total Cash" :formatter="tableFormat" prop="CASH_MONEY" align="center"/>
      <el-table-column label="Login Time" prop="OPT_TIME" align="center">
        <template slot-scope="{row}">
          <span>{{ (row.OPT_TIME) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Last Login IP" prop="LAST_LOGIN_IP" align="center"/>
      <el-table-column
        label="Operator"
        align="center"
        class-name="small-padding fixed-width"
        width="200px"
      >
        <template slot-scope="{row}">
          <el-button type="primary" circle icon="el-icon-edit" @click="handleUpdate(row)"/>
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
      :page-sizes="[20,50,99]"
      :page-size="99"
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
<!--          <el-form-item label="用户id" prop="USER_ID">-->
<!--            <el-input v-model="temp.USER_ID"/>-->
<!--          </el-form-item>-->

          <el-form-item label="昵称" prop="NICK_NAME">
            <el-input v-model="temp.NICK_NAME"/>
          </el-form-item>

          <el-form-item label="Password" prop="USER_PWD">
            <el-input v-model="temp.USER_PWD" placeholder="Please input" type="password"/>
          </el-form-item>

          <el-form-item label="Password Confirm">
            <el-input v-model="temp.REPEAT_PASSWORD" placeholder="Please input" type="password"/>
          </el-form-item>

          <el-form-item label="Status">
            <el-select v-model="temp.STATUS">
              <el-option
                v-for="item in STATE_OPTIONS"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="Real Name">
            <el-input v-model="temp.BANK_USER_NAME" placeholder="Please input"/>
          </el-form-item>

          <el-form-item label="Bank Card Number">
            <el-input v-model="temp.BANK_CARD" placeholder="Please input"/>
          </el-form-item>

          <el-form-item label="Cash Code">
            <el-input v-model="temp.CASH_CODE" placeholder="Please input"/>
          </el-form-item>


          <el-form-item label="Phone" prop="PHONE">
            <el-input v-model="temp.PHONE" onkeyup="value=value.replace(/[^\d]/g,'')" placeholder="Please input"/>
          </el-form-item>
          <el-form-item label="Agent" v-if="!is_agent">
            <el-select v-model="temp.AGENT_ID">
              <el-option
                v-for="item in agentOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="VIP" prop="VIP">
            <el-switch v-model="temp.IS_VIP" active-color="#13ce66" inactive-color="#ff4949"></el-switch>
          </el-form-item>
          <el-form-item label="HIGHER_LIMIT" prop="HIGHER_LIMIT">
            <el-switch v-model="temp.HIGHER_LIMIT" active-color="#13ce66" inactive-color="#ff4949"></el-switch>
          </el-form-item>
        </div>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">Cancel</el-button>
        <el-button type="primary" @click="dialogStatus==='create'?createData():updateData()">Confirm</el-button>
      </div>
    </el-dialog>

    <el-dialog :visible.sync="dialogPvVisible" title>
      <h2 style="text-align:center">Are you sure you want to delete this user?</h2>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogPvVisible = false">Cancel</el-button>
        <el-button type="primary" @click="deleteUser()">Confirm</el-button>
      </span>
    </el-dialog>
    <el-dialog :visible.sync="settingAgentDialogVisible" title width="80%">
      <h2 style="text-align:center">Setting User Agent</h2>
      <div class="filter-container" style="font-size:0">
        <el-date-picker
          v-model="noAgentUserStartTime"
          type="date"
          value-format="yyyy-MM-dd"
          placeholder="Start"
          class="item-margin"
        />
        <el-date-picker
          v-model="noAgentUserEndTime"
          type="date"
          value-format="yyyy-MM-dd"
          placeholder="End"
          class="item-margin"
        />

        <el-button type="primary" @click="getNoAgentUsers">go</el-button>

        <em>select agent:</em>
        <el-select v-model="temp.AGENT_ID">
          <el-option
            v-for="item in agentOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </div>

      <el-table
        :key="tableKey"
        v-loading="noAgentUserLoading"
        :data="noAgentUsers"
        border
        fit
        highlight-current-row
        style="width: 100%;"
      >
        <el-table-column label="UserId" prop="USER_ID" align="center"/>
        <el-table-column label="NickName" prop="NICK_NAME" align="center"/>
        <el-table-column label="Status" prop="STATUS" align="center" width="60px">
          <template slot-scope="{row}">
            <span>{{ row.STATUS=='1'?'Disable':'Enable' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Real Name" prop="BANK_USER_NAME" align="center"/>
        <el-table-column label="Bank card number" prop="BANK_CARD" align="center"/>
        <el-table-column label="Sex" prop="SEX" align="center" width="60px">
          <template slot-scope="{row}">
            <span>{{ row.SEX=='1'?'Female':'Man' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Phone" prop="PHONE" align="center"/>
        <el-table-column label="Owned Agent" prop="AGENT_ID" align="center"/>
        <el-table-column label="Total Amount" prop="TOTAL_MONEY" align="center"/>
        <el-table-column label="Total Cash" prop="CASH_MONEY" align="center"/>
        <el-table-column label="Login Time" prop="OPT_TIME" align="center">
          <template slot-scope="{row}">
            <span>{{ (row.OPT_TIME) }}</span>
          </template>
        </el-table-column>
        <el-table-column
          label="Operator"
          align="center"
          class-name="small-padding fixed-width"
          width="200px"
        >
          <template slot-scope="{row}">
            <el-button
              type="danger"
              circle
              icon="el-icon-delete"
              @click="noAgentUserhandleDelete(row)"
            />
          </template>
        </el-table-column>
      </el-table>

      <pagination
        v-show="noAgentUserTotal>0"
        :total="noAgentUserTotal"
        :page.sync="noAgentUserlistQuery.page"
        :limit.sync="noAgentUserlistQuery.limit"
        :page-sizes="[10,20,50]"
        :page-size="50"
        @pagination="getNoAgentUsers"
      />

      <span slot="footer" class="dialog-footer">
        <el-button @click="settingAgentDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="deleteUser()">Confirm</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
  import waves from '@/directive/waves' // waves directive
  import Pagination from '@/components/Pagination' // secondary package based on el-pagination
  import {
    getPlayerList,
    getUnAgentPlayerList,
    addPlayer,
    editPlayer,
    delPlayer
  } from '@/api/player'
  import {dateToString} from '@/utils/date-format'
  import {getAgentList} from '@/api/agent'
  import {getInfo} from '@/api/user'
  import {number_format} from "@/utils";

  export default {
    name: 'OrderList',
    components: {Pagination},
    directives: {waves},
    data() {
      return {
        startTime: '',
        endTime: '',
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
        listQuery: {
          page: 1,
          limit: 99,
          matchId: undefined
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
          AGENT_CODE: '',
          IS_VIP: false,
          HIGHER_LIMIT:false,
        },
        agentInfo: {},
        is_agent: false,
        rules: {
          NICK_NAME: [
            {required: true, message: 'nickname is required', trigger: 'change'}
          ],
          PHONE: [
            {required: true, message: 'phone is required', trigger: 'change'}
          ],
          USER_PWD: [
            {required: true, message: 'password is required', trigger: 'change'}
          ]
        }
      }
    },
    created() {
      this.getList()
      this.getAgent()
      this.getUserInfo()
    },
    methods: {
      getList: function () {
        this.listLoading = true
        getPlayerList(this.listQuery).then(response => {
          this.listLoading = false
          this.list = response.items
          this.total = response.total
          this.list.forEach(element => {
            element.OPT_TIME = dateToString(element.OPT_TIME)
            element.USER_PWD = null
          })
          setTimeout(() => {
            this.listLoading = false
          }, 1.5 * 1000)
        })
      },
      getUserInfo: function () {
        var _this = this;
        getInfo().then(res => {
          if (res.code === 20000) {
            _this.is_agent = res.data.is_agent;
            _this.agentInfo = res.data.agent_info;
          }
        })
      },
      handleFilter: function () {
        if (this.startTime !== '') {
          this.listQuery.start_time = this.startTime
        }
        if (this.endTime !== '') {
          this.listQuery.end_time = this.endTime
        }
        this.listQuery.page = 1
        this.getList()
      },
      resetTemp: function () {
        this.temp = {
          NICK_NAME: '',
          USER_PWD: '',
          REPEAT_PASSWORD: '',
          STATUS: '0',
          REAL_NAME: '',
          BANK_CARD: '',
          SEX: '0',
          AGENT_ID: '',
          PROVINCE: '',
          CITY: '',
          PHONE: '',
          BANK_USER_NAME: '',
          ROOM_CARD: 0,
          AGENT_CODE: '',
          IS_VIP: false,
        }
      },
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
          NICK_NAME: _this.temp.NICK_NAME,
          STATUS: _this.temp.STATUS,
          SEX: _this.temp.SEX,
          PROVINCE: _this.temp.PROVINCE,
          CITY: _this.temp.CITY,
          PHONE: _this.temp.PHONE.replace(/[^\d]/g,''),
          USER_PWD: _this.temp.USER_PWD,
          BANK_CARD: _this.temp.BANK_CARD,
          BANK_USER_NAME: _this.temp.BANK_USER_NAME,
          ROOM_CARD: 0,
          AGENT_ID: _this.temp.AGENT_ID,
          IS_VIP: _this.temp.IS_VIP,
          HIGHER_LIMIT: _this.temp.HIGHER_LIMIT,
        }

        if (this.is_agent) {
          para.AGENT_ID = this.agentInfo.AGENT_CODE;
        }

        addPlayer(para).then(response => {
          // 新增玩家api
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
          USER_ID: _this.temp.USER_ID.replace(/[^\d]/g,''),
          USER_PWD: _this.temp.USER_PWD,
          NICK_NAME: _this.temp.NICK_NAME,
          PHONE:_this.temp.PHONE,
          STATUS: _this.temp.STATUS,
          SEX: _this.temp.SEX,
          PROVINCE: _this.temp.PROVINCE,
          CITY: _this.temp.CITY,
          BANK_CARD: _this.temp.BANK_CARD,
          BANK_USER_NAME: _this.temp.BANK_USER_NAME,
          ROOM_CARD: 0,
          AGENT_ID: _this.temp.AGENT_ID,
          IS_VIP: _this.temp.IS_VIP,
          CASH_CODE:_this.temp.CASH_CODE,
          HIGHER_LIMIT: _this.temp.HIGHER_LIMIT,
        }
        if(!para.USER_PWD||para.USER_PWD===''){
          delete para.USER_PWD
        }
        if (this.is_agent) {
          para.AGENT_ID = this.agentInfo.AGENT_CODE;
        }

        editPlayer(para).then(response => {
          this.getList()
          this.$message({
            message: response.message,
            type: 'success'
          })
        })
        _this.dialogFormVisible = false
      },
      handleDelete(row) {
        this.dialogPvVisible = true
        this.deleteid = row
      },
      noAgentUserhandleDelete(row) {
        for (var i = 0; i < this.noAgentUsers.length; i++) {
          var currentRow = this.noAgentUsers[i]
          if (currentRow.USER_ID === row.USER_ID) {
            this.noAgentUsers.splice(i, 1)
          }
        }
      },
      deleteUser() {
        delPlayer({USER_ID: this.deleteid.USER_ID}).then(response => {
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
      getAgent() {
        getAgentList().then(response => {
          response.items.forEach(element => {
            this.agentOptions.push({
              label: element.AGENT_NAME,
              value: element.AGENT_CODE
            })
          })
        })
      },
      getNoAgentUsers() {
        var _this = this
        _this.noAgentUserLoading = true
        if (this.noAgentUserStartTime !== '') {
          this.noAgentUserlistQuery.start_time = this.noAgentUserStartTime
        }
        if (this.noAgentUserEndTime !== '') {
          this.noAgentUserlistQuery.end_time = this.noAgentUserEndTime
        }

        setTimeout(() => {
          _this.noAgentUserLoading = false
        }, 1.5 * 1000)
        getUnAgentPlayerList(this.noAgentUserlistQuery).then(response => {
          _this.noAgentUserLoading = false
          this.noAgentUsers = response.items
          this.noAgentUserTotal = response.noAgentUserTotal
        })
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
    }
  }
</script>
