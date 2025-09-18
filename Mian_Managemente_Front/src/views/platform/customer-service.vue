<template>
  <div class="app-container">
    <div class="filter-container">
      <em>关键字:</em>
      <el-input
        v-model="listQuery.key_word"
        placeholder="Key Word"
        style="width: 200px;"
        class="filter-item"
      />
      <el-button
        v-waves
        class="filter-item"
        type="primary"
        icon="el-icon-search"
        @click="handleFilter">Search
      </el-button>

      <el-button v-waves class="filter-item item-margin" type="primary" @click="handleCreate">
        Add
      </el-button>
    </div>

    <el-table
      :key="tableKey"
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%;"
    >
      <el-table-column type="index" width="50"/>
      <el-table-column label="Question" prop="question" width="" align="center"/>
      <el-table-column label="Answer" prop="answer" width="" align="center"/>
      <el-table-column label="Status" width="" align="center">
        <template slot-scope="{row}">
          <label>{{ row.enable?'Enable':'Disable' }}</label>
        </template>
      </el-table-column>
      <el-table-column label="Constant" width="" align="center">
        <template slot-scope="{row}">
          <label>{{ row.enable?'On':'Off' }}</label>
        </template>
      </el-table-column>
      <el-table-column
        label="Operator"
        align="center"
        class-name="small-padding fixed-width"
        width="200px">
        <template slot-scope="{row}">
          <el-button type="primary" circle icon="el-icon-edit" @click="handleUpdate(row)"/>
          <el-button type="danger" circle icon="el-icon-delete" @click="handleDelete(row,'deleted')"/>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      :title="textMap[dialogStatus]"
      :visible.sync="dialogFormVisible"
      style="width: 100%"
      :close-on-click-modal="false"
      custom-class="dialogwidth">
      <el-form
        ref="dataForm"
        :model="form"
        label-position="left"
        label-width="150px"
      >
        <div class="lb">
          <el-form-item label="Question：">
            <el-input v-model="form.question"></el-input>
          </el-form-item>
          <el-form-item label="Status：">
            <el-switch v-model="form.enable" active-text="Enable" inactive-text="Disable" active-color="#13ce66" inactive-color="#666666"></el-switch>
          </el-form-item>
          <el-form-item label="Constant Question：">
            <el-switch v-model="form.is_constant" active-text="On" inactive-text="Off" active-color="#13ce66" inactive-color="#666666"></el-switch>
          </el-form-item>
          <mavon-editor
            v-model="form.answer"
            :toolbars="toolbars"
            @imgAdd="handleImgAdd"
            ref="md"
            @imgDel="handleImgDel"
            style="min-height: 600px;width: 100%;margin: 0 50px"
            language="en"
          />
        </div>
      </el-form>

      <div slot="footer" class="dialog-footer">
        <!--        <el-button @click="dialogFormVisible = false">取消</el-button>-->
        <el-button @click="dialogFormVisible = false">Close</el-button>
        <el-button type="primary" @click="dialogStatus==='create'?addQuestion():editQuestion()">Confirm</el-button>
      </div>
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
  import waves from '@/directive/waves' // waves directive
  import Pagination from '@/components/Pagination' // secondary package based on el-pagination
  import {number_format} from "@/utils";
  import {addImage, removeImage} from "@/api/images";
  import axios from 'axios'

  export default {
    name: 'OrderList',
    components: {Pagination},
    directives: {waves},
    data() {
      return {
        startTime: '',
        endTime: '',
        total: 0,
        list: [],
        textMap: {
          edit: "Edit",
          create: "Add",
        },
        dialogStatus: "",
        tableKey: 0,
        toolbars: {
          bold: true,
          italic: true,
          header: true,
          underline: true,
          strikethrough: true,
          mark: true,
          superscript: true,
          subscript: true,
          quote: true,
          ol: true,
          ul: true,
          link: true,
          imagelink: true,
          code: true,
          table: true,
          fullscreen: true,
          readmodel: true,
          htmlcode: true,
          help: true,
          undo: true,
          redo: true,
          trash: true,
          save: true,
          navigation: true,
          subfield: true,
          preview: true
        },
        listLoading: false,
        dialogFormVisible: false,
        image_url_prefix:'http://192.168.99.9:9190/static/img/upload/',
        form: {
          answer: '',
          question: '',
          platform: 'innwa',
          is_constant: false,
          enable: true,
        },
        listQuery: {
          page: 1,
          limit: 99,
          type: null,
        }
      }
    },
    created() {
      this.getList()
    },
    methods: {
      getList() {
        let _this = this
        _this.listLoading = true
        let data = {
          platform: 'innwa',
        }
        axios.get('http://192.168.99.9:9100/qa', {
          params: data,
          headers: {'Content-Type': 'application/json'}
        }).then(resp => {
          let response = resp.data
          _this.list = response.items
          _this.total = response.total
          _this.listLoading = false
          _this.list.forEach(element => {
          })
        }).catch(error => {
          // console.error('图片上传失败:', error);
        });
      },
      addQuestion() {
        let _this = this
        _this.listLoading = true
        let data = _this.$toolbox.deep_clone(_this.form)
        axios.post('http://192.168.99.9:9100/qa', data, {headers: {'Content-Type': 'application/json'}}).then(resp => {
          _this.dialogFormVisible = false
          _this.getList()
        }).catch(error => {
          // console.error('图片上传失败:', error);
        });
      },
      editQuestion() {
        let _this = this
        _this.listLoading = true
        let data = _this.$toolbox.deep_clone(_this.form)
        axios.put(`http://192.168.99.9:9100/qa/${data.ID}`, data, {headers: {'Content-Type': 'application/json'}}).then(resp => {
          _this.dialogFormVisible = false
          _this.getList()
        }).catch(error => {
          // console.error('图片上传失败:', error);
        });
      },
      handleFilter() {
        if (this.startTime !== '') {
          this.listQuery.start_time = this.startTime
        }
        if (this.endTime !== '') {
          this.listQuery.end_time = this.endTime
        }
        this.listQuery.page = 1
        this.getList()
      },
      resetTemp() {
        this.form = this.$options.data().form
      },
      handleCreate() {
        this.resetTemp()
        this.dialogStatus = 'create'
        this.dialogFormVisible = true
        this.$nextTick(() => {
          this.$refs['dataForm'].clearValidate()
        })
      },
      handleUpdate(row) {
        this.form = Object.assign({}, row) // copy obj
        this.dialogStatus = 'update'
        this.dialogFormVisible = true
        this.$nextTick(() => {
          this.$refs['dataForm'].clearValidate()
        })
      },
      tableFormat(row, column, index) {
        // console.log(row, column, index)
        let str = ''
        switch (column.property) {
          case 'change_amount':
            str = number_format(row.BALANCE - row.AMOUNT)
            break
          default:
            str = number_format(row[column.property])
            break
        }
        return str
      },
      handleImgAdd(pos, file) {
        let _this = this
        const formData = new FormData();
        formData.append("NAME", "INNWA_AI");
        // formData.append("ID", this.form.ID);
        formData.append("file", file);
        formData.append("IMAGE_TYPE", "AI");

        addImage(formData)
          .then((res) => {
            if (res.code == 20000) {
              _this.$message({
                type: "success",
                message: "upload success",
              });
              let url = _this.image_url_prefix + res.name
              _this.$refs.md.$img2Url(pos, url);
            } else {
              _this.$message({
                type: "error",
                message: "upload error",
              });
            }
          })
          .catch((res) => {
            console.log("upload fail");
          });
      },

      // 图片删除事件（可选）
      handleImgDel(pos) {
        // 可以根据需要实现图片删除的后端逻辑
        // console.log('删除图片:', pos);
        let address = pos[0]
        if(typeof address==='string' && address){
          address = address.replace(this.image_url_prefix,'')
        }
        let _this = this;
        removeImage({
          ADDRESS:address
        }).then((res) => {
          if (res.code === 20000) {
            _this.$message({
              type: "success",
              message: "删除成功!",
            });
            _this.getImage();
          }
        });
      },
    }
  }
</script>
<style>
  .dialogwidth {
    width: 80%;
  }

  .lb {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    justify-content: space-between;
  }

  .lb .el-form-item {
    display: inline-block;
    width: 500px;
    margin-left: 50px;
    margin-right: 50px;
  }

  .lb .el-input--medium .el-input__inner {
    max-width: 400px;
    display: inline-block;
  }

  .sublist {
    display: flex;
    align-items: center;
  }
</style>
