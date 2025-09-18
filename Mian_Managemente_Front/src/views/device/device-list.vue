<template>
  <div class="app-container">
    <div class="filter-container">
      <!--      <el-button type="primary" @click="getorderList">getorderList</el-button>-->
      <!--      <el-button type="primary" @click="gettotalList">gettotalList</el-button>-->
      <!--      <el-button type="primary" @click="getPlaysTotal">getPlaysTotal</el-button>-->
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
      <el-table-column type="index" width="50" />
      <el-table-column label="Device Name" prop="Name" align="center" />
      <el-table-column label="Mac Address" prop="MacAddress" align="center" />
      <el-table-column label="Last Login Time" prop="LastLoginTime" align="center" />
      <el-table-column label="Disable" prop="Enable" align="center">
        <template slot-scope="scope">
          <el-switch v-model="scope.row.enable" active-color="#13ce66" inactive-color="#ff4949" />
        </template>
      </el-table-column>
      <el-table-column label="Creator" prop="Creator" align="center" />
      <el-table-column label="Create Time" prop="CreateTime" align="center" />
      <el-table-column label="Operate" align="center" class-name="small-padding fixed-width">
        <template slot-scope="{row}">
          <el-button type="primary" icon="el-icon-edit" circle @click="handleUpdate(row)" />
          <el-button icon="el-icon-delete" circle type="danger" @click="removeDevie(row)" />
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

    <el-dialog title="Add Device" :visible.sync="dialogFormVisible" :close-on-click-modal="false">
      <el-form :model="temp" label-position="right" label-width="150px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Device Name">
              <el-input v-model="temp.Name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Mac Address">
              <el-input v-model="temp.MacAddress" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-form-item label="Remark">
              <el-input v-model="temp.Remark" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button type="primary" @click="submit">Submit</el-button>
          <el-button @click="exit">Cancel</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script>
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import {
  getDeviceApi,
  addDeviceApi,
  editDeviceApi,
  removeDeviceApi
} from '@/api/device'
import { getLatestWithDrawList } from '@/api/financial'
import { getLatestOrders } from '@/api/order'
import { getPlayerCount, getToTalReport } from '@/api/report'
import { dateToString2 } from '@/utils/date-format'
import echarts from 'echarts'
export default {
  name: 'OrderList',
  components: { Pagination },
  data() {
    return {
      listLoading: false,
      list: [],
      total: 0,
      listQuery: {
        page: 0,
        limit: 0
      },
      operate: 'add',
      temp: {
        Name: '',
        MacAddress: '',
        Enable: true,
        Remark: ''
      },
      dialogFormVisible: false,
      loading: {}
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList: function() {
      var _this = this
      _this.listLoading = true

      getDeviceApi({}).then(res => {
        _this.listLoading = false
        if (res.code === 20000) {
          _this.list = res.items
        }
      })
    },
    handleUpdate(row) {
      this.operate = 'update'
      this.temp = Object.assign({}, row)
      this.dialogFormVisible = true
    },
    submit() {
      if (this.operate == 'add') {
        this.addDevie()
      } else {
        this.updateDevice()
      }
    },
    updateDevice() {
      var _this = this

      const loading = this.$loading({
        lock: true,
        text: 'Loading',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)'
      })

      delete _this.temp.CreateTime
      delete _this.temp.Creator
      delete _this.temp.LastLoginTime

      editDeviceApi(_this.temp).then(res => {
        loading.close()
        if (res.code === 20000) {
          _this.$message({
            message: 'Update Device Success!',
            type: 'success'
          })
          _this.getList()
          _this.dialogFormVisible = false
        }
      })
    },
    addDevie() {
      var _this = this

      const loading = this.$loading({
        lock: true,
        text: 'Loading',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)'
      })

      addDeviceApi(_this.temp).then(res => {
        loading.close()
        if (res.code === 20000) {
          _this.$message({
            message: 'Add Device Success!',
            type: 'success'
          })
          _this.getList()
          _this.dialogFormVisible = false
        }
      })
    },
    removeDevie(row) {
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
          removeDeviceApi({ ID: row.ID }).then(res => {
            loading.close()
            if (res.code === 20000) {
              _this.$message({
                message: 'Remove Device Success!',
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
      this.temp = {}
    },
    exit() {
      this.dialogFormVisible = false
    },
    getPlaysTotal() {
      getPlayerCount().then(res => {
        if (res.code === 20000) {
          this.user_active_count = res.user_active_count
          this.orders_today_count = res.orders_today_count
          this.user_today_count = res.user_today_count
          this.user_count = res.user_count
          this.user_month_count = res.user_month_count
          this.user_today_bet = res.user_today_bet
          this.orders_today_sum = res.orders_today_sum
        }
      })
    },

    getorderList() {
      var _this = this
      _this.loading = true
      getLatestOrders({ pageSize: 6 }).then(res => {
        if (res.code === 20000) {
        }
      })
    },
    gettotalList() {
      var _this = this
      getToTalReport({ 'start_time': dateToString2(new Date()) }).then(res => {
        if (res.code === 20000) {
        }
      })
    }
  }
}
</script>
