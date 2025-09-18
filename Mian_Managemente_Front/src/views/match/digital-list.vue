<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.key_word"
        placeholder="key word"
        style="width: 200px"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />

      <el-date-picker
        v-model="listQuery.startTime"
        type="date"
        placeholder="Start"
      />
      <el-date-picker
        v-model="listQuery.endTime"
        type="date"
        placeholder="End"
      />


      <el-radio v-model="radio" label="1" border @change="radioChange"
      >Settled
      </el-radio
      >
      <el-radio v-model="radio" label="0" border @change="radioChange"
      >Unsettlement
      </el-radio
      >
      <el-radio v-model="radio" label="2" border @change="radioChange"
      >All
      </el-radio
      >

      <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">Search
      </el-button>

      <el-button v-waves class="filter-item" type="primary" icon="el-icon-notebook-2" @click="reportVisible = true">report
      </el-button>

      <el-button v-waves class="filter-item" type="primary" icon="el-icon-notebook-1" @click="orderVisible = true">order
      </el-button>

      <el-button v-waves class="filter-item" type="primary" icon="el-icon-plus" @click="handleCreate">New Stage
      </el-button>
      <el-row class="text-center">
        <el-col :span="3">
          <span style="margin-right: 15px"
          >Total Bet Count: {{ total_bet_count }}</span
          >
        </el-col>
        <el-col :span="3">
          <span>Total Bet Amount: {{ total_bet_sum }}</span>
        </el-col>
        <el-col :span="3">
          <span>Total Company Benefit: {{ total_benefit }}</span>
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
      style="width: 100%"
    >
      <el-table-column type="index" width="50"/>
      <el-table-column label="ID" prop="ID" align="center" width="100px"/>
      <el-table-column label="STAGE" prop="STAGE" max-width="8%" align="center"/>
      <el-table-column label="ODDS" prop="ODDS" max-width="8%" align="center"/>
      <el-table-column label="MYAN_OPEN_TIME" :formatter="tableFormatter" prop="OPEN_TIME" width="100px" align="center"/>
      <el-table-column label="MYAN_CLOSE_TIME" :formatter="tableFormatter" prop="CLOSE_TIME" width="100px" align="center"/>
      <el-table-column label="BET_NUM" prop="BET_NUM" max-width="8%" align="center"/>
      <el-table-column label="BET_SUM" prop="BET_SUM" max-width="8%" align="center"/>
      <el-table-column label="BENEFIT" prop="BENEFIT" max-width="8%" align="center"/>
      <el-table-column label="RESULT" prop="RESULT" max-width="8%" align="center"/>
      <el-table-column label="LIMIT_CODE" prop="LIMIT_CODE" max-width="8%" align="center"/>
      <el-table-column label="LIMIT_NUM" prop="LIMIT_NUM" max-width="8%" align="center"/>
      <el-table-column label="EX_LIMIT" prop="EX_LIMIT" max-width="8%" align="center"/>
      <el-table-column label="SINGLE_MIN" prop="SINGLE_MIN" max-width="8%" align="center"/>
      <el-table-column label="SINGLE_MAX" prop="SINGLE_MAX" max-width="8%" align="center"/>
      <el-table-column label="USER_MAX" prop="USER_MAX" max-width="8%" align="center"/>
      <el-table-column label="NUM_USER_LIMIT" prop="NUM_USER_LIMIT" max-width="8%" align="center"/>
      <el-table-column label="REMARK" prop="REMARK" max-width="8%" align="center"/>
      <el-table-column label="CREATE_TIME" prop="CREATE_TIME" max-width="8%" align="center"/>
      <el-table-column label="UPDATE_TIME" prop="UPDATE_TIME" max-width="8%" align="center"/>
      <el-table-column label="CREATOR" prop="CREATOR" max-width="8%" align="center"/>
      <el-table-column label="UPDATER" prop="UPDATER" max-width="8%" align="center"/>
      <el-table-column label="STATUS" max-width="4%" align="center">
        <template slot-scope="{ row }">
          <span>{{ StatusLabel[row.STATUS] }}</span>
        </template>
      </el-table-column>
      <!--操作按钮-->
      <el-table-column
        label="operation"
        align="center"
        width="250px"
        class-name="small-padding fixed-width">
        <template slot-scope="scope">
          <div style="text-align: left">
            <el-button type="primary" @click="handleUpdate(scope.row)"
            >Edit
            </el-button>

            <el-button
              v-if="scope.row.STATUS == DigitStatus.Closed"
              type="primary"
              :loading="scope.row.settlementLoading"
              @click="showSettlement(scope.row)"
            >Settlement
            </el-button>
            <el-button
              v-if="scope.row.STATUS != DigitStatus.Settled"
              type="primary"
              :loading="scope.row.settlementLoading"
              @click="confirm_rc_dialog(scope.row)"
            >Cancel
            </el-button>
            <el-button
              v-if="scope.row.STATUS == DigitStatus.Settled"
              type="primary"
              :loading="scope.row.settlementLoading"
              @click="confirm_rc_dialog(scope.row,'reverse')"
            >Reverse
            </el-button>
            <el-button type="danger" @click="handleDelete(scope.row,'deleted')">Delete</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total > 0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      :page-sizes="[20, 50, 99]"
      :page-size="99"
      @pagination="getList"
    />

    <el-dialog
      title="Settlement"
      :visible.sync="settlementDialogs"
      style="text-align: center"
    >
      <el-row class="settlement-row">
        <el-col :span="12" class="settlement-col">
          <div class="grid-content bg-purple-light">ODDS</div>
        </el-col>
        <el-col :span="12" class="settlement-col">
          <div class="grid-content bg-purple-light">RESULT</div>
        </el-col>
      </el-row>
      <el-row class="settlement-row">
        <el-col :span="12" class="settlement-col">
          <div>{{ editFrom.ODDS }}</div>
        </el-col>
        <el-col :span="12" class="settlement-col">
          <div>{{ editFrom.RESULT }}</div>
        </el-col>
      </el-row>
      <el-row style="margin-top: 15px">
        <el-col :span="24">
          <el-button type="primary" @click="handleSettlement()"
          >Settlement
          </el-button
          >
          <el-button @click="settlementDialogs = false">Cancel</el-button>
        </el-col>
      </el-row>
    </el-dialog>

    <el-dialog
      title="Delete Stage"
      :visible.sync="deleteDialogVisible"
      style="text-align: center"
    >
      <el-row class="settlement-row">
        <el-col :span="12" class="settlement-col">
          <div class="grid-content bg-purple-light">ID</div>
        </el-col>
        <el-col :span="12" class="settlement-col">
          <div class="grid-content bg-purple-light">Stage</div>
        </el-col>
      </el-row>
      <el-row class="settlement-row">
        <el-col :span="12" class="settlement-col">
          <div>{{ selectedDigit.ID }}</div>
        </el-col>
        <el-col :span="12" class="settlement-col">
          <div>{{ selectedDigit.STAGE }}</div>
        </el-col>
      </el-row>
      <el-row style="margin-top: 15px">
        <el-col :span="24">
          <el-button type="primary" @click="deleteDigit(selectedDigit.ID)"
          >Delete
          </el-button
          >
          <el-button @click="deleteDialogVisible = false">Cancel</el-button>
        </el-col>
      </el-row>
    </el-dialog>

    <el-dialog
      @close="stop_refresh_data"
      :title="textMap[dialogStatus]"
      :visible.sync="dialogFormVisible"
      custom-class="dialogwidth"
      :close-on-click-modal="false"
    >
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="editFrom"
        label-position="left"
        label-width="120px"
      >
        <div class="lb">
          <el-form-item label="STAGE" prop="STAGE" span="11">
            <el-input v-model="editFrom.STAGE" style="width: 200px;"/>
            <el-radio-group  :disabled="editFrom.hasOwnProperty('CREATE_TIME')" v-model="editFrom.noon" @change="noonRadioChange">
              <el-radio :label="1">AM</el-radio>
              <el-radio :label="2">PM</el-radio>
            </el-radio-group>
          </el-form-item>
<!--          <el-form-item label="Noon">-->
<!--            -->
<!--          </el-form-item>-->
          <el-form-item label="RESULT" prop="RESULT">
            <el-input
              v-model="editFrom.RESULT"
              :disabled="editFrom.STATUS == DigitStatus.Settled"
              oninput="value=value.replace(/[^\d]/g,'').slice(0, 2)"
            />
          </el-form-item>
          <el-form-item label="ODDS" prop="ODDS" span="11">
            <el-input
              v-model="editFrom.ODDS"
              oninput="value = value.match(/^\d+(?:\.\d{0,2})?/)"
              maxlenth="2"
            />
          </el-form-item>

          <el-form-item label="STATUS">
            <el-select v-model="editFrom.STATUS">
              <el-option
                v-for="(index,item) in DigitStatus"
                :key="index"
                :label="item"
                :value="index"
                :disabled="index===3 || editFrom.STATUS === DigitStatus.Settled"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="Myan OPEN TIME">
            <div style="display: flex;flex-direction: column;">
              <el-date-picker
                v-model="editFrom.OPEN_MD_TIME"
                @change="set_server_time($event,1)"
                type="datetime"
                value-format="yyyy-MM-dd HH:mm:ss"
                placeholder="Please pick a date"
              />
              <span>Serv:{{editFrom.OPEN_TIME}}</span>
            </div>
          </el-form-item>
<!--          <el-form-item label="MYAN_OPEN_TIME">-->
<!--            <span>{{this.$to_myan_time(editFrom.OPEN_TIME)}}</span>-->
<!--          </el-form-item>-->


          <el-form-item label="Myan CLOSE TIME">
            <div style="display: flex;flex-direction: column;">
              <el-date-picker
                v-model="editFrom.CLOSE_MD_TIME"
                @change="set_server_time($event,2)"
                type="datetime"
                value-format="yyyy-MM-dd HH:mm:ss"
                placeholder="Please pick a date"
              />
              <span>Serv:{{editFrom.CLOSE_TIME}}</span>
            </div>
          </el-form-item>
<!--          <el-form-item label="MYAN_CLOSE_TIME">-->
<!--            <span>{{this.$to_myan_time(editFrom.CLOSE_TIME)}}</span>-->
<!--          </el-form-item>-->

          <el-form-item label="BAN_NUMS" prop="BAN_NUMS" span="11">
            <el-input
              v-model="editFrom.BAN_NUMS"
              @input="validateInput"
            />
          </el-form-item>


          <el-form-item label="BET_NUM" prop="BET_NUM">
            <el-input v-model="editFrom.BET_NUM" disabled readonly/>
          </el-form-item>
          <el-form-item label="BET_SUM" prop="BET_SUM">
            <el-input v-model="editFrom.BET_SUM" disabled readonly/>
          </el-form-item>
          <el-form-item label="BENEFIT" prop="BENEFIT">
            <el-input v-model="editFrom.BENEFIT" disabled readonly/>
          </el-form-item>
          <el-form-item label="CREATOR" prop="CREATOR">
            <el-input v-model="editFrom.CREATOR" disabled readonly/>
          </el-form-item>
          <el-form-item label="UPDATER" prop="UPDATER">
            <el-input v-model="editFrom.UPDATER" disabled readonly/>
          </el-form-item>

          <el-form-item label="LIMIT_CODE" prop="LIMIT_CODE">
            <el-input v-model="editFrom.LIMIT_CODE" oninput="value = value.replace(/\D/g,'')" />
          </el-form-item>
          <el-form-item label="LIMIT_NUM" prop="LIMIT_NUM">
            <el-input v-model="editFrom.LIMIT_NUM" oninput="value = value.replace(/\D/g,'')"/>
          </el-form-item>
          <el-form-item label="EX_LIMIT" prop="EX_LIMIT">
            <el-input v-model="editFrom.EX_LIMIT" oninput="value = value.replace(/\D/g,'')"/>
          </el-form-item>
          <el-form-item label="SINGLE_MIN" prop="SINGLE_MIN">
            <el-input v-model="editFrom.SINGLE_MIN" oninput="value = value.replace(/\D/g,'')"/>
          </el-form-item>
          <el-form-item label="SINGLE_MAX" prop="SINGLE_MAX">
            <el-input v-model="editFrom.SINGLE_MAX" oninput="value = value.replace(/\D/g,'')"/>
          </el-form-item>
          <el-form-item label="USER_MAX" prop="USER_MAX">
            <el-input v-model="editFrom.USER_MAX" oninput="value = value.replace(/\D/g,'')"/>
          </el-form-item>
          <el-form-item label="NUM_USER_LIMIT" prop="USER_MAX">
            <el-input v-model="editFrom.NUM_USER_LIMIT" oninput="value = value.replace(/\D/g,'')"/>
          </el-form-item>

          <el-form-item label="REMARK" prop="REMARK">
            <el-input
              v-model="editFrom.REMARK"
              :autosize="{ minRows: 2, maxRows: 4 }"
              type="textarea"
              placeholder="Please input"
            />
          </el-form-item>
        </div>
      </el-form>
        <el-collapse v-model="activeName" v-if="editFrom.ID">
          <!--          <el-collapse @change="getDigitDetail(editFrom.ID,$event)" v-model="activeName">-->
          <el-collapse-item title="Detail" name="1">
            <!--            <el-row>-->
            <!--              <el-radio-group :disabled="editFrom.DIGIT_STATUS_OPTIONS==3" v-model="historyStatus" @change="getDigitDetail(editFrom.ID)">-->
            <!--                <el-radio :label="true">Current</el-radio>-->
            <!--                <el-radio :label="false">History</el-radio>-->
            <!--              </el-radio-group>-->
            <!--            </el-row>-->
            <el-form
              ref="dataForm"
              :rules="rules"
              :model="editFrom"
              label-position="left"
              label-width="80px"
            >
            <div class="lb">
              <el-row>
                <el-form-item label="Bet Total:"><el-input v-model="bet_sum_total" readonly></el-input></el-form-item>
<!--                <el-form-item :label="String(bet_sum_total)"></el-form-item>-->
              </el-row>
            </div>
            <div class="cb">
              <el-form-item label="Num" v-for="i in row_count" :key="i">
                <el-row class="text-center">
                  <el-col :span="24">
                    <span>Amount / Limit</span>
                  </el-col>
                </el-row>
              </el-form-item>
            </div>
            <div class="cb">
              <el-form-item
                :label="item.num"
                v-for="item in bet_sum"
                :key="item.num"
              >
                <el-row class="text-center">
                  <el-col :span="12">
                    <el-input
                      style="text-align:right"
                      v-model="item.money"
                      readonly
                    />
                  </el-col>
                  <el-col :span="12">
                    <span>{{item.num_limit}}</span>
                  </el-col>
                </el-row>
              </el-form-item>
            </div>
            </el-form>
          </el-collapse-item>
        </el-collapse>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">Cancel</el-button>
        <el-button
          type="primary"
          @click="dialogStatus === 'create' ? createData() : updateData()"
        >Confirm
        </el-button
        >
      </div>
    </el-dialog>


    <!--order details-->
    <el-dialog
      :visible.sync="reportVisible"
      title="Digital Report"
      custom-class="dialogwidth"
    >
      <digitReport></digitReport>
    </el-dialog>
    <el-dialog
      :visible.sync="orderVisible"
      title="Digital Order"
      custom-class="dialogwidth">
      <DigitalOrderList></DigitalOrderList>
    </el-dialog>
  </div>
</template>

<script>
  import waves from "@/directive/waves"; // waves directive
  import {adjust_obj_prop, parseTime} from "@/utils";
  import digitReport from '@/views/financial/digital-totalcount'
  import DigitalOrderList from '@/views/platform/components/digital-order-list'
  import Pagination from "@/components/Pagination"; // secondary package based on el-pagination
  import Vue from "vue";
  import {
    getDigitList,
    addDigitByList,
    addDigit,
    delDigit,
    editDigit,
    settlementDigit,
    cancelDigit,
    addDigitSettle,
    reverseDigitSettle,
    getDigitDetail,
    getDigitHistoryDetail, cancel3DDigit, reverse3DDigitSettle,
  } from "@/api/digit";

  import {dateToString, dateToString2, stringToDate} from "@/utils/date-format";
  import {getOrderHistoryList, getOrderList} from "@/api/order";
  import XLSX from "xlsx";
  import DigitReport from "@/views/financial/digital-totalcount";

  export default {
    name: "ComplexTable",
    components: {DigitReport, Pagination,DigitalOrderList},
    directives: {waves},
    filters: {
      statusFilter(status) {
        const statusMap = {
          published: "success",
          draft: "info",
          deleted: "danger",
        };
        return statusMap[status];
      },
    },
    props: {
      beforeUpload: Function, // eslint-disable-line
      onSuccess: Function, // eslint-disable-line
    },
    data() {
      return {
        excelData: {
          header: null,
          results: null,
        },
        DigitStatus: {
          NotOpened: 0,
          Opened: 1,
          Closed: 2,
          Settled: 3,
        },
        StatusLabel: [
           "NotOpened",
           "Opened",
           "Closed",
           "Settled",
    ],
        orderDetails: [], // 混合单详情
        orderDetailsLoading: [],
        reportVisible: false,
        orderVisible: false,
        orderStatus: true,
        betTotal: 0,
        reward: 0,
        bet_sum: [],
        row_count: 0,
        intervalID:null,
        historyStatus: true,
        activeName: ["1"],
        total_bet_count: 0, // 订单总数量
        total_bet_sum: 0, // 订单总数额
        total_benefit: 0, // 总奖金
        orderList: [], // 比赛相关订单
        ordersVisible: false, // 比赛订单对话框
        orderListLoading: false, // 比赛订单加载状态
        ordersTotal: 0, // 比赛相关订单总数
        orderListQuery: {
          page: 1,
          limit: 99,
        }, // 比赛订单查询条件
        dialogCancelVisible: false,
        radio: "2",
        tableKey: 0,
        list: null,
        total: 0,
        excelLoading: false,
        listLoading: true,
        settlementDialogs: false,
        screenWidth: document.body.clientWidth,
        listQuery: {
          startTime: "",
          endTime: "",
          page: 1,
          limit: 99,
          DigitId: undefined,
          reverse: 1,
        },
        importanceOptions: [1, 2, 3],
        sortOptions: [
          {label: "ID Ascending", key: "+id"},
          {label: "ID Descending", key: "-id"},
        ],
        statusOptions: ["published", "draft", "deleted"],
        showReviewer: false,
        bet_sum_total:0,
        match_id:0,
        editFrom: {
          STAGE: "",
          ODDS: "",
          STATUS: "",
          OPEN_TIME: new Date(),
          CLOSE_TIME: new Date(),
          BET_NUM: "",
          BET_SUM: "",
          BENEFIT: "",
          RESULT: "",
          CREATE_TIME: new Date(),
          UPDATE_TIME: new Date(),
          CREATOR: "",
          UPDATER: "",
          REMARK: "",
        },
        dialogFormVisible: false,
        dialogStatus: "",
        textMap: {
          update: "Edit",
          create: "Create",
        },
        deleteDialogVisible: false,
        pvData: [],
        rules: {
          type: [
            {required: true, message: "type is required", trigger: "change"},
          ],
          Digit_TIME: [
            {
              type: "date",
              required: true,
              message: "timestamp is required",
              trigger: "change",
            },
          ],
          Digit_DESC: [
            {required: true, message: "title is required", trigger: "blur"},
          ],
        },
        downloadLoading: false,
        selectedDigit: "",
      };
    },
    created() {
      this.getList();
    },
    mounted() {
      const that = this;
      window.onresize = () => {
        window.screenWidth = document.body.clientWidth;
        that.screenWidth = window.screenWidth;
      };
    },
    watch: {
      screenWidth(newVal){
        this.row_count = parseInt(document.body.offsetWidth / 530);
      },

    },
    methods: {
      validateInput() {
        // 确保没有重复的逗号
        while (/,,/.test(this.editFrom.BAN_NUMS)) {
          this.editFrom.BAN_NUMS = this.editFrom.BAN_NUMS.replace(/,,/, ',');
        }

        // 分割字符串，对每个元素进行处理
        let parts = this.editFrom.BAN_NUMS.split(',');
        for (let i = 0; i < parts.length; i++) {
          // 确保每部分最多只有2位数字
          if (parts[i].length > 2) {
            parts[i] = parts[i].substring(0, 2);
          }
          // 确保只包含数字
          parts[i] = parts[i].replace(/[^0-9]/g, '');
        }

        // 重新连接字符串
        this.editFrom.BAN_NUMS = parts.join(',');
      },
      setOrderList(row) {
        this.ordersVisible = true;
        this.selectedDigit = row;
        this.orderStatus = true;
        this.getOrderList();
      },
      // 获取比赛相关订单
      getOrderList() {
        var _this = this;
        _this.orderListQuery.Digit_id = _this.selectedDigit.Digit_ID;
        _this.orderListLoading = true;
        _this.orderListQuery.is_group = 1;
        (_this.orderStatus
            ? getOrderList(_this.orderListQuery)
            : getOrderHistoryList(_this.orderListQuery)
        ).then((res) => {
          _this.orderListLoading = false;
          if (res.code === 20000) {
            _this.orderList = res.items;

            _this.orderList.forEach((element) => {
              if (element.BET_HOST_TEAM_RESULT === "100") {
                element.BET_HOST_TEAM_RESULT = "-";
              }
              if (element.BET_GUEST_TEAM_RESULT === "100") {
                element.BET_GUEST_TEAM_RESULT = "-";
              }
              if (element.DRAW_BUNKO === "0") {
                element.DRAW_ODDS = "+" + element.DRAW_ODDS;
              } else {
                element.DRAW_ODDS = "-" + element.DRAW_ODDS;
              }
            });
            _this.betTotal = res.total_bet;
            _this.reward = res.total_bonus;
            _this.ordersTotal = res.total;
          }
        });
      },
      noonRadioChange(val){

        let noon = val===1?'AM':'PM'
        let data = this.editFrom.STAGE.replace('am',noon).replace('pm',noon).
        replace('AM',noon).replace('PM',noon)
        this.$set(this.editFrom,'STAGE',data)
        this.handleCreate(1,noon)
      },
      radioChange() {
        if (this.radio === "2") {
          delete this.listQuery.is_game_over;
        } else {
          this.listQuery.is_game_over = this.radio;
        }
      },
      deleteAttr(row) {
        (this.DigitStatus ? this.editFrom.ATTR : this.editFrom.VIP_ATTR).splice(
          row.index - 1,
          1
        );
      },
      addAttr() {
        // 获取序号
        const _index =
          (this.DigitStatus ? this.editFrom.ATTR : this.editFrom.VIP_ATTR)
            .length + 1;
        (this.DigitStatus ? this.editFrom.ATTR : this.editFrom.VIP_ATTR).push({
          index: _index,
        });
      },
      getList() {
        this.listLoading = true;
        getDigitList(this.listQuery).then((response) => {
          this.listLoading = false;
          this.list = response.items;
          // console.log('getDigitList:', response.items)
          this.list.forEach((element) => {
            element.settlementLoading = false;
            element.cancelLoading = false;
          });
          this.total = response.total;
          this.total_bet_count = response.total_bet_count;
          this.total_bet_sum = response.total_bet_sum;
          this.total_benefit = response.total_benefit;
        });
      },
      handleFilter() {
        this.listQuery.page = 1;
        this.getList();
      },
      handleModifyStatus(row, status) {
        this.$message({
          message: "Success",
          type: "success",
        });
        row.status = status;
      },
      getDigitDetail(match_id, evt) {
        if (evt.length === 0) {
          return;
        }
        let _this = this;
        let reg = /(^\d{1}$)/
        let list = []
        let sum = 0
        _this.match_id = match_id
        let para = {match_id: match_id};
        let limit_num = _this.editFrom.LIMIT_NUM;
        (_this.editFrom.STATUS < 3
            ? getDigitDetail(para)
            : getDigitHistoryDetail(para)
        ).then((res) => {
          // if(res.items.length > 0){
          //   limit_num = res.items[0].LIMIT_NUM
          // }
          for (let i = 0; i < 100; i++) {
            let temp = {
              num: i.toString().padStart(2,'0'), money: '0' ,num_limit:_this.numFormat(limit_num)};
            res.items.forEach((ele) => {
              if (String(ele.BET_TYPE).padStart(2,'0') === temp.num) {
                sum += parseInt(ele.BET_MONEY)
                temp.money = _this.numFormat(parseInt(ele.BET_MONEY))
              }
            });
            list.push(temp);
          }
          Vue.set(_this.editFrom,'LIMIT_NUM',limit_num)
          _this.bet_sum = list
          _this.bet_sum_total = _this.numFormat(sum)
          // _this.bet_sum_total += ''
        });
      },
      numFormat(num){
        var res= num.toString().replace(/\d+/, function(n){ // 先提取整数部分
          return n.replace(/(\d)(?=(\d{3})+$)/g,function($1){
            return $1+",";
          });
        })
        return res;
      },
      showSettlement(row) {
        this.editFrom = Object.assign({}, row); // copy obj
        this.editFrom.Digit_TIME = stringToDate(this.editFrom.Digit_TIME);
        this.editFrom.CLOSE_TIME = stringToDate(this.editFrom.CLOSE_TIME);

        if (this.editFrom.IS_GAME_OVER === "1") {
          this.$message({
            message: "The game is settled",
            type: "error",
          });
          return;
        }

        if (this.editFrom.RESULT> -1 ) {
          this.settlementDialogs = true;
        } else {
          this.$message({
            message: "Please enter the RESULT of this stage first",
            type: "error",
          });
        }
      },
      handleSettlement() {
        let _this = this;
        _this.editFrom.settlementLoading = false;
        let para = {
          digit_id: _this.editFrom.ID,
        };

        const loading = this.$loading({
          lock: true,
          text: "Loading",
          spinner: "el-icon-loading",
          background: "rgba(0, 0, 0, 0.7)",
        });

        setTimeout(() => {
          loading.close();
        }, 1.5 * 1000);
        settlementDigit(para).then((res) => {
          loading.close();
          if (res.code === 20000) {
            _this.$message({
              message: "Add settlement Success",
              type: "success",
            });
            _this.getList();
          } else {
            _this.$message({
              message: "Add settlement Fail",
              type: "fail",
            });
          }
          _this.editFrom.settlementLoading = true;
          _this.settlementDialogs = false;
        });
      },
      addSettle(row) {
        var _this = this;
        if (row.IS_GAME_OVER === "1") {
          this.$message({
            message: "The game is settled",
            type: "error",
          });
          return;
        }

        if (!(row.HOST_TEAM_RESULT && row.GUEST_TEAM_RESULT)) {
          this.$message({
            message: "Please enter the score of this field first",
            type: "error",
          });
          return;
        }
        var para = {
          Digit_id: row.Digit_ID,
        };
        const loading = this.$loading({
          lock: true,
          text: "Loading",
          spinner: "el-icon-loading",
          background: "rgba(0, 0, 0, 0.7)",
        });
        setTimeout(() => {
          loading.close();
        }, 1.5 * 1000);
        addDigitSettle(para).then((res) => {
          loading.close();
          if (res.code === 20000) {
            _this.$message({
              message: "Add settle Success",
              type: "success",
            });
            _this.getList();
          } else {
            _this.$message({
              message: "Add settlement Fail",
              type: "fail",
            });
          }
        });
      },
      reverseDigit(row) {
        var _this = this;
        var para = {
          Digit_id: row.Digit_ID,
        };
        const loading = this.$loading({
          lock: true,
          text: "Loading",
          spinner: "el-icon-loading",
          background: "rgba(0, 0, 0, 0.7)",
        });
        setTimeout(() => {
          loading.close();
        }, 1.5 * 1000);
        reverseDigitSettle(para).then((res) => {
          loading.close();
          if (res.code === 20000) {
            _this.$message({
              message: "Add reverse Success",
              type: "success",
            });
            _this.getList();
          } else {
            _this.$message({
              message: "Add reverse Fail",
              type: "fail",
            });
          }
        });
      },
      resetTemp() {
        let date = new Date()
        let month = date.getMonth() + 1
        let day = date.getDate()
        let STAGE = date.getFullYear() + '' + (month<10? "0" + month : month) + '' + (day<10? "0" + day : day) +'_AM'
        let date2 = dateToString(new Date(date.getFullYear(),date.getMonth(),date.getDate(),9,0,0))
        let date3 = dateToString(new Date(date.getFullYear(),date.getMonth(),date.getDate(),12,0,0))
        this.editFrom = {
          STAGE: STAGE,
          ODDS: "20",
          STATUS: 0,
          OPEN_TIME: date2,
          CLOSE_TIME: date3,
          RESULT: "",
          noon:1,
          EX_LIMIT: 50000,
          LIMIT_CODE: 10,
          LIMIT_NUM: 100000,
          SINGLE_MAX: 10000,
          SINGLE_MIN: 100,
          USER_MAX: 50000,
          NUM_USER_LIMIT: 20000,
          REMARK: "",
        };
      },
      handleCreate(evt,noon='AM') {
        noon === 'AM' ? this.resetTemp() : '';
        this.dialogStatus = "create";
        let origin_data = this.list.find((ele)=>{
          return ele.STAGE.split('_').includes(noon)
        })
        let data = origin_data ? origin_data : this.list[0]
        if(data){
          data = adjust_obj_prop(data,['CLOSE_TIME','EX_LIMIT','LIMIT_CODE','LIMIT_NUM','NUM_USER_LIMIT','ODDS','OPEN_TIME','SINGLE_MAX','SINGLE_MIN','USER_MAX',])
          this.editFrom = Object.assign(this.editFrom,data)
        }
        this.$set(this.editFrom,'OPEN_TIME',this.$get_date_with_time(this.editFrom.OPEN_TIME))
        this.$set(this.editFrom,'CLOSE_TIME',this.$get_date_with_time(this.editFrom.CLOSE_TIME))
        this.$set(this.editFrom,'OPEN_MD_TIME',this.$to_myan_time(this.editFrom.OPEN_TIME))
        this.$set(this.editFrom,'CLOSE_MD_TIME',this.$to_myan_time(this.editFrom.CLOSE_TIME))
        // this.$set(this.editFrom,'CLOSE_MD_TIME',dateToString(new Date(stringToDate(this.editFrom.CLOSE_TIME).valueOf() - 5400 * 1000)))
        this.dialogFormVisible = true;
        // this.$nextTick(() => {
        //   this.$refs["dataForm"].clearValidate();
        // });
      },
      cancelDigitHandle() {
        var row = this.selectedDigit;
        this.editFrom = Object.assign({}, row); // copy obj

        this.editFrom.cancelLoading = true;

        var para = {
          Digit_id: this.editFrom.Digit_ID,
        };

        if (this.editFrom.IS_GAME_OVER === "1") {
          this.$message({
            message: "The game has ended and cannot be cancelled!",
            type: "error",
          });
          return;
        }

        cancelDigit(para).then((res) => {
          if (res.code === 20000) {
            this.getList();
            this.$message({
              message: "Cancel Success!",
              type: "success",
            });
          } else {
            this.$message({
              message: "Cancel Fail!",
              type: "success",
            });
          }
          this.dialogCancelVisible = false;
          this.editFrom.cancelLoading = false;
        });
      },
      createData() {
        let _this = this;
        let para = Object.assign({},_this.editFrom);
        if(para.BAN_NUMS){
          para.BAN_NUMS = Array.from(new Set(para.BAN_NUMS.split(',')))
            .sort((a, b) => a - b)
            .join(',')
        }
        addDigit(para).then((response) => {
          _this.dialogFormVisible = false;
          if (response.code === 20000) {
            _this.$message({
              message: response.message,
              type: "success",
            });
            _this.getList();
          }
        });
      },
      refresh_date(){
        let time = 5
        this.intervalID = setInterval(() => {
          let _this = this
          if (_this.$route.path !== '/match/digital-list' || !_this.dialogFormVisible) {
            _this.stop_refresh_data()
          } else if(_this.dialogFormVisible){
            _this.getDigitDetail(_this.match_id, [1, 2])
          }
        }, time * 1000)
      },
      stop_refresh_data(){
        window.clearInterval(this.intervalID)
        this.intervalID = null
      },
      handleUpdate(row) {
        this.editFrom = Object.assign({}, row);
        // this.editFrom.OPEN_TIME = stringToDate(this.editFrom.OPEN_TIME)
        // this.editFrom.CLOSE_TIME = stringToDate(this.editFrom.CLOSE_TIME)
        this.historyStatus = true;
        // this.getDigitDetai(row.ID)
        this.activeName = ["1"];
        this.row_count = parseInt(document.body.offsetWidth / 500);
        this.getDigitDetail(row.ID, [1, 2]);
        this.$set(this.editFrom,'OPEN_MD_TIME',this.$to_myan_time(this.editFrom.OPEN_TIME))
        this.$set(this.editFrom,'CLOSE_MD_TIME',this.$to_myan_time(this.editFrom.CLOSE_TIME))
        this.refresh_date()
        this.dialogStatus = "update";
        this.dialogFormVisible = true;
      },
      updateData() {
        const _this = this;
        let para = Object.assign({}, _this.editFrom);
        delete para.BENEFIT
        delete para.BET_NUM
        delete para.BET_SUM
        delete para.UPDATE_TIME
        delete para.CREATE_TIME
        if(para.BAN_NUMS){
          para.BAN_NUMS = Array.from(new Set(para.BAN_NUMS.split(',')))
            .sort((a, b) => a - b)
            .join(',')
        }
        editDigit(para).then((response) => {
          if (response.code === 20000) {
            _this.$message({
              message: response.message,
              type: "success",
            });
            this.dialogFormVisible = false;
            _this.getList();
          }
        });
      },
      deleteDigit: function () {
        this.deleteDialogVisible = false;
        setTimeout(() => {
          this.listLoading = false;
        }, 1.5 * 1000);
        delDigit({ID: this.selectedDigit.ID}).then((res) => {
          this.listLoading = false;
          if(res.code === 20000){

            this.$notify({
              title: "Success",
              message: "Delete Successfully",
              type: "success",
              duration: 2000,
            });
            const index = this.list.indexOf(this.selectedDigit);
            this.list.splice(index, 1);
          }
        });
      },
      tableFormatter(row, column, cellValue, index) {
        let str = ''
        switch (column.property) {
          case 'OPEN_TIME':
            str = this.$to_myan_time(row.OPEN_TIME)
            break
          case 'CLOSE_TIME':
            str = this.$to_myan_time(row.CLOSE_TIME)
            break
        }
        return str
      },
      handleDelete(row) {
        this.deleteDialogVisible = true;
        this.selectedDigit = row;
      },
      formatJson(filterVal, jsonData) {
        return jsonData.map((v) =>
          filterVal.map((j) => {
            if (j === "timestamp") {
              return parseTime(v[j]);
            } else {
              return v[j];
            }
          })
        );
      },
      set_server_time(time,type){
        if(type === 1){
          this.$set(this.editFrom,'OPEN_TIME',this.$to_server_time(this.editFrom.OPEN_MD_TIME))
        }else{
          this.$set(this.editFrom,'CLOSE_TIME',this.$to_server_time(this.editFrom.CLOSE_MD_TIME))
        }
      },
      confirm_rc_dialog(match, type = 'cancel') {
        this.$confirm(`Confirm to ${type} the match(ID:${match.ID})`, 'Tips', {
          confirmButtonText: 'Confirm',
          cancelButtonText: 'Cancel',
          type: 'warning'
        }).then(() => {
          this.reverse_cancel_match(match, type)
        }).catch(() => {

        });
      },
      reverse_cancel_match(match, type = 'cancel') {
        let _this = this
        var para = {
          digit_id: match.ID,
        };
        (type === 'cancel' ? cancelDigit(para) : reverseDigitSettle(para)).then((res) => {
          if (res.code === 20000) {
            _this.$message({
              message: `Add ${type} success`,
              type: "success",
            });
            _this.getList();
          } else {
            _this.$message({
              message: `Add ${type} fail`,
              type: "fail",
            });
          }
        });
      },
    },
  };
</script>
<style>
  .el-button {
    margin-bottom: 3px;
    margin-left: 0 !important;
  }

  .dialogwidth {
    width: 80%;
  }

  .settlement-row {
    height: 50px;
    line-height: 50px;
    font-size: 16px;
  }

  .bg-purple-light {
    background: #e5e9f2;
  }

  .grid-content {
    border-radius: 4px;
    min-height: 36px;
  }

  .settlement-col {
    border: 1px solid lightgrey;
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

  .cb .el-form-item {
    display: inline-block;
    width: 300px;
    margin-left: 50px;
    margin-right: 50px;
  }

  .sublist {
    display: flex;
    align-items: center;
  }
</style>
