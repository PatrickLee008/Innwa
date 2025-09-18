<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input v-model="listQuery.key_word" placeholder="Key word" style="width: 200px;" class="filter-item" @keyup.enter.native="handleFilter" />
      <el-date-picker v-model="startTime" type="date" value-format="yyyy-MM-dd" placeholder="Start" />
      <el-date-picker v-model="endTime" type="date" value-format="yyyy-MM-dd" placeholder="End" />
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        Search
      </el-button>
      <el-button v-waves class="filter-item item-margin" type="primary" @click="handleCreate">
        Add
      </el-button>
    </div>

    <el-table
      :key="tableKey"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%;"
    >
      <el-table-column label="Title" align="center" prop="TITLE" />
      <el-table-column label="Content" align="center" width="800px" prop="CONTENT" />
      <el-table-column label="Status" align="center">
        <template slot-scope="{row}">
          <span v-if="row.STATUS==1">effective</span>
          <span v-else>valid</span>
        </template>
      </el-table-column>
      <el-table-column label="Creator" align="center" prop="CREATOR" />
      <el-table-column label="Create Time" align="center" prop="CREATOR_TIME" />
      <el-table-column label="Operation" align="center" width="200px" class-name="small-padding fixed-width">
        <template slot-scope="{row}">
          <el-button type="primary" icon="el-icon-edit" circle @click="handleUpdate(row)" />
          <el-button type="danger" icon="el-icon-delete" circle @click="handleDelete(row)" />
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />

    <el-dialog
      :title="textMap[dialogStatus]"
      :visible.sync="dialogFormVisible"
      custom-class="dialogwidth"
    >
      <el-form
        ref="dataForm"
        :model="temp"
        label-position="left"
        label-width="100px"
      >
        <div class="lb">
          <el-form-item label="Status">
            <el-select v-model="temp.STATUS">
              <el-option
                v-for="item in STATUS_OPTION"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="Title">
            <el-input v-model="temp.TITLE" />
          </el-form-item>

          <el-form-item label="Content" style="width:100%">
            <el-input v-show="true" v-model="temp.CONTENT" :autosize="{ minRows: 2, maxRows: 4}" type="textarea" placeholder="Content" />
          </el-form-item>

        </div>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">Cancel</el-button>
        <el-button type="primary" @click="dialogStatus==='create'?createData():updateData()">Confirm</el-button>
      </div>
    </el-dialog>

    <el-dialog :visible.sync="dialogPvVisible" title="">
      <h2 style="text-align:center">Are you sure you want to delete this announcement?</h2>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogPvVisible = false">Cancel</el-button>
        <el-button type="primary" @click="deleteUser()">Confirm</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import waves from '@/directive/waves' // waves directive
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import { getNotice, addNotice, editNotice, delNotice } from '@/api/order'
import { dateToString } from '@/utils/date-format'

export default {
  name: 'Announcement',
  directives: { waves },
  components: { Pagination },
  filters: {
    statusFilter(status) {
      const statusMap = {
        published: 'success',
        draft: 'info',
        deleted: 'danger'
      }
      return statusMap[status]
    }
  },
  data() {
    return {
      tableKey: 0,
      startTime: '',
      endTime: '',
      textMap: {
        update: 'Edit',
        create: 'Create'
      },
      dialogPvVisible: false,
      dialogFormVisible: false,
      dialogStatus: '',
      temp: {
        TITLE: '',
        CONTENT: '',
        STATUS: ''
      },
      STATUS_OPTION: [
        {
          value: '1',
          label: 'Effective'
        },
        {
          value: '0',
          label: 'Valid'
        }
      ],
      list: [],
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 99,
        matchId: undefined
      },
      closeStatus: [],
      showReviewer: false
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList: function() {
      this.listLoading = true
      getNotice(this.listQuery).then(response => {
        this.list = response.items
        // this.total = response.total_amount
        this.list.forEach(element => {
          element.CREATOR_TIME = dateToString(element.CREATOR_TIME)
        })
        setTimeout(() => {
          this.listLoading = false
        }, 1.5 * 1000)
      })
    },
    handleFilter: function() {
      if (this.startTime !== '') {
        this.listQuery.start_time = this.startTime
      }
      if (this.endTime !== '') {
        this.listQuery.end_time = this.endTime
      }
      this.listQuery.page = 1
      this.getList()
    },
    resetTemp: function() {
      this.temp = {
        TITLE: '',
        CONTENT: '',
        STATUS: '1'
      }
    },
    handleCreate() {
      this.resetTemp()
      this.dialogStatus = 'create'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    createData() {
      const _this = this
      // this.$refs['dataForm'].validate(valid => {
      //   if (valid) {

      //   } else {
      //     return
      //   }
      // })

      this.dialogFormVisible = false
      addNotice(this.temp).then(response => {
        _this.$message({
          message: response.message,
          type: 'success'
        })
        _this.getList()
      })
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row) // copy obj
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
      this.temp.MNOTICE_ID = row.MNOTICE_ID
    },
    updateData() {
      // if (valid) {
      // } else {
      //   return
      // }
      const para = {
        MNOTICE_ID: this.temp.MNOTICE_ID,
        TITLE: this.temp.TITLE,
        CONTENT: this.temp.CONTENT
      }
      this.dialogFormVisible = false
      editNotice(para).then(response => {
        this.$message({
          message: response.message,
          type: 'success'
        })
        this.getList()
      })
    },
    handleDelete(row) {
      this.dialogPvVisible = true
      this.deleteid = row
    },
    deleteUser() {
      delNotice({ MNOTICE_ID: this.deleteid.MNOTICE_ID }).then(response => {
        setTimeout(() => {
          this.listLoading = false
        }, 1.5 * 1000)
        this.$notify({
          title: 'Success',
          message: 'Delete Successfully',
          type: 'success',
          duration: 2000
        })
        const index = this.list.indexOf(this.deleteid)
        this.list.splice(index, 1)
        this.dialogPvVisible = false
      })
    }
  }
}
</script>
<style>
</style>
