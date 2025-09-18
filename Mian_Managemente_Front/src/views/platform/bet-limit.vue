<template>
  <div class="app-container">
    <el-table
      :key="tableKey"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%;"
      :show-header="false"
    >
      <el-table-column align="center" width="220px">
        <template slot-scope="{row}">
          <span v-if="row.NAME !==''">{{ row.NAME }}</span>
        </template>
      </el-table-column>
      <el-table-column align="center">
        <template slot-scope="{row}">
          <el-form v-if="row.NAME !==''" :model="row">
            <el-input v-if="row.CODE!==null" v-show="true" v-model="row.CODE" placeholder="please input content" />
          </el-form>
        </template>
      </el-table-column>
      <el-table-column align="center" prop="TITLE" width="220px" />
      <el-table-column align="center">
        <template slot-scope="{row}">
          <el-form :model="row">
            <el-input v-show="true" v-model="row.CONTENT" placeholder="please input content" />
          </el-form>
        </template>
      </el-table-column>
      <el-table-column align="center" width="200px" class-name="small-padding fixed-width">
        <template slot-scope="{row}">
          <el-button type="primary" size="medium" round @click="handleUpdate(row)">SAVE</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import waves from '@/directive/waves' // waves directive
import { getBetLimit, editSettings } from '@/api/order'

export default {
  name: 'BetLimit',
  directives: { waves },
  data() {
    return {
      tableKey: 0,
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
      getBetLimit().then(response => {
        this.list = response.items
        this.listLoading = false
      })
    },
    handleUpdate: function(row) {
      const _this = this
      if (row.CONTENT === '') {
        _this.$message({
          message: '输入比例不能为空',
          type: 'fail'
        })
        return
      }
      const para = {
        MDICT_ID: row.MDICT_ID,
        CONTENT: row.CONTENT,
        CODE: row.CODE
      }
      editSettings(para).then(response => {
        this.$message({
          message: response.message,
          type: 'success'
        })
        this.getList()
      })
    }
  }
}
</script>
