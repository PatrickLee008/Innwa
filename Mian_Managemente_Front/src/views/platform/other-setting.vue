<template>
  <div class="app-container">
    <el-table
      :key="tableKey"
      :data="list"
      border
      fit
      highlight-current-row
      :show-header="false"
    >
      <el-table-column align="center" prop="NAME" width="220px"/>
      <el-table-column align="center">
        <template slot-scope="{ row }">
          <el-form :model="row" v-if="row.MDICT_ID==='1333'">
            <el-input
              type="textarea"
              v-show="true"
              v-model="row.CODE"
              placeholder="request token"
            />
            <el-input
              type="textarea"
              v-show="true"
              v-model="row.CONTENT"
              placeholder="request url"
            />
          </el-form>
          <el-form :model="row" v-else>
            <el-input
              type="textarea"
              v-show="true"
              v-model="row.CONTENT"
              placeholder="input content please"
            />
          </el-form>

        </template>
      </el-table-column>
      <el-table-column
        align="center"
        width="200px"
        class-name="small-padding fixed-width"
      >
        <template slot-scope="{ row }">
          <el-button type="primary" size="mini" @click="handleUpdate(row)"
          >save
          </el-button
          >
        </template>
      </el-table-column>
    </el-table>

    <el-table
      :data="updateRow"
      border
      fit
      highlight-current-row
      :show-header="false">
      <el-table-column align="center" prop="NAME" width="220px"/>
      <el-table-column>
        <template slot-scope="{ row }">
          <el-switch
            v-model="row.CODE"
            active-color="#13ce66"
            inactive-color="#ff4949"
            @change="handleUpdateMenu(row)"
          >
          </el-switch>
        </template>
      </el-table-column>
    </el-table>

    <el-table
      :data="refreshRow"
      border
      fit
      highlight-current-row
      :show-header="false">
      <el-table-column align="center" prop="NAME" width="220px"/>
      <el-table-column>
        <template slot-scope="{ row }">
          <el-button type="primary" @click="handle_refresh_order">Refresh</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
  import waves from "@/directive/waves"; // waves directive
  import {getOtherSetting, editSettings} from "@/api/order";
  import {getUpdateConfigApI, refreshHistoryOrder} from "@/api/platform";

  export default {
    name: "Pick",
    directives: {waves},
    data() {
      return {
        tableKey: 0,
        updateRow: [],
        refreshRow:[{NAME:'Refresh History Order',}],
        list: [],
        total: 0,
        listLoading: true,
        showReviewer: false,
      };
    },
    created() {
      this.getList();
    },
    methods: {
      getList: function () {
        this.listLoading = true;
        getOtherSetting().then((response) => {
          this.list = response.items;
          this.listLoading = false;
        });

        getUpdateConfigApI().then((res) => {
          this.updateRow = res.items;
          this.updateRow[0].CODE = this.updateRow[0].CODE == 1 ? true : false
        });
      },
      handleUpdateMenu: function (row) {
        let _this = this;
        let para = {
          MDICT_ID: row.MDICT_ID,
          CODE: row.CODE,
        };
        editSettings(para).then((response) => {
          this.$message({
            message: "Update Success",
            type: "success",
          });
          this.getList();
        });
      },
      handle_refresh_order: function (row) {
        let _this = this;
        let para = {};
        refreshHistoryOrder(para).then((response) => {
          let message = 'Refresh history Success'
          let type = 'success'
          if (response.code !== 20000) {
            message = 'Refresh history Fail!'
            type = 'fail'
          }
          _this.$message({
            message: message,
            type: type,
          });
        });
      },
      handleUpdate: function (row) {
        const _this = this;
        if (row.CONTENT === "") {
          _this.$message({
            message: "Content Cannot Be Null",
            type: "fail",
          });
          return;
        }
        let para = {
          MDICT_ID: row.MDICT_ID,
          CONTENT: row.CONTENT,
        };
        if(row.MDICT_ID =='1333'){
          para.CODE = row.CODE
        }
        editSettings(para).then((response) => {
          _this.$message({
            message: "Update Success",
            type: "success",
          });
          _this.getList();
        });
      },
    },
  };
</script>
