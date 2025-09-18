<template>
  <div class="app-container">
    <el-button type="primary" @click="handleAddRole">New Role</el-button>

    <el-table v-loading="loading" :data="rolesList" style="width: 100%;margin-top:30px;" border>
      <el-table-column align="center" label="Role Key" width="220">
        <template slot-scope="scope">{{ scope.row.role_id }}</template>
      </el-table-column>
      <el-table-column align="center" label="Role Name" width="220">
        <template slot-scope="scope">{{ scope.row.role_name }}</template>
      </el-table-column>
      <el-table-column align="header-center" label="Description">
        <template slot-scope="scope">{{ scope.row.description }}</template>
      </el-table-column>
      <el-table-column align="center" label="Operations">
        <template slot-scope="scope">
          <div>
            <el-button type="primary" size="small" @click="handleEdit(scope.row)">Edit</el-button>
            <el-button type="danger" size="small" @click="handleDelete(scope)">Delete</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog :visible.sync="dialogVisible" :title="dialogType==='edit'?'Edit Role':'New Role'">
      <el-form :model="role" label-width="80px" label-position="left">
        <el-form-item label="Name">
          <el-input v-model="role.role_name" placeholder="Role Name" />
        </el-form-item>
        <el-form-item label="Desc">
          <el-input
            v-model="role.description"
            :autosize="{ minRows: 2, maxRows: 4}"
            type="textarea"
            placeholder="Role Description"
          />
        </el-form-item>

        <el-form-item label="Menus">
          <el-row v-for="(item,key) in routes" :key="key" :name="key">
            <el-row style="border-bottom:1px solid lightgrey;margin-top:15px;">
              <el-col :span="12">
                <!--
                  <el-checkbox
                    v-model="_item.checked"
                    @change="routeSelectChange(_item,$event)"
                  >{{ _item.title }}</el-checkbox>
                -->
                <label>{{ item.title }}</label>
              </el-col>
            </el-row>

            <el-row v-for="(_item,_key) in item.children" :key="_key" style="margin-left:12px;">
              <el-col :span="12">
                <!--
                  <el-checkbox
                    v-model="_item.checked"
                    @change="routeSelectChange(_item,$event)"
                  >{{ _item.title }}</el-checkbox>
                -->
                <input
                  v-model="_item.checked"
                  type="checkbox"
                  @change="routeSelectChange(_item,item,key)"
                />
                <label>{{ _item.title }}</label>
              </el-col>
              <el-col :span="12">
                <el-col :span="6">
                  <input v-model="_item.add" type="checkbox" />
                  <label>Add</label>
                </el-col>
                <el-col :span="6">
                  <input v-model="_item.del" type="checkbox" />
                  <label>Delete</label>
                </el-col>
                <el-col :span="6">
                  <input v-model="_item.edit" type="checkbox" />
                  <label>Edit</label>
                </el-col>
                <el-col :span="6">
                  <input v-model="_item.query" type="checkbox" />
                  <label>Query</label>
                </el-col>
              </el-col>
            </el-row>
          </el-row>
        </el-form-item>
      </el-form>
      <div style="text-align:right;">
        <el-button type="danger" @click="dialogVisible=false">Cancel</el-button>
        <el-button type="primary" :loading="updating" @click="submit">Confirm</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getRoles, addRole, deleteRole, updateRole } from "@/api/role";
import { getMenuList } from "@/api/route";

const defaultRole = {
  key: "",
  name: "",
  description: "",
  routes: [],
};

export default {
  data() {
    return {
      activeNames: [0, 1, 2, 3, 4],
      updating: false,
      role: Object.assign({}, defaultRole),
      routes: [],
      loading: false,
      rolesList: [],
      dialogVisible: false,
      dialogType: "new",
      checkStrictly: false,
      selectRoutes: [],
    };
  },
  computed: {
    routesData() {
      return this.routes;
    },
  },
  created() {
    // Mock: get all routes and roles list from server
    this.getRoles();
    this.getRoutes();
    // console.log("store:"+JSON.stringify(this.$store.getters.routes));
  },
  methods: {
    // 二级菜单选中事件
    routeSelectChange(row, item, index) {
      // 如果是选中 , 判断已选中的列表有没有改路由, 没有则加入
      // 如果是取消选中 , 判断列表有没有该路由, 有则删除

      // 如果取消,则增删改查也设置为取消
      if (!row.checked) {
        row.add = false;
        row.edit = false;
        row.query = false;
        row.del = false;
      }
      // 如果选中, 则增删改查也设置选中
      else {
        row.add = true;
        row.edit = true;
        row.query = true;
        row.del = true;
      }
      this.$set(this.routes, index, item);
    },

    submit() {
      this.updating = true;
      var _this = this;

      _this.selectRoutes.length = 0;

      _this.routes.forEach((route) => {
        var add = false;
        route.children.forEach((chi) => {
          if (chi.checked) {
            add = true;
            _this.selectRoutes.push(chi);
          }
        });
        if (add) {
          var temp = Object.assign({}, route);
          _this.selectRoutes.push(temp);
        }
      });

      var para = {
        role_id: this.role.role_id,
        DESCRIPTION: this.role.description,
        NAME: this.role.role_name,
        routes: {},
      };

      // debugger;
      this.selectRoutes.forEach((element) => {
        para.routes[element.ID] = [
          element.add,
          element.del,
          element.edit,
          element.query,
        ];
      });

      if (this.dialogType === "edit") {
        updateRole(para).then((res) => {
          this.$message({
            type: "success",
            message: "update success!",
          });
          _this.updating = false;
          _this.dialogVisible = false;
          _this.getRoles();
        });
      } else {
        addRole(para).then((res) => {
          this.$message({
            type: "success",
            message: "add success!",
          });
          _this.updating = false;
          _this.dialogVisible = false;
          _this.getRoles();
        });
      }
    },

    getRoutes() {
      var _this = this;
      getMenuList().then((res) => {
        _this.routes = res.items;
      });
    },
    getRoles() {
      var _this = this;
      _this.loading = true;
      getRoles().then((res) => {
        _this.rolesList = res.items;
        _this.loading = false;
      });
    },

    handleAddRole() {
      this.role = Object.assign({}, defaultRole);

      // 新建的角色 , 清除所有选中权限
      this.routes.forEach((element) => {
        element.children.forEach((chi) => {
          chi.checked = false;
          chi.add = false;
          chi.del = false;
          chi.edit = false;
          chi.query = false;
        });
      });

      this.dialogType = "new";
      this.dialogVisible = true;
    },
    handleEdit(row) {
      var _this = this;
      this.role = Object.assign({}, row);

      this.routes.forEach((route) => {
        route.children.forEach((chi) => {
          chi.checked = false;
          chi.add = false;
          chi.del = false;
          chi.edit = false;
          chi.query = false;
        });
      });

      this.routes.forEach((route) => {
        route.children.forEach((chi) => {
          _this.role.routes.forEach((_route) => {
            if (_route.ROUTE_ID === chi.ID) {
              chi.checked = true;
              chi.add = _route.PERMISSION[0];
              chi.del = _route.PERMISSION[1];
              chi.edit = _route.PERMISSION[2];
              chi.query = _route.PERMISSION[3];
            }
          });
        });
      });

      this.dialogType = "edit";
      this.dialogVisible = true;
      this.checkStrictly = true;
    },
    handleDelete({ $index, row }) {
      this.$confirm("Confirm to remove the role?", "Warning", {
        confirmButtonText: "Confirm",
        cancelButtonText: "Cancel",
        type: "warning",
      })
        .then(async () => {
          //await deleteRole(row.key)
          var para = { role_id: row.role_id };
          deleteRole(para).then((res) => {
            if (res.code === 20000) {
              this.rolesList.splice($index, 1);
              this.$message({
                type: "success",
                message: "Delete succed!",
              });
            }
          });
        })
        .catch((err) => {
          console.error(err);
        });
    },
  },
};
</script>

<style lang="scss" scoped>
.app-container {
  .roles-table {
    margin-top: 30px;
  }
  .permission-tree {
    margin-bottom: 30px;
  }
}
.permission_bar {
  div {
    float: left;
    margin-right: 12px;
  }
}
input[type="checkbox"] {
  width: 15px;
  height: 15px;
}
</style>
