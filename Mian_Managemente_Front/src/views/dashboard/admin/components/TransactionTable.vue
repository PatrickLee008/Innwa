<template>
  <el-table v-loading="loading" :data="list" style="width: 100%;padding-top: 15px;">
    <el-table-column label="UserId" align="center" prop="USER_ID"></el-table-column>
    <el-table-column label="UserName" align="center" prop="USER_NAME"></el-table-column>
    <el-table-column label="Order Number" align="center" prop="ORDER_ID"></el-table-column>
    <el-table-column label="Order Type" align="center">
      <template slot-scope="{row}">{{orderType[row.ORDER_TYPE]}}</template>
    </el-table-column>
    <el-table-column label="Amount" prop="BET_MONEY"></el-table-column>
  </el-table>
</template>

<script>
import { getLatestOrders } from "@/api/order";

export default {
  data() {
    return {
      loading: false,
      orderType: ["B_Body", "B_Goal", "M_Body", "M_Goal"],
      list: []
    };
  },
  created() {
    this.getList();
  },
  methods: {
    getList() {
      var _this = this;
      _this.loading = true;
      getLatestOrders({ pageSize: 6 }).then(res => {
        if (res.code === 20000) {
          _this.list = res.items;
          _this.loading = false;
        }
      });
    }
  }
};
</script>
