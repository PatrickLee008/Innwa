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
      <em>Status</em>
      <el-select v-model="status" class="filter-item">
        <el-option
          v-for="item in status_option"
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
      />
      <el-date-picker v-model="endTime" type="date" value-format="yyyy-MM-dd" placeholder="End" />
      <el-button
        v-waves
        class="filter-item"
        type="primary"
        icon="el-icon-search"
        @click="handleFilter"
      >Search</el-button>
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-plus" @click="addCash">Add</el-button>
      <span>Total withdrawal:{{ cashTotal }}</span>
    </div>

    <el-table :key="tableKey" :data="list" border fit highlight-current-row style="width: 100%;">
      <el-table-column type="index" width="50" />
      <el-table-column label="UserId" prop="USER_ID" align="center" />
      <el-table-column label="nickname" prop="NICK_NAME" align="center" />
      <el-table-column label="Before Money" prop="BEFORE_MONEY" align="center" />
      <el-table-column label="withdraw" prop="MONEY" align="center" />
      <el-table-column label="After Money" prop="AFTER_MONEY" align="center" />
      <el-table-column label="Balance" prop="MONEY" align="center" />
      <el-table-column label="Paid" align="center">
        <template slot-scope="{row}">
           <span v-if="row.IS_PAY==1">Paid</span>
          <span v-if="row.IS_PAY==2">Reject</span>
          <span v-if="row.IS_PAY==0">Unpaid</span>
        </template>
      </el-table-column>
      <el-table-column label="Withdraw Time" prop="CREATE_TIME" align="center" />

      <el-table-column
        v-if="!isAgent"
        label="Operator"
        align="center"
        class-name="small-padding fixed-width"
      >
        <template slot-scope="{row}">
          <el-button
            v-if="row.IS_PAY=='0'"
            type="primary"
            size="mini"
            @click="handlesettle(row)"
          >Deal</el-button>
          <!--
          <el-button
            v-if="row.IS_PAY=='1'"
            type="danger"
            icon="el-icon-delete"
            circle
            @click="removeWithdraw(row)"
          ></el-button>
          -->
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

    <el-dialog :title="'New Withdraw'" :visible.sync="dialogFormVisible">
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="temp"
        label-position="left"
        label-width="180px"
      >
        <div class="lb">
          <!-- <el-form-item label="代理ID" prop="USER_ID">
            <el-select v-model="temp.USER_ID" no-data-text="暂无代理" @visible-change="selOption(1)">
              <el-option
                v-for="item in inList"
                :key="item.id"
                :label="item.id"
                :value="item"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="代理名">
            <el-select v-model="temp.NICK_NAME" no-data-text="暂无代理" @visible-change="selOption(2)">
              <el-option
                v-for="item in inList"
                :key="item.label"
                :label="item.label"
                :value="item"
              />
            </el-select>
          </el-form-item>-->
          <!-- <el-form-item label="余额">
            <el-input v-model="temp.LEFT_MONEY" placeholder="Please input" />
          </el-form-item>-->
          <el-form-item label="Withdraw Amount" prop="MONEY">
            <el-input v-model="temp.MONEY" placeholder="Please input" type="number" />
          </el-form-item>
        </div>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">Cancel</el-button>
        <el-button type="primary" @click="doAddCash">Confirm</el-button>
      </div>
    </el-dialog>

    <el-dialog :visible.sync="dialogPvVisible" title>
      <h2 style="text-align:center">Which action do you want to perform on this withdrawal application?</h2>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="cash(1)">Pay</el-button>
        <el-button type="danger" @click="cash(0)">Reject</el-button>
        <el-button @click="dialogPvVisible = false">Nothing</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import waves from "@/directive/waves"; // waves directive
import Pagination from "@/components/Pagination"; // secondary package based on el-pagination
import {
  getCashList,
  removeAgentWithdrawApi,
  settleAgentCash,
  addWithdraw,
} from "@/api/financial";
import { getInfo } from "@/api/user";

export default {
  name: "Playercash",
  components: { Pagination },
  directives: { waves },
  data() {
    return {
      startTime: "",
      endTime: "",
      nickName: "",
      cashTotal: 0,
      list: [],
      agList: [],
      tableKey: 0,
      total: 0,
      cashid: "",
      isAgent: false,
      dialogPvVisible: false,
      dialogFormVisible: false,
      listLoading: true,
      status: 3,
      status_option: [
        {
          value: 3,
          label: "全部",
        },
        {
          value: 1,
          label: "已付款",
        },
        {
          value: 0,
          label: "未付款",
        },
      ],
      rules: {
        USER_ID: [
          { required: true, message: "USER_ID is required", trigger: "change" },
        ],
        MONEY: [
          {
            required: true,
            message: "MONEY is required",
            trigger: "change",
          },
        ],
      },
      temp: {
        USER_ID: "",
        NICK_NAME: "",
        LEFT_MONEY: 0,
        MONEY: 0,
      },
      pay: [],
      listQuery: {
        page: 1,
        limit: 99,
        matchId: undefined,
      },
      inList: [],
    };
  },
  created() {
    this.getUserInfo();
    this.getList();
  },
  methods: {
    getList: function () {
      this.listLoading = true;
      this.listQuery.pay_type = 1;
      getCashList(this.listQuery).then((response) => {
        this.list = response.items;
        this.total = response.total;
        this.cashTotal = response.total_amount;
        response.items.forEach((element) => {
          this.inList.push({ id: element.USER_ID, name: element.NICK_NAME });
        });
        setTimeout(() => {
          this.listLoading = false;
        }, 1.5 * 1000);
      });
    },

    removeWithdraw: function (row) {
      var _this = this;
      removeAgentWithdrawApi({ remove_id: row.WITHDRAWAL_ID }).then((res) => {
        if (res.code === 20000) {
          _this.$message({
            message: "remove success!",
            type: "success",
          });
          _this.getList();
        }
      });
    },
    handlesettle: function (row) {
      const _this = this;
      _this.dialogPvVisible = true;
      _this.cashid = row.WITHDRAWAL_ID;
    },
    cash: function (type) {
      const _this = this;
      _this.dialogPvVisible = false;
      settleAgentCash({deal_opt:type, withdraw_id: _this.cashid }).then((response) => {
        _this.$message({
          message: response.message,
          type: "success",
        });
        _this.getList();
      });
    },
    handleFilter: function () {
      if (this.startTime !== "") {
        this.listQuery.start_time = this.startTime;
      }
      if (this.endTime !== "") {
        this.listQuery.end_time = this.endTime;
      }
      if (this.status === 3) {
        delete this.listQuery.is_pay;
      } else {
        this.listQuery.is_pay = this.status;
      }
      this.listQuery.page = 1;
      this.getList();
    },
    addCash: function () {
      this.dialogFormVisible = true;
      this.temp.MONEY = "";
    },
    getUserInfo: function () {
      var _this = this;
      getInfo().then((res) => {
        if (res.code === 20000) {
          _this.isAgent = res.data.is_agent;
        }
      });
    },
    doAddCash: function () {
      this.dialogFormVisible = false;
      addWithdraw({
        agent_id: this.temp.USER_ID.id,
        MONEY: this.temp.MONEY,
        PAY_TYPE: "1",
      }).then((response) => {
        if (response.code === 50001) {
          this.$message({
            message: response.message,
            type: "fail",
          });
        }
        this.$message({
          message: response.message,
          type: "success",
        });
        this.getList();
      });
    },
  },
};
</script>
