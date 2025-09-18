<template>
  <div class="app-container">
    <div class="filter-container">
      <el-row>
        <el-col :span="12">
          <em>Keyword：</em>
          <el-input
            v-model="listQuery.key_word"
            placeholder="key word"
            style="width: 200px;"
            class="filter-item"
          />
          <el-select v-model="listQuery.is_finished" @change="getList" placeholder="">
            <el-option label="Unfinish" :value="0"></el-option>
            <el-option label="Finished" :value="1"></el-option>
          </el-select>
          <el-button
            class="filter-item"
            type="primary"
            icon="el-icon-search"
            @click="handleFilter"
          >Search
          </el-button>
        </el-col>
        <el-col :span="12" align="right">

          <span>Status:{{autoswitch? 'Start':'Pause'}}<el-switch v-model="autoswitch" active-color="#13ce66"
                                                                   @change="setSwitch"
                                                                   inactive-color="#ff4949"></el-switch></span>
<!--          <el-button icon="el-icon-thirdbofang" @click="openConfirmDia(true)" type="primary">Start all</el-button>-->
<!--          <el-button icon="el-icon-thirdzanting" @click="openConfirmDia(false)" type="danger">Stop all</el-button>-->
          <!--          <el-popover-->
          <!--            placement="top"-->
          <!--            width="160"-->
          <!--            v-model="popover">-->
          <!--            <p>Do you want to settle all match in the list？</p>-->
          <!--            <div style="text-align: right; margin: 0">-->
          <!--              <el-button size="mini" type="text" @click="popover = false">Cancel</el-button>-->
          <!--              <el-button type="primary" size="mini" @click="startAllSettlement,popover = false">Confirm</el-button>-->
          <!--            </div>-->
          <!--            <el-button slot="reference" type="primary">Seattle all</el-button>-->
          <!--          </el-popover>-->
          <!--          <el-popover-->
          <!--            placement="top"-->
          <!--            width="160"-->
          <!--            v-model="popover2">-->
          <!--            <p>Do you want to stop settling all match in the list？</p>-->
          <!--            <div style="text-align: right; margin: 0">-->
          <!--              <el-button size="mini" type="text" @click="popover2 = false">Cancel</el-button>-->
          <!--              <el-button type="primary" size="mini" @click="startAllSettlement,popover = false">Confirm</el-button>-->
          <!--            </div>-->
          <!--            <el-button slot="reference" type="danger">Stop all</el-button>-->
          <!--          </el-popover>-->
        </el-col>
      </el-row>
    </div>


    <el-table
      :key="tableKey"
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%;">
      <el-table-column type="index" width="50"/>
      <el-table-column label="Match Number" prop="MATCH_ID" align="center" width="100px"/>
      <el-table-column label="Match Desc" prop="MATCH_DESC" max-width="8%" align="center"/>
      <el-table-column label="League" prop="REMARK" max-width="6%" align="center"/>
      <el-table-column label="Status" prop="STATUS" :formatter="tableFormatter" width="100px" align="center"/>
      <el-table-column label="Type" prop="SETTLE_TYPE" :formatter="tableFormatter" width="100px" align="center"/>
      <el-table-column label="Create time" prop="CREATE_TIME" max-width="8%" align="center"/>
      <el-table-column label="Operation" align="center" class-name="small-padding fixed-width" width="300px">
        <template slot-scope="scope">
<!--          <el-button-->
<!--            type="primary"-->
<!--            v-if="scope.row.STATUS===0||scope.row.STATUS===2"-->
<!--            circle-->
<!--            size="medium"-->
<!--            icon="el-icon-thirdbofang"-->
<!--            @click="startSettlement(scope.row)"></el-button>-->
<!--          <el-button-->
<!--            type="warning"-->
<!--            v-if="scope.row.STATUS===1"-->
<!--            size="medium"-->
<!--            circle-->
<!--            icon="el-icon-thirdzanting"-->
<!--            @click="stopSettlement(scope.row)"></el-button>-->
          <el-popover
            placement="top"
            v-if="!(scope.row.STATUS===3)"
            :ref="`popover-${scope.$index}`">
            <p>Wanner delete this item!？</p>
            <div style="text-align: center; margin: 0">
              <el-button type="primary" size="mini"
                         @click="removeSettle(scope.row),scope._self.$refs[`popover-${scope.$index}`].doClose()">
                Confirm
              </el-button>
            </div>
            <el-button icon="el-icon-delete" circle size="medium" type="danger" slot="reference"></el-button>
          </el-popover>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      title="Add Settle"
      :visible.sync="dialogFormVisible"
      style="width: 100%;"
      custom-class="dialogwidth">
      <div class="filter-container">
        <el-row>
          <el-col :span="20">
            <em>Settle List：</em>
            <span v-for="name in names" @click="DelSettleListData">{{name}}</span>
          </el-col>
          <el-button type="primary" @click="addSettle">Add Settle</el-button>
        </el-row>
        <el-form
          :model="form"
          label-position="left"
          label-width="80px">
          <div class="lb">
            <el-form-item label="Remark:">
              <el-input placeholder="Remark" v-model="form.Remark"></el-input>
            </el-form-item>
          </div>
        </el-form>
        <el-divider><i class="el-icon-search"></i></el-divider>
        <el-row>
          <el-col :span="8">
            <em>Keyword：</em>
            <el-input
              v-model="listQuery2.key_word"
              placeholder="使用人姓名"
              style="width: 200px;"
              class="filter-item"
            />
          </el-col>
          <el-col :span="8">
            <el-button type="primary" @click="handleFilter2">Search</el-button>
            <el-button type="info" @click="resetList">Reset List</el-button>
          </el-col>
        </el-row>
        <el-table
          ref="multipleTable"
          v-loading="listLoading2"
          :data="list2"
          :row-key="getRowKey"
          @selection-change="handleSelectionChange">
          <el-table-column type="selection" :reserve-selection="true" width="55"></el-table-column>
          <el-table-column type="index" width="50"/>
          <el-table-column label="Match Number" prop="MATCH_ID" align="center" width="100px"/>
          <el-table-column label="Match Desc" prop="MATCH_DESC" max-width="8%" align="center"/>
          <el-table-column label="Time" prop="MATCH_TIME" width="95px" align="center"/>
          <el-table-column label="Time(Myanmar)" prop="MATCH_MD_TIME" width="95px" align="center"/>
          <el-table-column label="Home" prop="HOST_TEAM" max-width="6%" align="center"/>
          <el-table-column label="Away" prop="GUEST_TEAM" max-width="6%" align="center"/>
          <el-table-column label="Closing Time" prop="CLOSING_TIME" width="95px" align="center"/>
          <el-table-column label="Status" max-width="4%" align="center">
            <template slot-scope="{row}">
              <span>{{ row.CLOSING_STATE==1?'Closed':'Unsealed' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="League" prop="REMARK" max-width="6%" align="center"/>
          <el-table-column label="Create Time" prop="CREATE_TIME" width="95px" align="center"/>
          <el-table-column label="Update Time" prop="UPDATE_TIME" width="95px" align="center"/>
          <el-table-column label="Home Score" prop="HOST_TEAM_RESULT" width="80px" align="center"/>
          <el-table-column label="Away Score" prop="GUEST_TEAM_RESULT" width="80px" align="center"/>
          <el-table-column label="VIP" width="50px" align="center">
            <template slot-scope="{row}">
              <span v-if="row.VIP_ATTR.length>0">Yes</span>
              <span v-else>No</span>
            </template>
          </el-table-column>
          <el-table-column label="Finished" width="80px" align="center">
            <template slot-scope="{row}">
              <span>{{ row.IS_GAME_OVER==1?'Finished':'Unfinished' }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <pagination
        v-show="total2>0"
        :total="total2"
        :page.sync="listQuery2.page"
        :page-sizes="[20,50,99]"
        :page-size="20"
        :limit.sync="listQuery2.limit"
        @pagination="getMatchList"
      />
    </el-dialog>
    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="listQuery.page"
      :page-sizes="[20,50,99]"
      :page-size="99"
      :limit.sync="listQuery.limit"
      @pagination="getList"
    />
  </div>
</template>

<script>
  import Pagination from "@/components/Pagination/index"; // secondary package based on el-pagination
  import {
    getMatchSettleList,
    addMatchSettle,
    removeMatchSettle,
    startAllMatchSettle,
    startMatchSettle,
    stopAllMatchSettle,
    stopMatchSettle,
    getMatchList,
    getSettleSwitch,
    setSettleSwitch
  } from "@/api/match";
  import Vue from "vue";

  export default {
    components: {Pagination},
    data() {
      return {
        rules: {},
        options: [],
        value: [],
        radio: "",
        loading: false,
        popover: false,
        popover2: false,
        dialogFormVisible: false,
        editFormVisible: false,
        selectRow: [],
        form: {
          Remark: null,
          TaskName: null,
        },
        startTime: "",
        endTime: "",
        total: 0,
        list: [],
        total2: 0,
        list2: [],
        tableKey: 0,
        listLoading: false,
        listLoading2: false,
        ids: [],
        autoswitch: false,
        names: [],
        selectionList: [],
        permission: {},
        routeID: 59,
        listQuery: {
          page: 1,
          limit: 99,
          start_time: null,
          end_time: null,
          is_finished:0,
        },
        listQuery2: {
          page: 1,
          limit: 20,
        }
      };
    },
    created() {
      this.getList();
      this.getSwitch();
    },
    mounted() {
      // this.permission = getPermission(this.routeID)
    },
    methods: {
      getList() {
        // var para = {
        //   current_page: this.listQuery.page,
        //   limit: this.listQuery.limit
        // };
        this.listLoading = true;
        getMatchSettleList(this.listQuery).then(response => {
          this.listLoading = false;
          this.list = response.items;
          this.total = response.total;
        });
      },
      getSwitch() {
        getSettleSwitch().then(response => {
          this.autoswitch = response.settle_switch
        });
      },
      tableFormatter(row, column, cellValue, index) {
        if (column.property == "STATUS") {
          switch (row.STATUS) {
            case 1:
              return "Waiting";
            case 2:
              return "Pause";
            case 3:
              return "Settling";
            case 4:
              return "Finished";
          }
        } else if (column.property == "SETTLE_TYPE") {
          switch (row.SETTLE_TYPE) {
            case 0:
              return "Settle";
            case 1:
              return "Cancel";
            case 2:
              return "Reverse";
          }
        }
      },
      getMatchList() {
        var _this = this;
        _this.listLoading2 = true;
        getMatchList(_this.listQuery2).then((res) => {
          if (res.code === 20000) {
            _this.listLoading2 = false;
            _this.list2 = res.items;
            _this.total2 = res.total;
          }
        });
      },
      removeSettle(row) {
        var _this = this;
        const loading = this.$loading({
          lock: true,
          text: "Loading",
          spinner: "el-icon-loading",
          background: "rgba(0, 0, 0, 0.7)"
        });
        removeMatchSettle({remove_id: row.ID}).then(res => {
          if (res.code == 20000) {
            this.$message({
              message: res.message,
              type: "success"
            });
            _this.getList();
          }
        });
        loading.close();
        _this.dialogFormVisible = false;
      },
      openConfirmDia(Is_start) {
        var cont = Is_start ? 'Do you want to settle all match in the list？' : 'Do you want to stop settling all match in the list？'
        this.$confirm(cont, 'Tips', {
          cancelButtonText: 'Cancel',
          confirmButtonText: 'Confirm',
          type: Is_start ? 'success' : 'error'
        }).then(() => {
          Is_start ? this.startAllSettlement() : this.stopAllSettlement()
        }).catch(() => {
          this.$message({
            type: 'info',
            message: 'Canceled!',
            duration: 1000,
          });
        });
      },
      setSwitch(val) {
        var _this = this;
        setSettleSwitch({switch:val}).then(res => {
          if (res.code == 20000) {
            _this.$message({
              message: res.message,
              type: "success"
            });
          }
          else {
            _this.$message({
              message: res.message,
              type: "error"
            });
          }
          _this.getList();
          _this.getSwitch();
        });
      },
      addSettle() {
        var _this = this;
        var para = {
          TaskType: _this.form.TaskType,
          Remark: _this.form.Remark,
          ids: _this.ids
        };
        if (_this.ids.length > 0 && _this.form.TaskType) {
          const loading = _this.$loading({
            lock: true,
            text: "Loading",
            spinner: "el-icon-loading",
            background: "rgba(0, 0, 0, 0.7)"
          });
          addMatchSettle(para).then(res => {
            if (res.code == 20000) {
              _this.$message({
                message: res.message,
                type: "success"
              });
              _this.getList();
              _this.resetList()
            }
          });
          loading.close();
          _this.dialogFormVisible = false;
        } else {
          _this.$message({
            message: "Settle list is null!!",
            type: "error"
          });
        }
      },
      startSettlement(row) {
        var _this = this;
        const loading = this.$loading({
          lock: true,
          text: "Loading",
          spinner: "el-icon-loading",
          background: "rgba(0, 0, 0, 0.7)"
        });
        startMatchSettle({start_id: row.ID,}).then(res => {
          if (res.code == 20000) {
            this.$message({
              message: res.message,
              type: "success"
            });
            _this.getList();
          }
        });
        loading.close();
      },
      stopSettlement(row) {
        var _this = this;
        const loading = this.$loading({
          lock: true,
          text: "Loading",
          spinner: "el-icon-loading",
          background: "rgba(0, 0, 0, 0.7)"
        });
        stopMatchSettle({stop_id: row.ID,}).then(res => {
          if (res.code == 20000) {
            this.$message({
              message: res.message,
              type: "success"
            });
            _this.getList();
          }
        });
        loading.close();
      },
      startAllSettlement() {
        var _this = this;
        const loading = this.$loading({
          lock: true,
          text: "Loading",
          spinner: "el-icon-loading",
          background: "rgba(0, 0, 0, 0.7)"
        });
        startAllMatchSettle().then(res => {
          if (res.code == 20000) {
            this.$message({
              message: res.message,
              type: "success"
            });
            _this.getList();
            _this.getSwitch();
          }
        });
        loading.close();
      },
      stopAllSettlement() {
        var _this = this;
        const loading = this.$loading({
          lock: true,
          text: "Loading",
          spinner: "el-icon-loading",
          background: "rgba(0, 0, 0, 0.7)"
        });
        stopAllMatchSettle().then(res => {
          if (res.code == 20000) {
            this.$message({
              message: res.message,
              type: "success"
            });
            _this.getList();
            _this.getSwitch();
          }
        });
        loading.close();
      },
      handleFilter() {
        if (this.startTime !== "") {
          this.listQuery.start_time = this.startTime;
        }
        if (this.endTime !== "") {
          this.listQuery.end_time = this.endTime;
        }
        this.listQuery.page = 1;
        this.getList();
      },
      handleFilter2() {
        if (this.startTime !== "") {
          this.listQuery2.start_time = this.startTime;
        }
        if (this.endTime !== "") {
          this.listQuery2.end_time = this.endTime;
        }
        this.listQuery2.page = 1;
        this.getMatchList();
      },
      addIDsToList() {
        var notExis = true
        this.selectionList.forEach(ele => {
          notExis = true
          this.ids.forEach(el => {
            if (ele.ID === el) {
              notExis = false
            } else {
            }
          })
          if (notExis) {
            this.ids.push(ele.ID)
            this.names.push(ele.FullName)
          }
        })
      },
      resetList() {
        this.ids = []
        this.names = []
        this.form = {}
        this.$refs.multipleTable.clearSelection();
      },
      DelSettleListData(val) {
        var index = this.names.indexOf(val.target.innerHTML)
        if (index > -1) {
          this.names.splice(index, 1);
          this.ids.splice(index, 1);
        }
      },
      getRowKey(row) {
        return row.ID
      },
      handleSelectionChange(row) {
        var _this = this;
        _this.ids = []
        _this.names = []
        row.forEach((ele) => {
          if (_this.ids.indexOf(ele.ID) < 0) {
            _this.ids.push(ele.ID)
            _this.names.push(ele.FullName)
          }
        })
      },
    }
  };
</script>
