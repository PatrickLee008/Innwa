<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.key_word"
        placeholder="Key Word"
        style="width: 200px"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
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
      <em>Role:</em
      ><el-select
        v-model="roleselect"
        class="filter-item"
        placeholder="Please select"
      >
        <el-option
          v-for="item in roles"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      <el-button
        v-waves
        class="filter-item"
        type="primary"
        icon="el-icon-search"
        @click="handleFilter"
      >
        Search
      </el-button>
      <el-button
        v-waves
        class="filter-item item-margin"
        type="primary"
        @click="handleCreate"
      >
        Add
      </el-button>
    </div>

    <el-table
      :key="tableKey"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%"
    >
      <el-table-column type="index" width="50" />
      <el-table-column label="UserId" prop="ID" align="center" />
      <el-table-column label="Account" prop="ACCOUNT" align="center" />
      <el-table-column label="UserName" prop="NAME" align="center" />
      <el-table-column label="Role" prop="ROLES" align="center">
        <template slot-scope="{ row }">
          <span>{{ row.ROLES.STR }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Creator" prop="CREATOR" align="center" />
      <el-table-column label="Update Time" prop="CREATE_TIME" align="center" />
      <el-table-column label="Last Login" prop="LAST_LOGIN" align="center" />
      <el-table-column label="Last Login Ip" prop="IP" align="center" />
      <el-table-column
        label="Operator"
        align="center"
        class-name="small-padding fixed-width"
      >
        <template slot-scope="{ row }">
          <el-button
            type="primary"
            icon="el-icon-edit"
            circle
            @click="handleUpdate(row)"
          />
          <el-button
            icon="el-icon-delete"
            circle
            type="danger"
            @click="handleDelete(row, 'deleted')"
          />
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total > 0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="getList"
    />

    <el-dialog
      :title="textMap[dialogStatus]"
      :visible.sync="dialogFormVisible"
      custom-class="dialogwidth"
    >
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="temp"
        label-position="left"
        label-width="100px"
      >
        <div class="lb">
          <el-form-item label="Role">
            <el-checkbox-group v-model="rolesarr" class="checkGroup">
              <el-checkbox
                v-for="operate in operation"
                :key="operate.value"
                :label="operate.value"
                @change="handleChecked"
                >{{ operate.label }}</el-checkbox
              >
            </el-checkbox-group>
          </el-form-item>

          <el-form-item label="Account">
            <el-input v-model="temp.ACCOUNT" />
          </el-form-item>

          <el-form-item label="Password">
            <el-input
              v-model="temp.PASSWORD"
              placeholder="Please input"
              type="password"
            />
          </el-form-item>

          <el-form-item label="Password Confirm">
            <el-input
              v-model="REPEAT_PASSWORD"
              placeholder="Please input"
              type="password"
            />
          </el-form-item>

          <el-form-item label="UserId">
            <el-input v-model="temp.ID" placeholder="Please input" />
          </el-form-item>

          <el-form-item label="UserName">
            <el-input v-model="temp.NAME" placeholder="Please input" />
          </el-form-item>

          <el-form-item label="Group">
            <el-select v-model="temp.Withdraw_Group" placeholder="Select The Group ">
              <el-option
                v-for="item in groupList"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              >
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="Phone">
            <el-input v-model="temp.PHONE" placeholder="Please input" />
          </el-form-item>

          <el-form-item label="Remark">
            <el-input v-model="REMARK" placeholder="Please input" />
          </el-form-item>
        </div>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">Cancel</el-button>
        <el-button
          type="primary"
          @click="dialogStatus === 'create' ? createData() : updateData()"
          >Confirm</el-button
        >
      </div>
    </el-dialog>

    <el-dialog :visible.sync="dialogPvVisible" title="Reading statistics">
      <h2 style="text-align: center">
        Are you sure you want to delete this user?
      </h2>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogPvVisible = false">Cancel</el-button>
        <el-button type="primary" @click="deleteUser()">Confirm</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getGroupApi } from "@/api/financial";

import waves from "@/directive/waves"; // waves directive
import Pagination from "@/components/Pagination"; // secondary package based on el-pagination
import { getAdmin, addAdmin, editAdmin, delAdmin } from "@/api/player";
import { getRoles } from "@/api/role";
export default {
  name: "OrderList",
  components: { Pagination },
  directives: { waves },
  data() {
    return {
      startTime: "",
      endTime: "",
      betTotal: 0,
      groupList: [],
      reword: 0,
      deleteid: "",
      roleselect: "",
      roles: [
        // {
        //   value: "5",
        //   label: '全部'
        // },
        {
          value: 1,
          label: "admin",
        },
        {
          value: 2,
          label: "acc",
        },
        {
          value: 3,
          label: "hdp",
        },
        {
          value: 4,
          label: "代理商",
        },
      ],
      rolesarr: [],
      operation: [],
      REPEAT_PASSWORD: "",
      REMARK: "",
      textMap: {
        update: "Edit",
        create: "Create",
      },
      temp: {
        ROLE_ID: undefined,
        ACCOUNT: "",
        ID: undefined,
        PASSWORD: "",
        NAME: "",
        PHONE: "",
      },
      rules: {
        type: [
          { required: true, message: "type is required", trigger: "change" },
        ],
        MATCH_TIME: [
          {
            type: "date",
            required: true,
            message: "timestamp is required",
            trigger: "change",
          },
        ],
        MATCH_DESC: [
          { required: true, message: "title is required", trigger: "blur" },
        ],
      },
      dialogPvVisible: false,
      dialogFormVisible: false,
      dialogStatus: "",
      list: [],
      tableKey: 0,
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 99,
      },
    };
  },
  created() {
    this.getList();
    this.getGroupList();
    this.getRoles();
  },
  methods: {
    getGroupList() {
      var _this = this;
      _this.groupList = [];
      getGroupApi().then((res) => {
        res.items.forEach((ele) => {
          var obj = {
            label: ele.GROUP_NAME ,
            value: ele.ID,
          };
          _this.groupList.push(obj);
        });
      });
    },
    getRoles: function () {
      getRoles().then((res) => {
        // 这里转换角色格式
        res.items.forEach((element) => {
          if (element.role_id != 2) {
            this.operation.push({
              value: element.role_id,
              label: element.role_name,
            });
          }
        });
      });
    },
    getList: function () {
      this.listLoading = true;
      getAdmin().then((response) => {
        this.list = response.items;
        // this.total = response.total
        this.list.forEach((element) => {
          element.ROLES.IDARR = [];
          element.ROLES.STR = "";
          for (let i = 0; i < element.ROLES.length; i++) {
            element.ROLES.IDARR.push(element.ROLES[i].ID);
            element.ROLES.STR = element.ROLES.STR + "," + element.ROLES[i].NAME;
          }
        });
        setTimeout(() => {
          this.listLoading = false;
        }, 1.5 * 1000);
      });
    },
    handleChecked: function (element) {},
    handleFilter: function () {
      if (this.startTime !== "") {
        this.listQuery.start_time = this.startTime;
      }
      if (this.endTime !== "") {
        this.listQuery.end_time = this.endTime;
      }
      // if (this.roleselect === "5") {
      //   delete this.listQuery.role
      // } else {
      //   this.listQuery.role = this.roleselect
      // }
      this.listQuery.page = 1;
      this.getList();
    },
    resetTemp: function () {
      this.temp = {
        ROLE_ID: "",
        ACCOUNT: "",
        ID: "",
        PASSWORD: "",
        NAME: "",
        PHONE: "",
      };
      this.REPEAT_PASSWORD = "";
      this.REMARK = "";
      this.rolesarr = [];
    },
    handleCreate() {
      this.resetTemp();
      this.dialogStatus = "create";
      this.dialogFormVisible = true;
      this.$nextTick(() => {
        this.$refs["dataForm"].clearValidate();
      });
    },
    createData() {
      const _this = this;
      // this.$refs['dataForm'].validate(valid => {
      //   if (valid) {

      //   } else {
      //     return
      //   }
      // })
      const para = {
        ACCOUNT: this.temp.ACCOUNT,
        PASSWORD: this.temp.PASSWORD,
        NAME: this.temp.NAME,
        PHONE: this.temp.PHONE,
        ROLES: this.rolesarr,
        AGENT_CODE: "",
        AGENT_NAME: "",
        Withdraw_Group:this.temp.Withdraw_Group,
        SKIN: "",
        STATUS: "",
      };
      this.dialogFormVisible = false;
      addAdmin(para).then((response) => {
        _this.$message({
          message: response.message,
          type: "success",
        });
        _this.getList();
      });
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row); // copy obj

      this.dialogStatus = "update";
      this.dialogFormVisible = true;
      this.$nextTick(() => {
        this.$refs["dataForm"].clearValidate();
      });
      this.rolesarr = row.ROLES.IDARR;
    },
    updateData() {
      const para = {
        ID: this.temp.ID,
        ACCOUNT: this.temp.ACCOUNT,
        PASSWORD: this.temp.PASSWORD,
        NAME: this.temp.NAME,
        PHONE: this.temp.PHONE,
        ROLES: this.rolesarr,
        Withdraw_Group:this.temp.Withdraw_Group,
        SKIN: "",
        STATUS: "",
      };
      editAdmin(para).then((response) => {
        this.$message({
          message: response.message,
          type: "success",
        });
        this.getList();
      });
      this.dialogFormVisible = false;
    },
    handleDelete(row) {
      this.dialogPvVisible = true;
      this.deleteid = row;
    },
    deleteUser() {
      delAdmin({ ID: this.deleteid.ID }).then((response) => {
        // 编辑玩家api
        setTimeout(() => {
          this.listLoading = false;
        }, 1.5 * 1000);
      });
      this.$notify({
        title: "Success",
        message: "Delete Successfully",
        type: "success",
        duration: 2000,
      });
      const index = this.list.indexOf(this.deleteid);
      this.list.splice(index, 1);
      this.dialogPvVisible = false;
    },
  },
};
</script>
