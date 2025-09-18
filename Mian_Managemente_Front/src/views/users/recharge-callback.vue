<template>
  <div class="app-container">
    <div class="filter-container" style="font-size:0">
      <el-input
        v-model="listQuery.key_word"
        placeholder="key_word"
        style="width: 200px;"
        class="filter-item item-margin"
        @keyup.enter.native="handleFilter"
      />
      <el-date-picker
        v-model="startTime"
        type="date"
        value-format="yyyy-MM-dd"
        placeholder="startTime"
        class="item-margin"
      />
      <el-date-picker
        v-model="endTime"
        type="date"
        value-format="yyyy-MM-dd"
        placeholder="endTime"
        class="item-margin"
      />

      <el-select v-model="listQuery.status" placeholder="status filter">
        <el-option
          v-for="item in options"
          :key="item.value"
          :label="item.label"
          :value="item.value">
        </el-option>
      </el-select>


      <el-button
        v-waves
        class="filter-item item-margin"
        type="primary"
        icon="el-icon-search"
        @click="handleFilter"
      >Search
      </el-button>
      <!--      <el-button-->
      <!--        v-waves-->
      <!--        class="filter-item item-margin"-->
      <!--        type="primary"-->
      <!--        icon="el-icon-add"-->
      <!--        @click="open"-->
      <!--      >Add</el-button>-->
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
      <el-table-column type="index" width="50"/>
      <el-table-column label="Bank Type" prop="CUSTOMER_BANK_CODE" align="center"/>
      <el-table-column label="Transaction Id" prop="TRANSACTION_ID" align="center"/>
      <el-table-column label="Customer Account" prop="CUSTOMER_BANK_ACCOUNT" align="center"/>
      <el-table-column label="Receiver Account" prop="RECEIVER_BANK_ACCOUNT" align="center"/>
      <el-table-column label="Amount" prop="AMOUNT" align="center"/>
      <el-table-column label="User ID" prop="USER_ID" align="center"/>
      <el-table-column label="User Name" prop="NICK_NAME" align="center"/>

      <el-table-column label="Status" prop="STATUS" align="center">
        <template slot-scope="scope">
          <span :style="getStatusLabelAndStyle(scope.row.STATUS).style">
            {{ getStatusLabelAndStyle(scope.row.STATUS).label }}
          </span>
        </template>
      </el-table-column>


      <el-table-column label="Transaction Time" prop="TRANSACTION_DATETIME" align="center"/>
      <el-table-column label="Operation" align="center">
        <template slot-scope="scope" v-if="scope.row.STATUS == 0">
          <div style="display: flex;flex-direction: column;">
            <el-button type="primary"  @click="handerEdit(scope.row)">Edit</el-button>
            <!--            <el-button type="danger" style="margin-top: 7px" @click="handleDelete(scope.row)">Delete</el-button>-->
          </div>
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
            <el-form-item label="UserId" prop="USER_ID">
              <el-input v-model="temp.USER_ID" placeholder="Please Input UserId" @blur="getUserInfo"/>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Username">
              <el-input v-model="temp.NICK_NAME" disabled/>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="User Money">
              <el-input v-model="temp.TOTAL_MONEY" disabled/>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="25">

          <el-col :span="8">
            <el-form-item label="Bank Type" prop="CUSTOMER_BANK_CODE">
              <el-input v-model="temp.CUSTOMER_BANK_CODE"/>
            </el-form-item>
          </el-col>


          <el-col :span="8">
            <el-form-item label="Customer Account" prop="CUSTOMER_BANK_ACCOUNT">
              <el-input v-model="temp.CUSTOMER_BANK_ACCOUNT"/>
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="Receiver Account" prop="RECEIVER_BANK_ACCOUNT">
              <el-input v-model="temp.RECEIVER_BANK_ACCOUNT"/>
            </el-form-item>
          </el-col>

        </el-row>

        <el-row :gutter="25">

          <el-col :span="8">
            <el-form-item label="Charge Amount" prop="AMOUNT">
              <el-input v-model="temp.AMOUNT"/>
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="Status">

              <el-select v-model="temp.STATUS" placeholder="status">
                <el-option
                  v-for="item in options"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                  :disabled="(!temp.USER_ID || !temp.NICK_NAME) && item.value === 1"
                >
                </el-option>
              </el-select>

            </el-form-item>
          </el-col>


          <el-col :span="8">
            <el-form-item label="Remark">
              <el-input v-model="temp.REMARK"/>
            </el-form-item>
          </el-col>


        </el-row>

<!--        <el-row :gutter="25">-->

<!--          <h2>Upload Picture</h2>-->
<!--          <el-upload-->
<!--            action="http://localhost:9090/charge_callback/edit"-->
<!--            ref="upload"-->
<!--            name="image"-->
<!--            :headers=headers-->
<!--            :data="temp"-->
<!--            :auto-upload="false"-->
<!--            :file-list="fileList"-->
<!--            list-type="picture-card"-->
<!--            :on-preview="handlePictureCardPreview"-->
<!--            :on-remove="handleRemove"-->
<!--          >-->
<!--            <i class="el-icon-plus"></i>-->
<!--          </el-upload>-->

<!--        </el-row>-->


      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submit">Confirm</el-button>

      </div>
    </el-dialog>
  </div>
</template>

<script>
import waves from '@/directive/waves' // waves directive
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import { editRechargeCallBack, getRechargeCallBack } from '@/api/financial'
import { getPlayer } from '@/api/player'

export default {
  name: 'PlayersRecharge',
  components: { Pagination },
  directives: { waves },
  data() {
    return {
      options: [
        { label: 'Waiting', value: 0 },
        { label: 'finished', value: 1 },
        { label: 'invalid', value: 2 }
      ],
      startTime: '',
      fileList: [],
      endTime: '',
      total: 0,
      reword: 0,
      keyword: '',
      dialogTitle: 'New Charge',
      list: [],
      tableKey: 0,
      total_amount: '',
      listLoading: true,
      dialogFormVisible: false,
      headers: {},
      listQuery: {
        page: 1,
        limit: 99,
        matchId: undefined
      },
      temp: {
        USER_ID: undefined,
        NICK_NAME: '',
        MONEY: '',
        REMARK: ''
      },
      rules: {
        USER_ID: [
          { required: true, message: 'USER_ID is required', trigger: 'change' }
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
    this.getList()
    console.log('time', this.startTime, this.endTime)

    this.headers = {
      Authorization: this.getCOOKIE('Admin-Token')
    }
  },
  methods: {
    getStatusLabelAndStyle(status) {
      let style = '';
      if (status === 1) {
        style = 'color: green; font-weight: bold';
      } else if (status === 2) {
        style = 'color: red; font-weight: bold';
      }
      return {
        style: style,
        label: this.options[status].label
      };
    },
    handleRemove(file, fileList) {
      console.log(file, fileList)
    },
    handlePictureCardPreview(file) {
      console.log(file)
    },
    getCOOKIE: function(objname) {
      var arrstr = document.cookie.split(';')
      for (var i = 0; i < arrstr.length; i++) {
        var temp = arrstr[i].split('=')
        if (temp[0] == objname) {
          return unescape(temp[1])
        }
      }
    },
    handerEdit: function(row) {
      // console.log(JSON.stringify(row))
      this.temp = Object.assign({}, row)
      this.dialogFormVisible = true
    },
    getList: function() {
      this.listLoading = true
      if (this.listQuery.status == 'none') {
        delete this.listQuery.status
      }
      getRechargeCallBack(this.listQuery).then((response) => {
        this.list = response.items
        this.total = response.total
        this.total_amount = response.total_amount
        setTimeout(() => {
          this.listLoading = false
        }, 1.5 * 1000)
      })
    },
    getUserInfo: function() {
      var _this = this
      var para = {
        USER_ID: _this.temp.USER_ID
      }
      getPlayer(para).then((res) => {
        if (res.code === 20000) {
          if (res.info) {
            _this.temp.NICK_NAME = res.info.NICK_NAME
            _this.temp.TOTAL_MONEY = res.info.TOTAL_MONEY
          } else {
            _this.$message({
              message: 'User does not exist',
              type: 'error'
            })
          }
        }
      })
    },
    // open: function () {
    //   this.temp.USER_ID = "";
    //   this.temp.MONEY = "";
    //   this.temp.TOTAL_MONEY = "";
    //   this.dialogFormVisible = true;
    // },
    submit() {
      let _this = this;
      let para = Object.assign({}, this.temp)
      editRechargeCallBack(para).then(res => {
        if (res.code == 20000) {
          _this.getList()
          _this.$message({
            message: "Success",
            type: "success",
          });
          _this.dialogFormVisible = false;
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
