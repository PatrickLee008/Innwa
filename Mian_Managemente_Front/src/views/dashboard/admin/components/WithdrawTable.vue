<template>
  <el-table v-loading="loading" :data="list" style="width: 100%;padding-top: 15px;">
    <el-table-column label="UserId" prop="USER_ID"></el-table-column>
    <el-table-column label="UserName" align="center" prop="NICK_NAME"></el-table-column>
    <el-table-column label="Amount" align="center" prop="MONEY"></el-table-column>
    <el-table-column label="Status" align="center">
      <template slot-scope="{row}">
        {{ row.status ===0?"paid":"Unpaid"}}
      </template>
    </el-table-column>
  </el-table>
</template>

<script>
import { getLatestWithDrawList } from "@/api/financial";

export default {
  data() {
    return {
      list: [],
      loading: false
    };
  },
  created() {
    this.getList()
  },
  methods: {
    getList(){
      var _this = this;
      _this.loading = true;
      getLatestWithDrawList({pageSize:6}).then(res=>{
        if(res.code===20000){
          _this.loading = false;
          _this.list = res.items;
        }
      })
    }
  }
};
</script>
