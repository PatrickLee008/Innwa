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
        placeholder="Start Date"
        class="item-margin"
      />
      <el-date-picker
        v-model="endTime"
        type="date"
        value-format="yyyy-MM-dd"
        placeholder="End Date"
        class="item-margin"
      />
      <el-select v-model="listQuery.charge_way" placeholder="Charge Type">
        <el-option
          v-for="(item,index) in options"
          :key="index"
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
      <el-button
        v-waves
        class="filter-item item-margin"
        type="primary"
        icon="el-icon-add"
        @click="open"
      >Add
      </el-button>
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
      <el-table-column label="Charge ID" prop="RECHARGE_ID" align="center"/>
      <el-table-column label="UserId" prop="USER_ID" align="center"/>
      <el-table-column label="UserName" prop="NICK_NAME" align="center"/>
      <el-table-column label="Before Charge" prop="BEFORE_MONEY" :formatter="tableFormat" align="center"/>
      <el-table-column label="Amount" prop="MONEY" :formatter="tableFormat" align="center"/>
      <el-table-column label="After Charge" prop="AFTER_MONEY" :formatter="tableFormat" align="center"/>
      <el-table-column label="Remark" prop="REMARK" align="center"/>
      <el-table-column label="Operator" prop="CREATOR" align="center"/>
      <el-table-column label="Operating Time" prop="CREATOR_TIME" align="center"/>
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
              <el-input v-model="temp.NICK_NAME" :disabled="true"/>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="User Money">
              <el-input v-model="temp.TOTAL_MONEY" :disabled="true"/>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="25">
          <el-col :span="8">
            <el-form-item label="Charge Amount" prop="MONEY">
              <el-input v-model="temp.MONEY" placeholder="Please input Charge Amount"/>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Remark">
              <el-input v-model="temp.REMARK" placeholder="Please input Remark"/>
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
  import waves from "@/directive/waves"; // waves directive
  import Pagination from "@/components/Pagination"; // secondary package based on el-pagination
  import {getPlayer, getRechargeList, addRecharge} from "@/api/player";
  import {number_format} from "@/utils";

  export default {
    name: "PlayersRecharge",
    components: {Pagination},
    directives: {waves},
    data() {
      return {
        startTime: "",
        endTime: "",
        total: 0,
        reword: 0,
        keyword: "",
        dialogTitle: "New Charge",
        list: [],
        tableKey: 0,
        total_amount: "",
        listLoading: true,
        dialogFormVisible: false,
        listQuery: {
          page: 1,
          limit: 99,
          matchId: undefined,
        },
        temp: {
          USER_ID: undefined,
          NICK_NAME: "",
          MONEY: "",
          REMARK: "",
        },
        rules: {
          USER_ID: [
            {required: true, message: "USER_ID is required", trigger: "change"},
          ],
          MONEY: [
            {
              required: true,
              message: "MONEY is required",
              trigger: "change",
            },
          ],
        },
        options: [
          {
            value: '',
            label: 'All'
          },
          {
            value: 1,
            label: 'Auto'
          },
          {
            value: 0,
            label: 'Manual'
          }],
      };
    },
    created() {
      this.getList();
      console.log("time", this.startTime, this.endTime);
    },
    methods: {
      getList: function () {
        this.listLoading = true;
        getRechargeList(this.listQuery).then((response) => {
          this.list = response.items;
          this.total = response.total;
          this.total_amount = number_format(response.total_amount);
          setTimeout(() => {
            this.listLoading = false;
          }, 1.5 * 1000);
        });
      },
      getUserInfo: function () {
        var _this = this;
        var para = {
          USER_ID: _this.temp.USER_ID,
        };
        getPlayer(para).then((res) => {
          if (res.code === 20000) {
            if (res.info) {
              _this.temp.NICK_NAME = res.info.NICK_NAME;
              _this.temp.TOTAL_MONEY = res.info.TOTAL_MONEY;
            } else {
              _this.$message({
                message: "User does not exist",
                type: "error",
              });
            }
          }
        });
      },
      open: function () {
        this.temp.USER_ID = "";
        this.temp.MONEY = "";
        this.temp.TOTAL_MONEY = "";
        this.dialogFormVisible = true;
      },
      add: function () {
        var _this = this;
        _this.$refs["dataForm"].validate((valid) => {
          if (valid) {
            _this.temp.MONEY = parseInt(_this.temp.MONEY);
          } else {
            return;
          }
        });
        _this.dialogFormVisible = false;
        addRecharge(_this.temp).then((response) => {
          if (response.code === 20000) {
            _this.$message({
              message: response.message,
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
<style>
  .item-margin {
    margin-left: 5px;
    margin-right: 5px;
  }
</style>
