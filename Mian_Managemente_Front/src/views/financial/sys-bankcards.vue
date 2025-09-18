<template>
  <div class="app-container">
    <div class="filter-container">

      <el-select v-model="selected_bank_code" placeholder="Bank Code" clearable @change="bankCodeChange">
        <el-option
          v-for="item in bank_codes"
          :key="item"
          :label="item"
          :value="item">
        </el-option>
      </el-select>
      <el-button class="filter-item item-margin" type="primary" @click="handleCreate">Add</el-button>
    </div>

    <el-table
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%;"
    >
      <el-table-column type="index" width="50"/>
      <el-table-column label="Name" prop="NAME" align="center"/>
      <el-table-column label="Account" prop="ACCOUNT" align="center"/>
      <el-table-column label="Bank Code" prop="BANK_CODE" align="center"/>
      <el-table-column label="Daily Income" prop="DAILY_INCOME" align="center"/>
      <el-table-column label="Total income" prop="INCOME" align="center"/>
      <el-table-column label="Daily Limit" prop="DAILY_LIMIT" align="center"/>
      <!--      <el-table-column label="Remain Limit" align="center">-->
      <!--        <template slot-scope="scope">-->
      <!--          {{ scope.row.DAILY_LIMIT - scope.row.DAILY_INCOME }}-->
      <!--        </template>-->
      <!--      </el-table-column>-->
      <el-table-column label="Create Time" prop="CREATE_TIME" align="center"/>
      <el-table-column label="Update Time" prop="UPDATE_TIME" align="center"/>
      <el-table-column label="Remark" prop="REMARK" align="center"/>
      <el-table-column label="Enable" prop="ENABLE" align="center">
        <template slot-scope="scope">
          <el-switch v-model="scope.row.ENABLE" active-color="#13ce66" inactive-color="#ff4949"
                     @change="bankcardEnableChange(scope.row.ID, scope.row.ENABLE)"/>
        </template>
      </el-table-column>
      <el-table-column label="App Visible" prop="VISIBLE" align="center">
        <template slot-scope="scope">
          <el-switch v-model="scope.row.VISIBLE" active-color="#13ce66" inactive-color="#ff4949"
                     @change="bankcardVisibleChange(scope.row.ID, scope.row.VISIBLE)"/>
        </template>
      </el-table-column>
      <el-table-column label="Card Rank" prop="RANK" align="center"/>
      <el-table-column label="Operate" align="center" class-name="small-padding fixed-width">
        <template slot-scope="{row}">
          <el-row>
            <el-button type="primary" icon="el-icon-minus" circle @click="showReduceForm(row)"/>
            <el-button type="primary" icon="el-icon-date" circle @click="dailyReport(row)"/>
          </el-row>
          <el-row class="" style="padding: 3px"></el-row>
          <el-row>
            <el-button type="primary" icon="el-icon-edit" circle @click="handleUpdate(row)"/>
            <el-button icon="el-icon-delete" circle type="danger" @click="removeBankcard(row)"/>
          </el-row>
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

    <el-dialog title="System Bankcard" :visible.sync="dialogFormVisible" :close-on-click-modal="false">
      <el-form :model="temp" label-position="right" label-width="150px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Name">
              <el-input v-model="temp.NAME "/>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Account">
              <el-input v-model="temp.ACCOUNT "/>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Bank Code">
              <el-select v-model="temp.BANK_CODE" placeholder="请选择">
                <el-option
                  v-for="item in bank_codes"
                  :key="item"
                  :label="item"
                  :value="item">
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Income">
              <el-input v-model="temp.INCOME" oninput="value = value.match(/^\d+(?:\.\d{0,2})?/)"/>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-form-item label="Daily Limit">
              <el-input v-model="temp.DAILY_LIMIT" oninput="value = value.match(/^\d+(?:\.\d{0,2})?/)"/>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-form-item label="Card Rank">
              <el-input v-model="temp.RANK"/>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-form-item label="Remark">
              <el-input v-model="temp.REMARK"/>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button type="primary" @click="submit">Submit</el-button>
          <el-button @click="exit">Cancel</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>

    <el-dialog title="Daily Report" :visible.sync="reportFormVisible" :close-on-click-modal="false">

      <el-date-picker
        v-model="reportFilter.start_time"
        value-format="yyyy-MM-dd"
        type="date"
        placeholder="Start Date">
      </el-date-picker>


      <el-date-picker
        v-model="reportFilter.end_time"
        value-format="yyyy-MM-dd"
        type="date"
        placeholder="End Date">
      </el-date-picker>
      <el-button @click="getReport">Search</el-button>

      <el-table
        :data="dailyReportList"
        style="width: 100%">
        <el-table-column
          prop="DATE"
          label="Date"
          width="180">
        </el-table-column>
        <el-table-column
          prop="CUSTOMER_BANK_CODE"
          label="Bank Type"
          width="180">
        </el-table-column>
        <el-table-column
          prop="RECEIVER_BANK_ACCOUNT"
          label="Account"
          width="180">
        </el-table-column>
        <el-table-column
          prop="NAME"
          label="Name"
          width="180">
        </el-table-column>
        <el-table-column
          prop="AMOUNT"
          label="Amount"
          width="180">
        </el-table-column>
        <el-table-column
          prop="CASH_OUT"
          label="Cash Out"
          width="180">
        </el-table-column>
      </el-table>
    </el-dialog>

    <el-dialog title="Cash Out" :visible.sync="reduceFormVisible" :close-on-click-modal="false">

      <el-row>
        <el-input v-model="reduceForm.amount " style="width: 200px" placeholder="please input amount"/>
        <el-date-picker
          v-model="reduceForm.datetime"
          value-format="yyyy-MM-dd hh:mm:ss"
          type="datetime"
          placeholder="Cash Out Time">
        </el-date-picker>
      </el-row>

      <el-row style="margin-top: 12px">
        <el-button type="primary" @click="reduceSubmit()">Submit</el-button>
        <el-button type="info" @click="reduceFormVisible = false">Cancel</el-button>
      </el-row>
    </el-dialog>

  </div>
</template>

<script>
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import {
  getBankcardApi,
  ankcardVisibleApi,
  addBankcardApi,
  editBankcardApi,
  removeBankcardApi,
  activeBankcardApi,
  getDailyReport,
  bankCardCashOut
} from '@/api/financial'
import {dateToString2} from '@/utils/date-format'

export default {
  components: {Pagination},
  data() {
    return {
      listLoading: false,
      listLoading1: false,
      reduceFormVisible: false,
      selected_bank_code: "",
      list: [],
      total: 0,
      reduceForm: {
        id: 0,
        amount: 0
      },
      listQuery: {
        page: 1,
        limit: 20
      },
      reportFilter: {},
      bank_codes: ['KBZ', 'WaveMoney'],
      operate: 'add',
      dailyReportList: [],
      temp: {
        NAME: '',
        ACCOUNT: '',
        BANK_CODE: '',
        INCOME: '',
        DAILY_LIMIT: '',
        REMARK: '',
      },
      currentBankRow: {},
      dialogFormVisible: false,
      reportFormVisible: false,
      loading: {},
      form: {},
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList: function () {
      var _this = this
      _this.listLoading = true
      let para = Object.assign({},_this.listQuery)
      para.bank_code =  _this.selected_bank_code
      getBankcardApi(para).then(res => {
        _this.listLoading = false
        if (res.code === 20000) {
          _this.list = res.items
          _this.total = res.total;
        }
      })
    },
    reduceSubmit() {

      var _this = this;
      const loading = this.$loading({
        lock: true,
        text: 'Loading',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)'
      })

      var para = {
        amount: this.reduceForm.amount,
        datetime: this.reduceForm.datetime
      }
      para.amount = parseInt(para.amount)

      bankCardCashOut(this.reduceForm.ID, para).then(res => {
        if (res.code == 20000) {
          loading.close()
          _this.$message({
            message: 'Update Bankcard Success!',
            type: 'success'
          })
          _this.getList()
        }
        _this.reduceFormVisible = false
      })
    },
    showReduceForm(row) {
      this.reduceForm = row;
      this.reduceFormVisible = true;
    },
    handleUpdate(row) {
      this.resetForm()
      this.operate = 'update'
      this.temp = Object.assign({}, row)
      this.dialogFormVisible = true
    },
    dailyReport(row) {
      this.resetForm()
      this.reportFormVisible = true
      this.currentBankRow = row;
    },
    getReport: function () {
      var _this = this
      _this.listLoading1 = true

      var para = {
        id: this.currentBankRow.ID,
        start_time: this.reportFilter.start_time,
        end_time: this.reportFilter.end_time
      }
      getDailyReport(para).then(res => {
        _this.listLoading1 = false
        if (res.code === 20000) {
          _this.dailyReportList = res.items
        }
      })
    },
    resetForm() {
      this.form = this.$options.data().form
    },
    submit() {
      if (this.operate == 'add') {
        this.addBankcard()
      } else {
        this.updateBankcard()
      }
    },
    updateBankcard() {
      var _this = this

      const loading = this.$loading({
        lock: true,
        text: 'Loading',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)'
      })

      delete _this.temp.CREATE_TIME
      delete _this.temp.CREATOR
      delete _this.temp.UPDATE_TIME

      editBankcardApi(_this.temp).then(res => {
        loading.close()
        if (res.code === 20000) {
          _this.$message({
            message: 'Update Bankcard Success!',
            type: 'success'
          })
          _this.getList()
          _this.dialogFormVisible = false
        }
      })
    },
    bankCodeChange() {
      this.getList()
    },
    bankcardVisibleChange(id, visible) {
      let _this = this
      const loading = this.$loading({
        lock: true,
        text: 'Loading',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)'
      })

      let data = {'ID': id, 'VISIBLE': visible}

      ankcardVisibleApi(data).then(res => {
        loading.close()
        if (res.code === 20000) {
          _this.$message({
            message: 'Active Bankcard Success!',
            type: 'success'
          })
          _this.getList()
          _this.dialogFormVisible = false
        }
      })
    },
    bankcardEnableChange(id, enable) {
      let _this = this
      const loading = this.$loading({
        lock: true,
        text: 'Loading',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)'
      })

      let data = {'ID': id, 'enable': enable}

      activeBankcardApi(data).then(res => {
        loading.close()
        if (res.code === 20000) {
          _this.$message({
            message: 'Active Bankcard Success!',
            type: 'success'
          })
          _this.getList()
          _this.dialogFormVisible = false
        }
      })
    },
    addBankcard() {
      var _this = this

      const loading = this.$loading({
        lock: true,
        text: 'Loading',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)'
      })

      addBankcardApi(_this.temp).then(res => {
        loading.close()
        if (res.code === 20000) {
          _this.$message({
            message: 'Add Bankcard Success!',
            type: 'success'
          })
          _this.getList()
          _this.dialogFormVisible = false
        }
      })
    },
    removeBankcard(row) {
      var _this = this

      this.$confirm('Are you sure to permanently delete this record?', 'Tips', {
        confirmButtonText: 'Yes',
        cancelButtonText: 'Cancel',
        type: 'warning'
      })
        .then(() => {
          const loading = this.$loading({
            lock: true,
            text: 'Loading',
            spinner: 'el-icon-loading',
            background: 'rgba(0, 0, 0, 0.7)'
          })
          removeBankcardApi({ID: row.ID}).then(res => {
            loading.close()
            if (res.code === 20000) {
              _this.$message({
                message: 'Remove Bankcard Success!',
                type: 'success'
              })
              _this.getList()
            }
          })
        })
        .catch(() => {
          this.$message({
            type: 'info',
            message: '已取消删除'
          })
        })
    },
    handleCreate() {
      this.dialogFormVisible = true
      this.operate = 'add'
      this.temp = {ENABLE: true}
    },
    exit() {
      this.dialogFormVisible = false
    }
  }
}
</script>
