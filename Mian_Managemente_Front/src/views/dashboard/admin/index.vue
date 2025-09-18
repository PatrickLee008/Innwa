<template>
  <div class="dashboard-editor-container">
    <el-row :gutter="8">
      <h2 class="list_title " style="margin:18px 0 ">Google Verification</h2>
      <div v-if="userInfo.GOOGLE_SECRET">

        <img :src="myGoogleCode" style="width: 100px;height: 100px;">
        <p>Your Secret ：  {{userInfo.GOOGLE_SECRET}}</p>
        <a href="https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2" target="_blank"  style="color:blue;text-decoration: underline">click here to download google authenticator</a>
        <p>Please use your Google Authenticator to scan this qrcode,or input the scret on the above line</p>
      </div>
      <div v-else>
        <el-button  style="margin:12px 0" @click="getGoogleCode">Click Here to Set Google Enable</el-button>
      </div>

    </el-row>
    <github-corner class="github-corner" />



    <panel-group @handleSetLineChartData="handleSetLineChartData" />

    <el-row :gutter="32">
      <el-col :xs="12" :sm="12" :lg="12">
        <div class="chart-wrapper">
          <bar-chart />
        </div>
      </el-col>
      <el-col :xs="12" :sm="12" :lg="12">
        <div class="chart-wrapper">
          <agent-chart />
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="8">
      <el-col
        :xs="{span: 24}"
        :sm="{span: 24}"
        :md="{span: 24}"
        :lg="{span: 12}"
        :xl="{span: 12}"
        style="padding-right:8px;margin-bottom:30px;"
      >
        <p class="list_title">New charges</p>
        <charge-table />
      </el-col>
      <el-col
        :xs="{span: 24}"
        :sm="{span: 24}"
        :md="{span: 24}"
        :lg="{span: 12}"
        :xl="{span: 12}"
        style="padding-right:8px;margin-bottom:30px;"
      >
        <p class="list_title">New Cash</p>
        <withdraw-table />
      </el-col>
    </el-row>

    <el-row :gutter="8">
      <p class="list_title">New Orders</p>
      <el-col
        :xs="{span: 24}"
        :sm="{span: 24}"
        :md="{span: 24}"
        :lg="{span: 24}"
        :xl="{span: 24}"
        style="padding-right:8px;margin-bottom:30px;"
      >
        <transaction-table />
      </el-col>
    </el-row>


  </div>
</template>

<script>
import GithubCorner from "@/components/GithubCorner";
import PanelGroup from "./components/PanelGroup";
import LineChart from "./components/LineChart";
import RaddarChart from "./components/RaddarChart";
import PieChart from "./components/PieChart";
import BarChart from "./components/BarChart";
import TransactionTable from "./components/TransactionTable";
import TodoList from "./components/TodoList";
import BoxCard from "./components/BoxCard";
import WithdrawTable from "./components/WithdrawTable";
import ChargeTable from "./components/ChargeTable";
import AgentChart from "./components/AgentChart";
import {setup_2fa,getInfo} from "@/api/user"

const lineChartData = {
  newVisitis: {
    expectedData: [100, 120, 161, 134, 105, 160, 165],
    actualData: [120, 82, 91, 154, 162, 140, 145]
  },
  messages: {
    expectedData: [200, 192, 120, 144, 160, 130, 140],
    actualData: [180, 160, 151, 106, 145, 150, 130]
  },
  purchases: {
    expectedData: [80, 100, 121, 104, 105, 90, 100],
    actualData: [120, 90, 100, 138, 142, 130, 130]
  },
  shoppings: {
    expectedData: [130, 140, 141, 142, 145, 150, 160],
    actualData: [120, 82, 91, 154, 162, 140, 130]
  }
};

export default {
  name: "DashboardAdmin",
  components: {
    GithubCorner,
    PanelGroup,
    LineChart,
    RaddarChart,
    PieChart,
    BarChart,
    TransactionTable,
    TodoList,
    BoxCard,
    WithdrawTable,
    ChargeTable,
    AgentChart
  },
  data() {
    return {
      myGoogleCode:'',
      userInfo:{},
      lineChartData: lineChartData.newVisitis
    };
  },
  methods: {
    getGoogleCode(){
      let _this =this;
      setup_2fa().then(res=>{
        if(res.code == 20000){
          _this.userInfo = res.item;
          _this.myGoogleCode = res.data.qr_url
        }
      })
    },
    handleSetLineChartData(type) {
      this.lineChartData = lineChartData[type];
    },
    getUserInfo(){
      let _this =this;
      getInfo().then(res=>{
        if(res.code == 20000){
          _this.userInfo = res.data.info;
          _this.myGoogleCode = process.env.VUE_APP_BASE_API +'static/google_code/'+this.userInfo.ACCOUNT+'_qrcode.png'
        }
      })
    }
  },
  mounted() {
    this.getUserInfo()
    // this.getGoogleCode()
  }
};
</script>

<style lang="scss" scoped>
.list_title {
  margin-left: 8px;
  color: #606266;
  font-size: 16px;
  height: 8px;
}
.dashboard-editor-container {
  padding: 32px;
  background-color: rgb(240, 242, 245);
  position: relative;

  .github-corner {
    position: absolute;
    top: 0px;
    border: 0;
    right: 0;
  }

  .chart-wrapper {
    background: #fff;
    padding: 16px 16px 0;
    margin-bottom: 32px;
  }
}

@media (max-width: 1024px) {
  .chart-wrapper {
    padding: 8px;
  }
}
</style>
