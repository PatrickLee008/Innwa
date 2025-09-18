<template>
  <el-table :data="list" v-loading="loading" style="width: 100%;padding-top: 15px;">
    <el-table-column label="UserId" prop="USER_ID"></el-table-column>
    <el-table-column label="UserName" align="center" prop="NICK_NAME"></el-table-column>
    <el-table-column label="Charge Amount" align="center" prop="MONEY"></el-table-column>
    <el-table-column label="Charge Time" align="center" prop="CREATOR_TIME"></el-table-column>
  </el-table>
</template>

<script>
import { getLatestChargeList } from "@/api/financial";

export default {
  data() {
    return {
      loading: false,
      list: null
    };
  },
  created() {
    this.getList();
  },
  methods: {
    getList() {
      var _this = this;
      _this.loading = true;
      getLatestChargeList({ pageSize: 6 }).then(res => {
        if (res.code === 20000) {
          _this.loading = false;
          _this.list = res.items;
        }
      });
    }
  }
};
</script>
