<template>
  <div class="app-container">
    <div class="filter-container">
      <el-row>
        <el-input
          v-model="listQuery.key_word"
          placeholder="key word"
          style="width: 200px"
          class="filter-item"
        />
        <el-button
          icon="el-icon-search"
          class="filter-item"
          type="primary"
          @click="getImage"
          >Search
        </el-button>
        <!--        <el-button-->
        <!--          class="filter-item"-->
        <!--          type="primary"-->
        <!--          icon="el-icon-plus"-->
        <!--          @click="addImageForm"-->
        <!--        >Add-->
        <!--        </el-button>-->
      </el-row>
    </div>

    <el-table
      v-loading="listLoading"
      :data="list"
      fit
      border
      highlight-current-row
      style="width: 100%"
    >
      <el-table-column type="index" width="50" />
      <el-table-column
        v-for="(ctl, index) in table_ctl"
        :formatter="ctl.formatter"
        :sortable="ctl.sortable"
        :key="index"
        :label="ctl.label"
        :prop="ctl.prop"
        v-if="ctl.visiable"
        align="center"
      ></el-table-column>

      <el-table-column
        label="Operation"
        align="center"
        class-name="small-padding fixed-width"
        width="200px"
      >
        <template slot="header" slot-scope="scope">
          <span style="margin-right: 15px">Operation</span>
        </template>
        <template slot-scope="scope">
          <el-tooltip
            class="item"
            effect="dark"
            :hide-after="500"
            content="edit"
            placement="top"
          >
            <el-button
              icon="el-icon-edit"
              circle
              size="medium"
              @click="updateImage(scope.row)"
              type="primary"
            ></el-button>
          </el-tooltip>
          <!--          <el-tooltip class="item" effect="dark" :hide-after="500" content="delete" placement="top">-->
          <!--            <el-button icon="el-icon-delete" circle size="medium" type="danger"-->
          <!--                       @click="showDeleteForm(scope.row)"></el-button>-->
          <!--          </el-tooltip>-->
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      :title="textMap[dialogStatus]"
      :visible.sync="dialogFormVisible"
      style="width: 100%"
      @close="dialogClose"
      custom-class="dialogwidth"
    >
      <el-form
        ref="dataForm"
        :model="form"
        label-position="left"
        label-width="150px"
      >
        <div class="lb">
          <el-form-item label="NAME：">
            <el-input readonly v-model="form.NAME"></el-input>
          </el-form-item>
          <!--          <el-form-item>-->

          <!--            <el-upload-->
          <!--              class="upload-demo"-->
          <!--              action="https://jsonplaceholder.typicode.com/posts/"-->
          <!--              :limit="1">-->
          <!--              <el-button size="small" type="primary">Upload</el-button>-->
          <!--            </el-upload>-->
          <!--          </el-form-item>-->
          <el-form-item label="PIC:">
            <el-upload
              action="#"
              :on-preview="handlePictureCardPreview"
              :file-list="ImageFileList"
              ref="upload"
              :http-request="uploadImage"
              :on-change="fileChange"
              :limit="1"
              list-type="picture-card"
              accept=".jpg,.jpeg,.png,.gif,.bmp,.pdf,.JPG,.JPEG,.PBG,.GIF,.BMP,.PDF"
              :before-upload="beforePicUpload"
            >
              <div slot="tip" class="el-upload__tip">
                only jpg/png file and no exceed 500kb
              </div>
            </el-upload>
          </el-form-item>
          <!--          <el-form-item label="启用：">-->
          <!--            <el-switch v-model="form.valid"></el-switch>-->
          <!--          </el-form-item>-->
        </div>
      </el-form>

      <div slot="footer" class="dialog-footer">
        <!--        <el-button @click="dialogFormVisible = false">取消</el-button>-->
        <el-button @click="dialogFormVisible = false">Close</el-button>
        <!--        <el-button type="primary" @click="dialogStatus==='create'?addImage():editAppUser()">确定</el-button>-->
      </div>
    </el-dialog>
    <el-dialog
      title="表格列编辑"
      :visible.sync="table_dialog_form_visiable"
      style="width: 100%"
      custom-class="dialogwidth"
    >
      <el-form ref="dataForm" label-position="left" label-width="200px">
        <div class="lb">
          <el-form-item
            :label="ctl.label + '：'"
            v-for="(ctl, index) in table_ctl"
            :key="index"
          >
            <el-switch
              v-model="ctl.visiable"
              active-text="可见"
              inactive-text="不可见"
              active-color="#13ce66"
              inactive-color="#666666"
            ></el-switch>
          </el-form-item>
        </div>
      </el-form>

      <div slot="footer" class="dialog-footer">
        <el-button @click="table_dialog_form_visiable = false">确定</el-button>
      </div>
    </el-dialog>
    <pagination
      v-show="total > 0"
      :total="total"
      :page.sync="listQuery.page"
      :page-sizes="[20, 50, 99]"
      :page-size="99"
      :limit.sync="listQuery.limit"
      @pagination="getImage"
    />
  </div>
</template>

<script>
import Pagination from "@/components/Pagination/index"; // secondary package based on el-pagination
import Vue from "vue";
import { getToken } from "@/utils/auth";
import { addImage, editImage, removeImage, getImageList } from "@/api/images";

export default {
  components: { Pagination },
  data() {
    return {
      list: [],
      total: 0,
      rechargeForm: {},
      user_monthly: {},

      ImageFileList: [],
      table_dialog_form_visiable: false,
      table_ctl: [
        {
          label: "ID",
          prop: "ID",
          sortable: false,
          visiable: true,
          formatter: null,
        },
        {
          label: "NAME",
          prop: "NAME",
          sortable: false,
          visiable: true,
          formatter: null,
        },
        {
          label: "ADDRESS",
          prop: "ADDRESS",
          sortable: false,
          visiable: true,
          formatter: null,
        },
        {
          label: "CREATE_TIME",
          prop: "CREATE_TIME",
          sortable: false,
          visiable: true,
          formatter: null,
        },
      ],
      total_price: 0,
      package_type_list: [
        { value: 1, label: "1个月" },
        { value: 3, label: "3个月" },
        { value: 6, label: "6个月" },
        { value: 12, label: "12个月" },
      ],
      rechargeFormVisible: false,
      role_list: ["商家", "管理员"],
      listLoading: false,
      form: {},
      baseUrl: process.env.VUE_APP_BASE_API,
      headers: {
        Authorization: getToken(),
      },
      fileVisible: false,
      fileImageUrl: "",
      fileName: "",
      dialogFormVisible: false,
      textMap: {
        edit: "Edit",
        create: "Add",
      },
      dialogStatus: "",
      listQuery: {
        page: 1,
        limit: 99,
        start_time: null,
        end_time: null,
      },
    };
  },
  created() {
    this.getImage();
  },
  mounted() {},
  methods: {
    getImage() {
      let _this = this;
      _this.listLoading = true;
      getImageList(_this.listQuery).then((response) => {
        _this.list = response.items;
        _this.listLoading = false;
      });
    },
    addImage() {
      let _this = this;
      let para = Object.assign({}, _this.form);
      // para.roles = [para.roles]
      addImage(para).then((res) => {
        if (res.code === 20000) {
          _this.$message({
            type: "success",
            message: res.message,
          });
          _this.dialogFormVisible = false;
          _this.getImage();
        }
      });
    },
    addImageForm() {
      this.resetForm();
      this.dialogStatus = "create";
      this.dialogFormVisible = true;
    },
    updateImage(row) {
      this.resetForm();
      this.form = row;
      this.dialogStatus = "edit";
      this.ImageFileList = [
        {
          ID: row.ID,
          NAME: row.NAME,
          url: "http://img.innwabet.com/" + row.ADDRESS,
        },
      ];
      this.dialogFormVisible = true;
    },
    uploadImage(params) {
      let _this = this
      const formData = new FormData();
      const file = params.file;
      formData.append("NAME", this.form.NAME);
      formData.append("ID", this.form.ID);
      formData.append("file", file);

      const loading = this.$loading({
        lock: true,
        text: "upload",
        spinner: "el-icon-loading",
        background: "rgba(0, 0, 0, 0.7)",
      });

      editImage(formData)
        .then((res) => {
          loading.close();
          if (res.data.code == 20000) {
            _this.$message({
              type: "success",
              message: "upload success",
            });
            params.onSuccess(); // 上传成功的图片会显示绿色的对勾
            // 但是我们上传成功了图片， fileList 里面的值却没有改变，还好有on-change指令可以使用
          } else {
            _this.$message({
              type: "error",
              message: "upload error",
            });
            params.onError(); // 上传成功的图片会显示绿色的对勾
            // 但是我们上传成功了图片， fileList 里面的值却没有改变，还好有on-change指令可以使用
          }
        })
        .catch((res) => {
          console.log("图片上传失败");
        });
    },
    fileChange(file) {
      this.$refs.upload.clearFiles(); //清除文件对象
      this.logo = file.raw; // 取出上传文件的对象，在其它地方也可以使用
      this.ImageFileList = [{ name: file.name, url: file.url }]; // 重新手动赋值filstList， 免得自定义上传成功了, 而fileList并没有动态改变， 这样每次都是上传一个对象
      this.form.NAME = file.name;
    },
    resetForm() {
      this.form = {};
      this.rechargeForm = { valid_months: 1, valid: true };
    },
    editAppUser() {
      let _this = this;
      let para = Object.assign({}, _this.form);
      // para.roles = [para.roles]
      delete para.update_time;
      editImage(para).then((res) => {
        if (res.code === 20000) {
          _this.$message({
            type: "success",
            message: res.message,
          });
          _this.dialogFormVisible = false;
          _this.getImage();
        }
      });
    },

    fileUploadSuccess(response, file, fileList) {
      if (response.code === 20000) {
        // file.ID = response.file.ID;
        // file.FileType = response.file.FileType;
        // console.log(response)
        this.dialogFormVisible = false;
        this.getImage();
        this.$message({
          type: "success",
          duration: 2500,
          message: "Edit success",
        });
      } else {
        this.$message({
          type: "error",
          duration: 1500,
          message: response.message,
        });
      }
    },

    dialogClose() {
      this.ImageFileList = [];
    },
    beforePicUpload(file) {
      const isPG =
        file.type === "image/png" ||
        file.type === "image/jpeg" ||
        file.type === "image/jpg" ||
        file.type === "image/bmp";
      if (!isPG) {
        this.$message.error(
          "Only can upload .png / .jpeg / .jpg / .bmp image!"
        );
      }
      let name_not_exist =
        this.form.NAME === "" ||
        this.form.NAME === null ||
        this.form.NAME === undefined;
      if (name_not_exist) {
        this.$message.error("Please input name!");
      }
      return isPG && !name_not_exist;
    },
    removeImage(row) {
      let _this = this;
      removeImage(row.id).then((res) => {
        if (res.code === 20000) {
          _this.$message({
            type: "success",
            message: "删除成功!",
          });
          _this.getImage();
        }
      });
    },
    tableFormat(row, column, index) {
      // console.log(row, column, index)
      let str = "";
      switch (column.property) {
        case "update_time":
          str = row.update_time ? row.update_time.slice(0, 10) : "";
          break;
        case "create_time":
          str = row.create_time.slice(0, 10);
          break;
      }
      return str;
    },
    handlePictureCardPreview(file) {
      this.fileName = file.name;
      this.fileImageUrl = file.url;
      this.fileVisible = true;
    },
    showDeleteForm(row) {
      this.$confirm("Delete image ID:「" + row.ID + "」?", "Hint", {
        confirmButtonText: "Confirm",
        cancelButtonText: "Cancel",
        type: "warning",
      })
        .then(() => {
          this.removeImage(row);
        })
        .catch(() => {
          this.$message({
            type: "info",
            message: "Canceled",
            duration: 500,
          });
        });
    },
  },
};
</script>
