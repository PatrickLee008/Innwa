<template>
  <div class="app-container">
    <div class="filter-container" />

    <el-table
      :key="tableKey"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%;"
      :show-header="false"
    >
      <el-table-column prop="NAME" align="center" width="220px" />
      <el-table-column align="center">
        <template slot-scope="{row}">
          <el-form :model="row">
            <el-input v-show="true" v-model="row.CONTENT" placeholder="input content please" />
          </el-form>
        </template>
      </el-table-column>
      <el-table-column align="center" width="200px" class-name="small-padding fixed-width">
        <template slot-scope="{row}">
          <el-button type="primary" size="mini" @click="handleUpdate(row)">save</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import waves from "@/directive/waves"; // waves directive
import { getcommission, editSettings } from "@/api/order";

export default {
  name: "CommissionRate",
  directives: { waves },
  data() {
    return {
      tableKey: 0,
      list: [],
      listLoading: true,
      closeStatus: [],
      showReviewer: false
    };
  },
  created() {
    this.getList();
  },
  methods: {
    getList: function() {
      this.listLoading = true;
      getcommission().then(response => {
        this.list = response.items;
        setTimeout(() => {
          this.listLoading = false;
        }, 1.5 * 1000);
      });
    },
    handleUpdate: function(row) {
      const _this = this;
      if (row.CONTENT === "") {
        _this.$message({
          message: "输入比例不能为空",
          type: "fail"
        });
        return;
      }
      const para = {
        MDICT_ID: row.MDICT_ID,
        CONTENT: row.CONTENT
      };
      editSettings(para).then(response => {
        this.$message({
          message: response.message,
          type: "success"
        });
        this.getList();
      });
    }
  }
};
</script>
