<template>
  <div class="app-container">
    <div class="filter-container">
      <el-button class="filter-item item-margin" type="primary" @click="handleCreate">Add</el-button>
    </div>

    <el-table
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%;"
    >
      <el-table-column type="index" width="50" />
      <el-table-column label="Group Name" prop="GROUP_NAME" align="center" />
      <el-table-column label="Remark" prop="REMARK" align="center" />
      <el-table-column label="NOW_HANDLE" prop="NOW_HANDLE" align="center" />
      <el-table-column label="MAX_HANDLE" prop="MAX_HANDLE" align="center" />
      <el-table-column label="Create Time" prop="CREATE_TIME" align="center" />
      <el-table-column label="Enable" prop="HANDLE_ON" align="center">
        <template slot-scope="scope">
          <el-switch disabled v-model="scope.row.HANDLE_ON" active-color="#13ce66" inactive-color="#ff4949" />
        </template>
      </el-table-column>
      <el-table-column label="Operate" align="center" class-name="small-padding fixed-width">
        <template slot-scope="{row}">
          <el-button type="primary" icon="el-icon-edit" circle @click="handleUpdate(row)" />
          <el-button icon="el-icon-delete" circle type="danger" @click="removeGroup(row)" />
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="getList"
    />

    <el-dialog title="Add Group" :visible.sync="dialogFormVisible" :close-on-click-modal="false">
      <el-form :model="temp" label-position="right" label-width="150px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Group Name">
              <el-input v-model="temp.GROUP_NAME " />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-form-item label="Limit">
              <el-input v-model="temp.MAX_HANDLE" @input="temp.LIMIT=temp.LIMIT.replace(/\D/g,'')"/>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-form-item label="Enable">
              <el-switch  v-model="temp.HANDLE_ON" active-color="#13ce66" inactive-color="#ff4949"></el-switch>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-form-item label="Remark">
              <el-input v-model="temp.REMARK" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button type="primary" @click="submit">Submit</el-button>
          <el-button @click="exit">Cancel</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script>
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import {
  getGroupApi,
  addGroupApi,
  editGroupApi,
  removeGroupApi
} from '@/api/financial'
import { dateToString2 } from '@/utils/date-format'
export default {
  components: { Pagination },
  data() {
    return {
      listLoading: false,
      list: [],
      total: 0,
      listQuery: {
        page: 0,
        limit: 0
      },
      operate: 'add',
      temp: {
        Name: '',
        Remark: ''
      },
      dialogFormVisible: false,
      loading: {}
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList: function() {
      var _this = this
      _this.listLoading = true

      getGroupApi({}).then(res => {
        _this.listLoading = false
        if (res.code === 20000) {
          _this.list = res.items
        }
      })
    },
    handleUpdate(row) {
      this.operate = 'update'
      this.temp = Object.assign({}, row)
      this.dialogFormVisible = true
    },
    submit() {
      if (this.operate == 'add') {
        this.addGroup()
      } else {
        this.updateGroup()
      }
    },
    updateGroup() {
      var _this = this

      const loading = this.$loading({
        lock: true,
        text: 'Loading',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)'
      })

      delete _this.temp.CREATE_TIME
      delete _this.temp.CREATOR
      delete _this.temp.UPDATE_TIME

      editGroupApi(_this.temp).then(res => {
        loading.close()
        if (res.code === 20000) {
          _this.$message({
            message: 'Update Group Success!',
            type: 'success'
          })
          _this.getList()
          _this.dialogFormVisible = false
        }
      })
    },
    addGroup() {
      var _this = this

      const loading = this.$loading({
        lock: true,
        text: 'Loading',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)'
      })

      addGroupApi(_this.temp).then(res => {
        loading.close()
        if (res.code === 20000) {
          _this.$message({
            message: 'Add Group Success!',
            type: 'success'
          })
          _this.getList()
          _this.dialogFormVisible = false
        }
      })
    },
    removeGroup(row) {
      var _this = this

      this.$confirm('Are you sure to permanently delete this record?', 'Tips', {
        confirmButtonText: 'Yes',
        cancelButtonText: 'Cancel',
        type: 'warning'
      })
        .then(() => {
          const loading = this.$loading({
            lock: true,
            text: 'Loading',
            spinner: 'el-icon-loading',
            background: 'rgba(0, 0, 0, 0.7)'
          })
          removeGroupApi({ ID: row.ID }).then(res => {
            loading.close()
            if (res.code === 20000) {
              _this.$message({
                message: 'Remove Group Success!',
                type: 'success'
              })
              _this.getList()
            }
          })
        })
        .catch(() => {
          this.$message({
            type: 'info',
            message: '已取消删除'
          })
        })
    },
    handleCreate() {
      this.dialogFormVisible = true
      this.operate = 'add'
      this.temp = {ENABLE:true}
    },
    exit() {
      this.dialogFormVisible = false
    }
  }
}
</script>
