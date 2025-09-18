<template>
  <div class="app-container">
    <div class="filter-container">
      <el-row>
        <el-input
          v-model="listQuery.key_word"
          placeholder="Key Word"
          style="width: 200px"
          class="filter-item"
          @keyup.enter.native="handleFilter"
        />
        <em>Status</em>
        <el-select v-model="status" class="filter-item" placeholder="Status">
          <el-option
            v-for="item in status_option"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        <em>Group</em>
        <el-select v-model="listQuery.group_id" class="filter-item" placeholder="Group">
          <el-option
            v-for="item in groupList"
            :key="item.ID"
            :label="item.GROUP_NAME"
            :value="item.ID"
          />
        </el-select>
        <el-date-picker
          v-model="startTime"
          type="date"
          value-format="yyyy-MM-dd"
          placeholder="Start"
        />
        <el-date-picker
          v-model="endTime"
          type="date"
          value-format="yyyy-MM-dd"
          placeholder="End"
        />
        <el-button
          v-waves
          class="filter-item"
          type="primary"
          icon="el-icon-search"
          @click="handleFilter"
        >Search
        </el-button
        >
      </el-row>
      <el-row>
        <span>Withdraw Total Amount:{{ cashTotal + '    '}}</span>
<!--        <span> Undeal Count:{{ undealTotal }}</span>-->
      </el-row>
    </div>

    <el-table
      v-loading="listLoading"
      :key="tableKey"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%"
    >
      <el-table-column type="index" width="50"/>
      <el-table-column
        label="Withdraw ID"
        prop="WITHDRAWAL_ID"
        align="center"
      />
      <el-table-column
        label="Withdraw Code"
        prop="WITHDRAWAL_CODE"
        align="center"
      />
      <el-table-column label="UserId" prop="USER_ID" align="center"/>
      <el-table-column label="Username" prop="NICK_NAME" align="center"/>
      <el-table-column label="Before Money" :formatter="tableFormat" prop="BEFORE_MONEY" align="center" />
      <el-table-column label="WithDraw Amount" :formatter="tableFormat" prop="MONEY" align="center"/>
      <el-table-column label="After Money" :formatter="tableFormat" prop="AFTER_MONEY" align="center"/>

      <el-table-column label="Bank" prop="BANK_TYPE" align="center"/>

      <el-table-column label="Card Number" prop="CARD_NUM" align="center"/>
      <el-table-column label="Operator" prop="OPERATOR" align="center"/>
      <el-table-column label="Remark" prop="REMARK" align="center"/>

      <el-table-column label="Payment" align="center">
        <template slot-scope="{ row }">
          <span v-if="row.IS_PAY == 1">Paid</span>
          <span v-if="row.IS_PAY == 2">Reject</span>
          <span v-if="row.IS_PAY == 0">Unpaid</span>
        </template>
      </el-table-column>
      <!-- <el-table-column label="创建人" prop="CREATOR" align="center" /> -->
      <el-table-column label="Withdraw Time" prop="CREATE_TIME" align="center" />
      <el-table-column label="WithDraw Group" prop="Work_Group" align="center"/>
      <el-table-column
        label="operating"
        align="center"
        class-name="small-padding fixed-width"
      >

        <template slot-scope="{ row }">
          <el-button
            v-if="row.IS_PAY == '0'"
            type="primary"
            size="mini"
            @click="handlesettle(row)"
          >Deal
          </el-button
          >

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
      v-show="total > 0"
      :page-sizes="[20, 50, 99]"
      :page-size="99"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="getList"
    />

    <el-dialog :visible.sync="dialogPvVisible" @close="remark = null">
      <h2 style="text-align: center">
        Which action do you want to perform on this withdrawal application?
      </h2>
      <span slot="footer" class="dialog-footer">
        <el-row>
          <el-col :span="12" align="left">
            <em style="">Remark:</em>
            <el-input v-model="remark" style="width: 200px; color: yellow"/>
          </el-col>
          <el-col :span="12" align="right">
            <el-button type="primary" @click="cash(1)">Pay</el-button>
            <el-button type="danger" @click="cash(0)">Reject</el-button>
            <el-button @click="dialogPvVisible = false">Nothing</el-button>
          </el-col>
        </el-row>
      </span>
    </el-dialog>
  </div>
</template>

<script>
  import waves from "@/directive/waves"; // waves directive
  import Pagination from "@/components/Pagination"; // secondary package based on el-pagination
  import {
    getCashList,
    settleCash,
    removeAgentWithdrawApi, getGroupApi,
  } from "@/api/financial";
  import {number_format} from "@/utils";

  export default {
    name: "Playercash",
    components: {Pagination},
    directives: {waves},
    data() {
      return {
        startTime: "",
        endTime: "",
        nickName: "",
        cashTotal: 0,
        undealTotal: 0,
        list: [],
        groupList: [],
        tableKey: 0,
        total: 0,
        cashid: "",
        dialogPvVisible: false,
        listLoading: false,
        status: 3,
        remark: null,
        status_option: [
          {
            value: 3,
            label: "All",
          },
          {
            value: 1,
            label: "Paid",
          },
          {
            value: 2,
            label: "Reject",
          },
          {
            value: 0,
            label: "Unpaid",
          },
        ],
        pay: [],
        listQuery: {
          page: 1,
          limit: 99,
          matchId: undefined,
        },
      };
    },
    created() {
      this.getList();
      this.getGroupList();
    },
    methods: {
      getList: function () {
        this.listLoading = true;
        this.listQuery.pay_type = 2;
        getCashList(this.listQuery).then((response) => {
          this.list = response.items;
          this.total = response.total;
          this.cashTotal = number_format(response.total_amount);
          this.undealTotal = response.undeal_count;
          setTimeout(() => {
            this.listLoading = false;
          }, 1.5 * 1000);
        });
      },

      getGroupList: function () {
        var _this = this
        _this.groupList = [{GROUP_NAME: 'All',ID:0},]
        getGroupApi({}).then(res => {
          if (res.code === 20000) {
            res.items.forEach(ele=>{
              _this.groupList.push(ele)
            })
          }
        })
      },
      handlesettle: function (row) {
        const _this = this;
        _this.dialogPvVisible = true;
        _this.cashid = row.WITHDRAWAL_ID;
      },
      cash: function (type) {
        const _this = this;
        _this.dialogPvVisible = false;
        settleCash({
          deal_opt: type,
          withdraw_id: _this.cashid,
          remark: _this.remark,
        }).then((response) => {
          _this.$message({
            message: response.message,
            type: "success",
          });
          _this.getList();
        });
      },
      removeWithdraw: function (row) {
        var _this = this;
        removeAgentWithdrawApi({remove_id: row.WITHDRAWAL_ID}).then((res) => {
          if (res.code === 20000) {
            _this.$message({
              message: "remove success!",
              type: "success",
            });
            _this.getList();
          }
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
    },
  };
</script>
