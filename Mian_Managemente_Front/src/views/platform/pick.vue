<template>
  <div class="app-container">
    <el-table
      :key="tableKey"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%"
      :show-header="false"
    >
      <el-table-column align="center" prop="NAME" width="220px" />
      <el-table-column align="center">
        <template slot-scope="{ row }">
          <el-form :model="row">
            <el-input
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
          <el-button type="primary" size="mini" @click="handleUpdate(row)">
            save
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <h2>Filter Leagues</h2>
    <div style="margin:5px 0;">
      <el-button type="primary" @click="addFilterLeague()">
        Add Filter League
      </el-button>
      <el-button type="primary" @click="saveFilterLeague()"> Save </el-button>
    </div>

    <el-table
      :data="filterLeagusList"
      border
      fit
      highlight-current-row
      style="width: 100%"
      :show-header="false"
    >
      <el-table-column type="index" width="50" />
      <el-table-column
        align="center"
        label="league name"
        prop="name"
        width="220px"
      >
        <template slot-scope="{ row }">
          <span v-if="!row.isEdit">{{ row.name }}</span>
          <el-input v-if="row.isEdit" v-model="row.name" />
        </template>
      </el-table-column>
      <el-table-column
        align="center"
        width="200px"
        class-name="small-padding fixed-width"
      >
        <template slot-scope="{ row }">
          <el-button type="danger" size="mini" @click="deleteFilterLeague(row)">
            delete
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import waves from "@/directive/waves"; // waves directive
import { getPick, editSettings } from "@/api/order";

export default {
  name: "Pick",
  directives: { waves },
  data() {
    return {
      tableKey: 0,
      list: [],
      total: 0,
      listLoading: true,
      showReviewer: false,
      filterLeagusList: [],
    };
  },
  created() {
    this.getList();
  },
  methods: {
    saveFilterLeague() {
      var content = "";
      this.filterLeagusList.forEach((ele,index) => {
          content += ele.name.replaceAll('\t ','').trim();
          if(index != this.filterLeagusList.length-1){
            content +=  ",";
          }
      });
      const para = {
        MDICT_ID: 41,
        CONTENT: content,
      };
      editSettings(para).then((response) => {
        this.$message({
          message: response.message,
          type: "success",
        });
        this.getList();
      });
    },
    deleteFilterLeague(row) {
      this.filterLeagusList.forEach((ele, index) => {
        if (ele.name == row.name) {
          this.filterLeagusList.splice(index, 1);
        }
      });
    },
    addFilterLeague() {
      this.filterLeagusList.push({ isEdit: true, name: "" });
    },
    getList: function () {
      this.listLoading = true;
      var _this = this;
      getPick().then((response) => {
        _this.list = [];
        response.items.forEach((element) => {
          if (element.MDICT_ID == "41") {
            _this.filterLeagusList = [];
            var tempArr = element.CONTENT.replaceAll('\t ','').split(",");
            tempArr.forEach((item) => {
              var obj = {
                isEdit:false,
                name: item,
              };
              _this.filterLeagusList.push(obj);
            });
            // console.log(_this.filterLeagusList);
            _this.filterLeagusList.sort((a,b)=>{
              return a.name.charCodeAt(0) - b.name.charCodeAt(0);
            })
            // console.log(_this.filterLeagusList);
          } else {
            _this.list.push(element);
          }
        });
        _this.listLoading = false;
      });
    },
    handleUpdate: function (row) {
      const _this = this;
      if (row.CONTENT === "") {
        _this.$message({
          message: "输入内容不能为空",
          type: "fail",
        });
        return;
      }
      let para = {}
      if(row.MDICT_ID == "41"){
        para = {
          MDICT_ID: row.MDICT_ID,
          CONTENT: row.CONTENT.replaceAll('\t','').replace(/[^A-Za-z0-9 ]/g, '').trim(),
        };
      }else{
        para = {
        MDICT_ID: row.MDICT_ID,
        CONTENT: row.CONTENT,
      };
      }

      editSettings(para).then((response) => {
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
