<template>
  <div class="app-container">
    <h1>Innwabet App Ad Image</h1>
    <el-upload
      :action="baseUrl+'up_image/add'"
      list-type="picture-card"
      :headers="headers"
      :on-preview="handlePictureCardPreview"
      :file-list="list"
      :on-remove="3"
    >
      <i class="el-icon-plus"></i>
    </el-upload>
  </div>
</template>

<script>
import { getImageList } from "@/api/images";
import { getToken } from "@/utils/auth";

export default {
  data() {
    return {
      headers: {
        Authorization: getToken(),
      },
      baseUrl: process.env.VUE_APP_BASE_API,
      startTime: "",
      endTime: "",
      total: 0,
      list: [],
      tableKey: 0,
      listLoading: false,
      listQuery: {
        page: 1,
        limit: 99,
      },
      fileName: "",
      fileImageUrl: "",
      fileVisible: "",
    };
  },
  created() {
    this.getList();
  },
  methods: {
    handlePictureCardPreview(file) {
      this.fileName = file.name;
      this.fileImageUrl = file.url;
      this.fileVisible = true;
    },
    handleFileRemove(file, fileList) {
      var _this = this;
      removeFileApi({ ID: file.ID }).then((res) => {
        if (res.code === 20000) {
          _this.$message({
            message: "删除成功！",
            type: "success",
          });
        }
      });
    },
    handleEdit(row) {},
    getList() {
      this.listLoading = true;

      //切割地址
      var ip = process.env.VUE_APP_BASE_API.substring(
        0,
        process.env.VUE_APP_BASE_API.length - 5
      );
      this.list = [];
      getImageList(this.listQuery).then((response) => {
        response.items.forEach((item) => {
          var obj = {
            ID: item.ID,
            name: item.ADDRESS,
            url: ip + "9190/static/img/upload/" + item.ADDRESS,
          };
          this.list.push(obj);
        });
        this.listLoading = false;
      });
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
  },
};
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
