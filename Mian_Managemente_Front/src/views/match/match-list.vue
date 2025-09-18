<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.key_word"
        placeholder="key word"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />

      <el-date-picker v-model="listQuery.startTime" type="date" placeholder="Start"/>
      <el-date-picker v-model="listQuery.endTime" type="date" placeholder="End"/>

      <input
        ref="excel-upload-input"
        class="excel-upload-input"
        type="file"
        accept=".xlsx, .xls"
        style="display:none"
        @change="handleClick"
      >

      <el-radio v-model="radio" label="1" border @change="radioChange">Settled</el-radio>
      <el-radio v-model="radio" label="0" border @change="radioChange">Unsettlement</el-radio>
      <el-radio v-model="radio" label="2" border @change="radioChange">All</el-radio>

      <el-select v-model="listQuery.exception" class="filter-item" placeholder="Exception Status" @change="handleFilter" clearable>
        <el-option v-for="item in status_option" :key="item.value" :label="item.label" :value="item.value" />
      </el-select>

      <el-button
        v-waves
        class="filter-item"
        type="primary"
        icon="el-icon-search"
        @click="handleFilter"
      >Search
      </el-button>
      <el-button
        class="filter-item"
        style="margin-left: 10px;"
        type="primary"
        icon="el-icon-edit"
        @click="handleCreate"
      >Add
      </el-button>
      <el-button
        class="filter-item"
        style="margin-left: 10px;"
        :type="HideMatchList.length?'warning':'info'"
        icon="el-icon-s-claim"
        @click="showHideList"
      >{{`Hide Confirm:${HideMatchList.length}`}}
      </el-button>

      <el-button
        v-waves
        :loading="downloadLoading"
        class="filter-item"
        type="primary"
        icon="el-icon-download"
        @click="handleDownload"
      >Download Data Excel
      </el-button>

      <el-button type="primary" class="filter-item" icon="el-icon-download">
        <a href="http://ag.innwabet.com/excel/match_template.xls">Download Excel Template</a>
      </el-button>

      <el-button
        :loading="excelLoading"
        class="filter-item"
        icon="el-icon-upload2"
        type="primary"
        @click="handleUpload"
      >Upload Excel
      </el-button>
    </div>

    <el-table
      :key="tableKey"
      v-loading="listLoading"
      :data="list"
      border
      fit
      :row-class-name="tableRowClassName"
      highlight-current-row
      style="width: 100%;"
    >
      <el-table-column type="index" width="50"/>
      <el-table-column label="Match Number" prop="MATCH_ID" align="center" width="100px"/>
      <el-table-column label="Match Desc" prop="MATCH_DESC" max-width="8%" align="center"/>
      <el-table-column label="Time" prop="MATCH_TIME" width="95px" align="center"/>
      <el-table-column label="Time(Myanmar)" prop="MATCH_MD_TIME" width="95px" align="center"/>
      <el-table-column label="Home" prop="HOST_TEAM" max-width="6%" align="center"/>
      <el-table-column label="Away" prop="GUEST_TEAM" max-width="6%" align="center"/>
      <el-table-column label="Closing Time" prop="CLOSING_TIME" width="95px" align="center"/>
      <el-table-column label="Status" max-width="4%" align="center">
        <template slot-scope="{row}">
          <span>{{ row.CLOSING_STATE==1?'Closed':'Unsealed' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="League" prop="REMARK" max-width="6%" align="center"/>
      <el-table-column label="Create Time" prop="CREATE_TIME" width="95px" align="center"/>
      <el-table-column label="Update Time" prop="UPDATE_TIME" width="95px" align="center"/>
      <el-table-column label="Home Score" prop="HOST_TEAM_RESULT" width="80px" align="center"/>
      <el-table-column label="Away Score" prop="GUEST_TEAM_RESULT" width="80px" align="center"/>
<!--      <el-table-column label="VIP" width="50px" align="center">-->
<!--        <template slot-scope="{row}">-->
<!--          <span v-if="row.VIP_ATTR.length>0">Yes</span>-->
<!--          <span v-else>No</span>-->
<!--        </template>-->
<!--      </el-table-column>-->
      <el-table-column label="Finished" width="80px" align="center">
        <template slot-scope="{row}">
          <span>{{ row.IS_GAME_OVER==1?'Finished':'Unfinished' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Hide Reason" prop="HIDE_REASON" width="95px" align="center"/>
      <el-table-column label="Hide Statue" width="95px" align="center">
        <template slot-scope="{ row }">
          {{ hide_format(row.hide) }}
        </template>
      </el-table-column>

      <el-table-column
        label="operation"
        align="center"
        width="250px"
        class-name="small-padding fixed-width"
      >
        <template slot-scope="scope">
          <div style="text-align:left">
            <el-button type="primary" @click="handleUpdate(scope.row)">Edit</el-button>
            <el-button
              type="primary"
              v-if="scope.row.IS_GAME_OVER==0&&(scope.row.STATUS==0||scope.row.STATUS==4)"
              :loading="scope.row.settlementLoading"
              @click="showSettlement(scope.row)"
            >Settlement
            </el-button>
            <el-popover
              placement="top"
              v-if="scope.row.IS_GAME_OVER==1&&(scope.row.STATUS==0||scope.row.STATUS==4)"
              :ref="`popover-${scope.$index}`">
              <p>Wanner reverse this match?？</p>
              <div style="text-align: center; margin: 0">
                <el-button type="primary" size="mini"
                           @click="reverseMatch(scope.row,0),scope._self.$refs[`popover-${scope.$index}`].doClose()">
                  Confirm
                </el-button>
                <el-button type="danger" size="mini"
                           @click="reverseMatch(scope.row,1),scope._self.$refs[`popover-${scope.$index}`].doClose()">
                  Confirm（new）
                </el-button>
              </div>
              <el-button size="medium" type="danger" slot="reference">Reverse</el-button>
            </el-popover>
            <!--            <el-button-->
            <!--              type="primary"-->
            <!--              @click="addSettle(row)"-->
            <!--            >Add Settle</el-button>-->
            <el-button :type="scope.row.HasOrder?'success':'info'" @click="setOrderList(scope.row)">Orders</el-button>
            <el-button type="warning" v-if="scope.row.IS_GAME_OVER==0" :loading="scope.row.cancelLoading"
                       @click="handleCancel(scope.row)">Cancel
            </el-button>
            <el-button type="danger" @click="handleDelete(scope.row,'deleted')">Delete</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      :page-sizes="[20,50,99]"
      :page-size="99"
      @pagination="getList"
    />

    <el-dialog title="Settlement" :visible.sync="settlementDialogs" style="text-align:center;">
      <el-row class="settlement-row">
        <el-col :span="12" class="settlement-col">
          <div class="grid-content bg-purple-light">{{ temp.HOST_TEAM }}</div>
        </el-col>
        <el-col :span="12" class="settlement-col">
          <div class="grid-content bg-purple-light">{{ temp.GUEST_TEAM }}</div>
        </el-col>
      </el-row>
      <el-row class="settlement-row">
        <el-col :span="12" class="settlement-col">
          <div>{{ temp.HOST_TEAM_RESULT }}</div>
        </el-col>
        <el-col :span="12" class="settlement-col">
          <div>{{ temp.GUEST_TEAM_RESULT }}</div>
        </el-col>
      </el-row>
      <el-row style="margin-top:15px;">
        <el-col :span="24">
          <el-button type="primary" @click="handleSettlement(0)">Settlement</el-button>
          <el-button type="danger" @click="handleSettlement(1)">Settlement(new)</el-button>
          <el-button @click="settlementDialogs = false">Cancel</el-button>
        </el-col>
      </el-row>
    </el-dialog>

    <el-dialog
      :title="textMap[dialogStatus]"
      :visible.sync="dialogFormVisible"
      custom-class="dialogwidth">
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="temp"
        v-loading="dialogLoading"
        label-position="left"
        label-width="100px"
      >
        <div class="lb">
          <el-form-item label="Time" prop="MATCH_TIME">
            <!--prop="timestamp"-->
            <el-date-picker
              v-model="temp.MATCH_TIME"
              type="datetime"
              value-format="timestamp"
              placeholder="Please pick a date"
            />
          </el-form-item>
          <el-form-item label="Match Description" prop="MATCH_DESC">
            <el-input v-model="temp.MATCH_DESC"/>
          </el-form-item>

          <el-form-item label="HOME">
            <el-input v-model="temp.HOST_TEAM" placeholder="Please input"/>
          </el-form-item>
          <el-form-item label="Away">
            <el-input v-model="temp.GUEST_TEAM" placeholder="Please input"/>
          </el-form-item>

          <el-form-item label="Closing Time">
            <el-date-picker
              v-model="temp.CLOSING_TIME"
              type="datetime"
              value-format="timestamp"
              placeholder="Please pick a date"
            />
          </el-form-item>

          <el-form-item label="Statue">
            <el-select v-model="temp.CLOSING_STATE">
              <el-option
                v-for="item in CLOSING_STATE_OPTIONS"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="Home Score">
            <el-input v-model="temp.HOST_TEAM_RESULT" oninput="value = value.replace(/\D/g,'')" placeholder="Please input"/>
          </el-form-item>
          <el-form-item label="Away Score">
            <el-input v-model="temp.GUEST_TEAM_RESULT" oninput="value = value.replace(/\D/g,'')" placeholder="Please input"/>
          </el-form-item>

          <el-form-item label="League" prop="REMARK">
            <el-input
              v-model="temp.REMARK"
              :autosize="{ minRows: 2, maxRows: 4}"
              type="textarea"
              placeholder="Please input"
            />
          </el-form-item>

          <el-form-item label="Exception" prop="REMARK">
            <el-select v-model="temp.exception" class="filter-item" placeholder="Exception Status" >
              <el-option v-if="index !== 0" v-for="(item,index) in status_option" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>

          <el-form-item label="Hide" prop="REMARK">
            <el-select v-model="temp.hide" class="filter-item" placeholder="Exception Status" >
              <el-option value="0" label="No"/>
              <el-option value="1" label="Yes"/>
            </el-select>
          </el-form-item>

        </div>
        <el-row>
          <el-radio-group v-model="matchStatus" @change="">
            <el-radio :label="true">Normal</el-radio>
            <el-radio :label="false">VIP</el-radio>
          </el-radio-group>
          <el-button @click="getMatchDetail(temp)" type="primary" style="float: right;">SUM</el-button>
        </el-row>
        <div class="sublist">
          <el-table
            :key="tableKey"
            v-loading="listLoading"
            :data="matchStatus ? temp.ATTR : temp.VIP_ATTR"
            border
            fit
            highlight-current-row
            style="width: 100%;"
          >
            <el-table-column label="Index" width="50px" prop="index" align="center"/>

            <el-table-column label="Odds Type" align="center">
              <template slot-scope="{row}">
                <el-form :model="row">
                  <el-form-item>
                    <el-select v-model="row.MATCH_ATTR_TYPE" @change="handleMatchTypeChange(row)">
                      <el-option
                        :disabled="!matchStatus"
                        v-for="item in MATCH_ATTR_TYPE_OPTIONS"
                        :key="item.value"
                        :label="item.label"
                        :value="item.value"
                      />
                    </el-select>
                  </el-form-item>
                </el-form>
              </template>
            </el-table-column>

            <el-table-column label="(Home/Over/Odd)Odds" align="center">
              <template slot-scope="{row}">
                <el-form :model="row">
                  <el-form-item>
                    <el-input v-model="row.ODDS" :disabled="row.MATCH_ATTR_TYPE != '10'"/>
                  </el-form-item>
                </el-form>
              </template>
            </el-table-column>
            <el-table-column label="(Away/Under/Even)Odds" align="center">
              <template slot-scope="{row}">
                <el-form :model="row">
                  <el-form-item>
                    <el-input v-model="row.ODDS_GUEST" :disabled="row.MATCH_ATTR_TYPE != '10'"/>
                  </el-form-item>
                </el-form>
              </template>
            </el-table-column>

            <el-table-column label="HDP" align="center">
              <template v-if="row.MATCH_ATTR_TYPE ==1 || row.MATCH_ATTR_TYPE == 4" slot-scope="{row}">
                <el-form :model="row">
                  <el-form-item>
                    <el-select v-model="row.LOSE_TEAM">
                      <el-option
                        :disabled="!matchStatus"
                        v-for="item in LOSE_TEAM_OPTIONS"
                        :key="item.value"
                        :label="item.label"
                        :value="item.value"
                      />
                    </el-select>
                  </el-form-item>
                </el-form>
              </template>
            </el-table-column>
            <el-table-column label="Balls" align="center">
              <template v-if="row.MATCH_ATTR_TYPE != 6 && row.MATCH_ATTR_TYPE != 7" slot-scope="{row}">
                <el-form :model="row">
                  <el-form-item>
                    <el-input v-model="row.LOSE_BALL_NUM" :disabled="!matchStatus"/>
                  </el-form-item>
                </el-form>
              </template>
            </el-table-column>
            <el-table-column label="Give Away" align="center">
              <template v-if="row.MATCH_ATTR_TYPE != 6 && row.MATCH_ATTR_TYPE != 7" slot-scope="{row}">
                <el-form :model="row">
                  <el-form-item>
                    <el-select v-model="row.DRAW_BUNKO">
                      <el-option
                        :disabled="!matchStatus"
                        v-for="item in DRAW_BUNKO_OPTIONS"
                        :key="item.value"
                        :label="item.label"
                        :value="item.value"
                      />
                    </el-select>
                  </el-form-item>
                </el-form>
              </template>
            </el-table-column>

            <el-table-column label="(Draw)Odds" align="center">
              <template v-if="row.MATCH_ATTR_TYPE != 6 && row.MATCH_ATTR_TYPE != 7" slot-scope="{row}">
                <el-form :model="row">
                  <el-form-item>
                    <el-input v-model="row.DRAW_ODDS" :disabled="!matchStatus"/>
                  </el-form-item>
                </el-form>
              </template>
            </el-table-column>
            <el-table-column label="Bet Total" prop="BET_TOTAL" align="center">
            </el-table-column>
            <el-table-column label="Delete" align="center" class-name="small-padding fixed-width">
              <template slot-scope="{row}">
                <el-button type="danger" icon="el-icon-delete" :disabled="!matchStatus" circle
                           @click="deleteAttr(row)"/>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <el-row>
          <el-button type="primary" icon="el-icon-plus" :disabled="!matchStatus" @click="addAttr()"/>
        </el-row>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">Cancel</el-button>
        <el-button type="primary" @click="dialogStatus==='create'?createData():updateData()">Confirm</el-button>
      </div>
    </el-dialog>

    <el-dialog :visible.sync="dialogPvVisible" title="删除比赛">
      <h2 style="text-align:center">确定删除该场比赛？</h2>
      <!-- <el-table :data="pvData" border fit highlight-current-row style="width: 100%">
        <el-table-column prop="key" label="Channel" />
        <el-table-column prop="pv" label="Pv" />
      </el-table>-->
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogPvVisible = false">Cancel</el-button>
        <el-button type="primary" @click="deleteMatch">Confirm</el-button>
      </span>
    </el-dialog>

    <el-dialog :visible.sync="dialogCancelVisible" title="取消比赛">
      <h2 style="text-align:center">Cancel this game will return all orders, confirm cancellation?</h2>
      <!-- <el-table :data="pvData" border fit highlight-current-row style="width: 100%">
        <el-table-column prop="key" label="Channel" />
        <el-table-column prop="pv" label="Pv" />
      </el-table>-->
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogCancelVisible = false">Cancel</el-button>
        <el-button type="primary" @click="cancelMatchHandle(0)">Confirm</el-button>
        <el-button type="danger" @click="cancelMatchHandle(1)">Confirm(new)</el-button>
      </span>
    </el-dialog>

    <el-dialog :visible.sync="ordersVisible" title="Match Orders" custom-class="dialogwidth">
      <div class="filter-container">

        <el-radio-group v-model="orderStatus" @change="getOrderList">
          <el-radio :label="true">Current</el-radio>
          <el-radio :label="false">History</el-radio>
        </el-radio-group>
        <span style="margin-right:15px;">Total Amount:{{ betTotal }}</span>
        <span>Total bonus:{{ reword }}</span>
      </div>

      <el-table
        :key="tableKey"
        v-loading="orderListLoading"
        :data="orderList"
        border
        fit
        highlight-current-row
        style="width: 100%;"
      >
        <el-table-column label="Order Number" prop="ORDER_ID" align="center" width="100px"/>
        <el-table-column label="UserId" prop="USER_ID" width="80px" align="center"/>
        <el-table-column label="Nickname" prop="USER_NAME" width="95px" align="center"/>
        <el-table-column label="Match Number" prop="MATCH_ID" width="95px" align="center"/>
        <el-table-column label="Order Desc" prop="ORDER_DESC" max-width="6%" align="center"/>
        <el-table-column label="Order Type" max-width="6%" align="center">

          <template slot-scope="{row}">
            <span v-if="row.ORDER_TYPE==1">B_Body</span>
            <span v-else-if="row.ORDER_TYPE==2">B_Goal</span>
            <!--<span v-else-if="row.ORDER_TYPE==3">波胆</span>-->
            <span v-else-if="row.ORDER_TYPE==4">M_Body</span>
            <span v-else-if="row.ORDER_TYPE==5">M_Goal</span>
            <span v-else-if="row.ORDER_TYPE==6">B_OE</span>
            <span v-else-if="row.ORDER_TYPE==7">M_OE</span>
            <span v-else-if="row.ORDER_TYPE==10">B_1X2</span>
          </template>

        </el-table-column>
        <el-table-column label="Amount" prop="BET_MONEY" :formatter="tableFormat" width="95px" align="center"/>
        <el-table-column label="Bet Type" max-width="6%" align="center">
          <template slot-scope="{row}">
            <div v-if="row.ORDER_TYPE==1 || row.ORDER_TYPE==4">
              <span v-if="row.BET_TYPE==1">Home</span>
              <span v-else>Away</span>
            </div>
            <div v-if="row.ORDER_TYPE==2 || row.ORDER_TYPE==5">
              <span v-if="row.BALL_TYPE==1">Over</span>
              <span v-else>Under</span>
            </div>
            <div v-if="row.ORDER_TYPE==6 || row.ORDER_TYPE==7">
              <span v-if="row.BET_TYPE==1">Odd</span>
              <span v-else>Even</span>
            </div>
            <div v-if="row.ORDER_TYPE==10 || row.ORDER_TYPE==11">
              <span v-if="row.BET_TYPE==1">Home</span>
              <span v-else-if="row.BET_TYPE==3">Draw</span>
              <span v-else>Away</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Create Time" prop="CREATE_TIME" width="95px" align="center"/>
        <el-table-column label="Update Time" prop="UPDATE_TIME" width="95px" align="center"/>
        <el-table-column label="Remark" prop="REMARK" width="80px" align="center"/>
        <el-table-column
          label="Home Score"
          prop="BET_HOST_TEAM_RESULT"
          width="50px"
          align="center"
        />
        <el-table-column
          label="Away Score"
          prop="BET_GUEST_TEAM_RESULT"
          width="50px"
          align="center"
        />
        <el-table-column label="Order Status" width="50px" align="center">
          <template slot-scope="{row}">
            <span v-if="row.STATUS==1">effective</span>
            <span v-else>invalid</span>
          </template>
        </el-table-column>
        <el-table-column label="Mixed" width="50px" align="center">
          <template slot-scope="{row}">
            <span v-if="row.IS_MIX==1">Yes</span>
            <span v-else>No</span>
          </template>
        </el-table-column>
        <el-table-column label="Order Result" width="50px" align="center">
          <template slot-scope="{row}">
            <span v-if="row.IS_WIN==1">Win</span>
            <span v-if="row.IS_WIN==0">Lose</span>
            <span v-else>Not</span>
          </template>
        </el-table-column>
        <el-table-column label="Bonus" prop="BONUS" :formatter="tableFormat" width="80px" align="center"/>
        <el-table-column label="Odds" prop="BET_ODDS" width="50px" align="center"/>
        <el-table-column label="HDP" prop="LOSE_TEAM" width="50px" align="center">

          <template slot-scope="{row}">
            <span v-if="row.LOSE_TEAM==1">Home</span>
            <span v-if="row.LOSE_TEAM==2">Away</span>
          </template>

        </el-table-column>
        <el-table-column label="Balls" prop="LOSE_BALL_NUM" width="50px" align="center"/>
        <el-table-column label="DRAW_ODDS" prop="DRAW_ODDS" width="50px" align="center"/>
        <el-table-column label="Details" prop="MIX_DETAIL" width="100px" align="center">
          <template slot-scope="{row}">
            <el-button v-if="row.IS_MIX==1" type="info" @click="showDetails(row.ORDER_ID)">details</el-button>
          </template>
        </el-table-column>
      </el-table>

      <pagination
        v-show="ordersTotal>0"
        :total="ordersTotal"
        :page.sync="orderListQuery.page"
        :page-sizes="[20,50,99]"
        :page-size="99"
        :limit.sync="orderListQuery.limit"
        @pagination="getOrderList"
      />
    </el-dialog>

    <el-dialog
      :visible.sync="orderDetailsVisible"
      title="Orders Details"
      custom-class="dialogwidth"
    >
      <el-table
        :key="tableKey"
        v-loading="orderDetailsLoading"
        :data="orderDetails"
        border
        fit
        highlight-current-row
        style="width: 100%;"
      >
        <el-table-column label="#" type="index" width="50px"/>
        <el-table-column label="Order Number" prop="ORDER_ID" max-width="8%" align="center"/>
        <el-table-column label="User Id" prop="USER_ID" width="95px" align="center"/>
        <el-table-column label="Nickname" prop="USER_NAME" width="95px" align="center"/>
        <el-table-column label="Match Number" prop="MATCH_ID" max-width="6%" align="center"/>
        <el-table-column label="Order Desc" prop="ORDER_DESC" max-width="6%" align="center"/>
        <el-table-column label="Order Type" max-width="6%" align="center">

          <template slot-scope="{row}">
            <span v-if="row.ORDER_TYPE==1">B_Body</span>
            <span v-else-if="row.ORDER_TYPE==2">B_Goal</span>
            <!--<span v-else-if="row.ORDER_TYPE==3">波胆</span>-->
            <span v-else-if="row.ORDER_TYPE==4">M_Body</span>
            <span v-else-if="row.ORDER_TYPE==5">M_Goal</span>
            <span v-else-if="row.ORDER_TYPE==6">B_OE</span>
            <span v-else-if="row.ORDER_TYPE==7">M_OE</span>
            <span v-else-if="row.ORDER_TYPE==10">B_1X2</span>
          </template>

        </el-table-column>
        <el-table-column label="Amount" prop="BET_MONEY" :formatter="tableFormat" width="95px" align="center"/>
        <el-table-column label="Bet Type" max-width="6%" align="center">


          <template slot-scope="{row}">
            <div v-if="row.ORDER_TYPE==1 || row.ORDER_TYPE==4">
              <span v-if="row.BET_TYPE==1">Home</span>
              <span v-else>Away</span>
            </div>
            <div v-if="row.ORDER_TYPE==2 || row.ORDER_TYPE==5">
              <span v-if="row.BALL_TYPE==1">Over</span>
              <span v-else>Under</span>
            </div>
            <div v-if="row.ORDER_TYPE==6 || row.ORDER_TYPE==7">
              <span v-if="row.BET_TYPE==1">Odd</span>
              <span v-else>Even</span>
            </div>
            <div v-if="row.ORDER_TYPE==10 || row.ORDER_TYPE==11">
              <span v-if="row.BET_TYPE==1">Home</span>
              <span v-else-if="row.BET_TYPE==3">Draw</span>
              <span v-else>Away</span>
            </div>
          </template>

        </el-table-column>
        <el-table-column label="Create Time" prop="CREATE_TIME" width="95px" align="center"/>
        <el-table-column label="Update Time" prop="UPDATE_TIME" width="95px" align="center"/>
        <el-table-column label="Remark" prop="REMARK" width="80px" align="center"/>
        <el-table-column
          label="Home Score"
          prop="BET_HOST_TEAM_RESULT"
          width="50px"
          align="center"
        />
        <el-table-column
          label="Away Score"
          prop="BET_GUEST_TEAM_RESULT"
          width="50px"
          align="center"
        />
        <el-table-column label="Order Status" width="50px" align="center">
          <template slot-scope="{row}">
            <span v-if="row.STATUS==1">effective</span>
            <span v-else>invalid</span>
          </template>
        </el-table-column>
        <el-table-column label="Order Result" width="50px" align="center">
          <template slot-scope="{row}">
            <span v-if="row.IS_WIN==1">Win</span>
            <span v-if="row.IS_WIN==0">Lose</span>
          </template>
        </el-table-column>
        <el-table-column label="Bonus" prop="BONUS" :formatter="tableFormat" width="80px" align="center"/>
        <el-table-column label="Odds" prop="BET_ODDS" width="50px" align="center"/>
        <el-table-column label="HDP" prop="LOSE_TEAM" width="50px" align="center">
          <template slot-scope="{row}">
            <span v-if="row.LOSE_TEAM==1">Home</span>
            <span v-if="row.LOSE_TEAM==2">Away</span>
          </template>
        </el-table-column>
        <el-table-column label="Balls" prop="LOSE_BALL_NUM" width="50px" align="center"/>
        <el-table-column label="DRAW_ODDS" prop="DRAW_ODDS" width="50px" align="center"/>
      </el-table>
    </el-dialog>
    <el-dialog title="Hide Confirm" :visible.sync="dialogVisible" width="1200px">
      <el-table :data="HideMatchList" border style="width: 100%">
        <el-table-column type="index" width="50"/>
        <el-table-column label="Match Number" prop="MATCH_ID" align="center" width="100px"/>
        <el-table-column label="Match Desc" prop="MATCH_DESC" max-width="8%" align="center"/>
        <el-table-column label="Time" prop="MATCH_TIME" width="95px" align="center"/>
        <el-table-column label="Time(Myanmar)" prop="MATCH_MD_TIME" width="95px" align="center"/>
        <el-table-column label="Home" prop="HOST_TEAM" max-width="6%" align="center"/>
        <el-table-column label="Away" prop="GUEST_TEAM" max-width="6%" align="center"/>
        <el-table-column label="Closing Time" prop="CLOSING_TIME" width="95px" align="center"/>
        <el-table-column label="Status" max-width="4%" align="center">
          <template slot-scope="{row}">
            <span>{{ row.CLOSING_STATE==1?'Closed':'Unsealed' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Hide Reason" prop="HIDE_REASON" width="95px" align="center"/>
        <el-table-column label="Hide Statue" prop="hide" width="105px" align="center">
          <template slot-scope="{ row }">
            <el-select v-model="row.hide" placeholder="Hide Statue">
              <el-option
                v-for="item in HideStatusList"
                :key="item.value"
                :label="item.label"
                :value="item.value">
              </el-option>
            </el-select>
          </template>
        </el-table-column>

        <el-table-column label="Hide Confirm" prop="HIDE_CONFIRM" width="95px" align="center">
          <template slot-scope="{ row }">
            <el-button type="text" @click="HideConfirm([row])">Confirm</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">Close</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
  import waves from '@/directive/waves' // waves directive
  import {parseTime, onlyNumber, number_format} from '@/utils'
  import Pagination from '@/components/Pagination' // secondary package based on el-pagination
  import {
    getMatchList,
    getMatchDetail,
    addMatchByList,
    addMatch,
    delMatch,
    editMatch,
    settlementMatch,
    cancelMatch,
    addMatchSettle,
    reverseMatchSettle,getMatchHideWarning,setMatchHideState
  } from '@/api/match'

  import {dateToString, stringToDate} from '@/utils/date-format'
  import {getOrderHistoryList, getOrderList} from '@/api/order'
  import XLSX from 'xlsx'

  export default {
    name: 'ComplexTable',
    components: {Pagination},
    directives: {waves},
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
    props: {
      beforeUpload: Function, // eslint-disable-line
      onSuccess: Function // eslint-disable-line
    },
    data() {
      return {
        excelData: {
          header: null,
          results: null
        },
        orderDetails: [], // 混合单详情
        orderDetailsLoading: [],
        orderDetailsVisible: false,
        dialogLoading: false,
        orderStatus: true,
        matchStatus: true,
        betTotal: 0, // 订单总金额
        reword: 0, // 总奖金
        orderList: [], // 比赛相关订单
        ordersVisible: false, // 比赛订单对话框
        orderListLoading: false, // 比赛订单加载状态
        ordersTotal: 0, // 比赛相关订单总数
        orderListQuery: {
          page: 1,
          limit: 99
        }, // 比赛订单查询条件
        dialogCancelVisible: false,
        radio: '2',
        tableKey: 0,
        list: null,
        total: 0,
        excelLoading: false,
        listLoading: true,
        settlementDialogs: false,
        listQuery: {
          startTime: '',
          endTime: '',
          page: 1,
          limit: 99,
          matchId: undefined,
          reverse: 1
        },
        status_option: [
          {
            value: null,
            label: 'All'
          },
          {
            value: 0,
            label: 'Normal'
          },
          {
            value: 1,
            label: 'Abnormal'
          },
          // {
          //   value: 2,
          //   label: 'Exception'
          // },
        ],
        importanceOptions: [1, 2, 3],
        sortOptions: [
          {label: 'ID Ascending', key: '+id'},
          {label: 'ID Descending', key: '-id'}
        ],
        statusOptions: ['published', 'draft', 'deleted'],
        showReviewer: false,
        temp: {
          MATCH_ID: '',
          REMARK: '',
          MATCH_TIME: new Date(),
          IS_GAME_OVER: '',
          MATCH_DESC: '',
          CLOSING_TIME: new Date(),
          CLOSING_STATE: null,
          HOST_TEAM: '',
          GUEST_TEAM: '',
          HOST_TEAM_RESULT: '',
          GUEST_TEAM_RESULT: '',
          MATCH_MD_TIME: new Date(),
          UPDATE_TIME: new Date(),
          ATTR: []
        },
        dialogFormVisible: false,
        dialogStatus: '',
        textMap: {
          update: 'Edit',
          create: 'Create'
        },
        dialogPvVisible: false,
        pvData: [],
        rules: {
          type: [
            {required: true, message: 'type is required', trigger: 'change'}
          ],
          MATCH_TIME: [
            {
              type: 'date',
              required: true,
              message: 'timestamp is required',
              trigger: 'change'
            }
          ],
          MATCH_DESC: [
            {required: true, message: 'title is required', trigger: 'blur'}
          ]
        },
        CLOSING_STATE_OPTIONS: [
          {
            value: '0',
            label: 'Unsealed'
          },
          {
            value: '1',
            label: 'Closed'
          }
        ],
        MATCH_ATTR_TYPE_OPTIONS: [
          {
            value: '1',
            label: 'B_Body'
          },
          {
            value: '2',
            label: 'B_Goal'
          },
          // {
          //   value: "3",
          //   label: "单笔波胆"
          // },
          {
            value: '6',
            label: 'B_Odd/Even'
          },
          {
            value: '10',
            label: 'B_WDL'
          },
          {
            value: '4',
            label: 'M_Body'
          },
          {
            value: '5',
            label: 'M_Goal'
          },
          {
            value: '7',
            label: 'M_Odd/Even'
          }
        ],
        LOSE_TEAM_OPTIONS: [
          {
            value: '1',
            label: 'Home'
          },
          {
            value: '2',
            label: 'Away'
          }
        ],
        DRAW_BUNKO_OPTIONS: [
          {
            value: '0',
            label: '+'
          },
          {
            value: '1',
            label: '-'
          }
        ],
        HideStatusList: [
          {
            value: '0',
            label: 'Show'
          },
          {
            value: '1',
            label: 'Hide'
          }
        ],
        downloadLoading: false,
        selectedMatch: '',
        HideMatchList: [],
        dialogVisible: false,
      }
    },
    created() {
      this.getList()
      this.GetMatchHideWarning()
    },
    methods: {
      tableRowClassName({ row, rowIndex }) {
        if (row.exception == '1') {
          return 'warning-row'
        }else if (row.exception == '2') {
          return 'danger-row'
        }else if(row.hide == 1 && row.HIDE_CONFIRM=='0'){
          return 'row-red'
        }
        return '';
      },
      showDetails(order_id) {
        var _this = this
        var para = {order_id: order_id, is_group: 0}
        _this.orderDetailsVisible = true
        _this.orderDetailsLoading = true;
        (_this.orderStatus ? getOrderList(para) : getOrderHistoryList(para)).then(res => {
          _this.orderDetailsLoading = false
          if (res.code === 20000) {
            _this.orderDetails = []
            res.items.forEach(element => {
              if (element.BET_HOST_TEAM_RESULT == '100') {
                element.BET_HOST_TEAM_RESULT = '-'
              }
              if (element.BET_GUEST_TEAM_RESULT == '100') {
                element.BET_GUEST_TEAM_RESULT = '-'
              }
              if (element.DRAW_BUNKO == '0') {
                element.DRAW_ODDS = '+' + element.DRAW_ODDS
              } else {
                element.DRAW_ODDS = '-' + element.DRAW_ODDS
              }
              _this.orderDetails.push(element)
            })
          }
        })
      },
      generateData({header, results}) {
        this.excelData.header = header

        // 拆分数据 ，把盘口数据拆分到attr中
        this.excelData.results = results
        this.onSuccess && this.onSuccess(this.excelData)
        // 拆分数据提交到后端
        this.submitExcelData()
      },
      handleCancel(row) {
        this.dialogCancelVisible = true
        this.selectedMatch = row
      },
      handleMatchTypeChange(row) {
        row.odd_edit = false
        switch (row.MATCH_ATTR_TYPE) {
          case '1':
            row.ODDS = 1
            row.ODDS_GUEST = 1
            break
          case '2':
            row.ODDS = 1
            row.ODDS_GUEST = 1
            break
          case '4':
            row.ODDS = 2
            row.ODDS_GUEST = 2
            break
          case '5':
            row.ODDS = 2
            row.ODDS_GUEST = 2
            break
          case '10':
            row.odd_edit = true
            break
        }
      },
      // 订单列表过滤
      orderListFilter() {
      },
      setOrderList(row) {
        this.ordersVisible = true
        this.selectedMatch = row
        this.orderStatus = true
        this.getOrderList()
      },
      // 获取比赛相关订单
      getOrderList() {
        var _this = this
        _this.orderListQuery.match_id = _this.selectedMatch.MATCH_ID
        _this.orderListLoading = true
        _this.orderListQuery.is_group = 1;
        (_this.orderStatus ? getOrderList(_this.orderListQuery) : getOrderHistoryList(_this.orderListQuery)).then(res => {
          _this.orderListLoading = false
          if (res.code === 20000) {
            _this.orderList = res.items

            _this.orderList.forEach(element => {
              if (element.BET_HOST_TEAM_RESULT == '100') {
                element.BET_HOST_TEAM_RESULT = '-'
              }
              if (element.BET_GUEST_TEAM_RESULT == '100') {
                element.BET_GUEST_TEAM_RESULT = '-'
              }
              if (element.DRAW_BUNKO == '0') {
                element.DRAW_ODDS = '+' + element.DRAW_ODDS
              } else {
                element.DRAW_ODDS = '-' + element.DRAW_ODDS
              }
            })
            _this.betTotal = number_format(res.total_bet)
            _this.reword = number_format(res.total_bonus)
            _this.ordersTotal = res.total
          }
        })
      },
      submitExcelData() {
        var matchList = []

        this.excelData.results.forEach(element => {
          var mian_date = stringToDate(element.Time) // 缅甸时间
          mian_date = mian_date.getTime()
          mian_date -= 5400 * 1000
          mian_date = new Date(mian_date)

          var matchInfo = {
            MATCH_DESC: element.Home + ' VS ' + element.Away,
            MATCH_TIME: element.Time,
            CLOSING_TIME: element.Time,
            MATCH_MD_TIME: dateToString(mian_date),
            REMARK: element.League,
            HOST_TEAM: element.Home,
            GUEST_TEAM: element.Away,
            ATTR: []
          }

          debugger

          if (element.M_Body) {
            var m_body = []

            if (element.M_Body.indexOf('+') > -1) {
              m_body = element.M_Body.split('+')
              m_body[2] = '+'
            } else {
              m_body = element.M_Body.split('-')
              m_body[2] = '-'
            }

            // 混合胜负盘
            var mixedBodyAttr = {
              MATCH_ATTR_TYPE: 4,
              ODDS: 2,
              ODDS_GUEST: 2,
              DRAW_BUNKO: m_body[2] === '+' ? 0 : 1,
              DRAW_ODDS: m_body[1],
              CREATE_TIME: dateToString(new Date()),
              LOSE_TEAM: element.HDP === 'H' ? 1 : 2,
              LOSE_BALL_NUM: m_body[0]
            }

            matchInfo.ATTR.push(mixedBodyAttr)
          }

          if (element.M_Goal) {
            var m_Goal = []
            if (element.M_Goal.indexOf('+') > -1) {
              m_Goal = element.M_Goal.split('+')
              m_Goal[2] = '+'
            } else {
              m_Goal = element.M_Goal.split('-')
              m_Goal[2] = '-'
            }

            // 混合大小盘
            var mixedGoalAttr = {
              MATCH_ATTR_TYPE: 5,
              ODDS: 2,
              ODDS_GUEST: 2,
              DRAW_BUNKO: m_Goal[2] === '+' ? 0 : 1,
              DRAW_ODDS: m_Goal[1],
              CREATE_TIME: dateToString(new Date()),
              LOSE_TEAM: element.HDP === 'H' ? 1 : 2,
              LOSE_BALL_NUM: m_Goal[0]
            }

            matchInfo.ATTR.push(mixedGoalAttr)
          }

          if (element.M_Odd_Even) {
            var m_Odd = []
            if (element.M_Odd_Even.indexOf('/') > -1) {
              m_Odd = element.M_Odd_Even.split('/')
            }

            // 混合单双盘
            var mixedOddAttr = {
              MATCH_ATTR_TYPE: 7,
              ODDS: m_Odd[0],
              ODDS_GUEST: m_Odd[1],
              CREATE_TIME: dateToString(new Date())
            }

            matchInfo.ATTR.push(mixedOddAttr)
          }

          if (element.B_Body) {
            var b_body = []
            if (element.B_Body.indexOf('+') > -1) {
              b_body = element.B_Body.split('+')
              b_body[2] = '+'
            } else {
              b_body = element.B_Body.split('-')
              b_body[2] = '-'
            }

            // 单笔胜负盘
            var singgleBodyAttr = {
              MATCH_ATTR_TYPE: 1,
              ODDS: 1,
              ODDS_GUEST: 1,
              DRAW_BUNKO: b_body[2] === '+' ? 0 : 1,
              DRAW_ODDS: b_body[1],
              CREATE_TIME: dateToString(new Date()),
              LOSE_TEAM: element.HDP === 'H' ? 1 : 2,
              LOSE_BALL_NUM: b_body[0]
            }

            matchInfo.ATTR.push(singgleBodyAttr)
          }

          if (element.B_Goal) {
            var b_Goal = []
            if (element.B_Goal.indexOf('+') > -1) {
              b_Goal = element.B_Goal.split('+')
              b_Goal[2] = '+'
            } else {
              b_Goal = element.B_Goal.split('-')
              b_Goal[2] = '-'
            }

            // 单笔大小盘
            var singgleGoalAttr = {
              MATCH_ATTR_TYPE: 2,
              ODDS: 1,
              ODDS_GUEST: 1,
              DRAW_BUNKO: b_Goal[2] === '+' ? 0 : 1,
              DRAW_ODDS: b_Goal[1],
              CREATE_TIME: dateToString(new Date()),
              LOSE_TEAM: element.HDP === 'H' ? 1 : 2,
              LOSE_BALL_NUM: b_Goal[0]
            }

            matchInfo.ATTR.push(singgleGoalAttr)
          }

          if (element.B_Odd_Even) {
            var b_Odd = []
            if (element.B_Odd_Even.indexOf('/') > -1) {
              b_Odd = element.B_Odd_Even.split('/')
            }

            // 单笔单双盘
            var b_OddAttr = {
              MATCH_ATTR_TYPE: 6,
              ODDS: b_Odd[0],
              ODDS_GUEST: b_Odd[1],
              CREATE_TIME: dateToString(new Date())
            }

            matchInfo.ATTR.push(b_OddAttr)
          }

          matchList.push(matchInfo)
        })

        addMatchByList(matchList).then(res => {
          if (res.code === 20000) {
            this.$message({
              message: 'Upload Success!',
              type: 'success'
            })
          } else {
            this.$message({
              message: res.message,
              type: 'error'
            })
          }
          this.excelLoading = false
          this.getList()
        })
      },
      handleDrop(e) {
        e.stopPropagation()
        e.preventDefault()
        if (this.excelLoading) return
        const files = e.dataTransfer.files
        if (files.length !== 1) {
          this.$message.error('Only support uploading one file!')
          return
        }
        const rawFile = files[0] // only use files[0]
        if (!this.isExcel(rawFile)) {
          this.$message.error(
            'Only supports upload .xlsx, .xls, .csv suffix files'
          )
          return false
        }
        this.upload(rawFile)
        e.stopPropagation()
        e.preventDefault()
      },
      handleDragover(e) {
        e.stopPropagation()
        e.preventDefault()
        e.dataTransfer.dropEffect = 'copy'
      },
      handleUpload() {
        this.$store.getters.user
        this.$refs['excel-upload-input'].click()
      },
      handleClick(e) {
        const files = e.target.files
        const rawFile = files[0] // only use files[0]
        if (!rawFile) return
        this.upload(rawFile)
      },
      upload(rawFile) {
        this.$refs['excel-upload-input'].value = null // fix can't select the same excel
        if (!this.beforeUpload) {
          this.readerData(rawFile)
          return
        }
        const before = this.beforeUpload(rawFile)
        if (before) {
          this.readerData(rawFile)
        }
      },
      readerData(rawFile) {
        this.excelLoading = true
        return new Promise((resolve, reject) => {
          const reader = new FileReader()
          reader.onload = e => {
            const data = e.target.result
            const workbook = XLSX.read(data, {type: 'array'})
            const firstSheetName = workbook.SheetNames[0]
            const worksheet = workbook.Sheets[firstSheetName]
            const header = this.getHeaderRow(worksheet)
            const results = XLSX.utils.sheet_to_json(worksheet)
            this.generateData({header, results})
            this.excelLoading = false
            resolve()
          }
          reader.readAsArrayBuffer(rawFile)
        })
      },
      getHeaderRow(sheet) {
        const headers = []
        const range = XLSX.utils.decode_range(sheet['!ref'])
        let C
        const R = range.s.r
        /* start in the first row */
        for (C = range.s.c; C <= range.e.c; ++C) {
          /* walk every column in the range */
          const cell = sheet[XLSX.utils.encode_cell({c: C, r: R})]
          /* find the cell in the first row */
          let hdr = 'UNKNOWN ' + C // <-- replace with your desired default
          if (cell && cell.t) hdr = XLSX.utils.format_cell(cell)
          headers.push(hdr)
        }
        return headers
      },
      isExcel(file) {
        return /\.(xlsx|xls|csv)$/.test(file.name)
      },
      radioChange() {
        if (this.radio === '2') {
          delete this.listQuery.is_game_over
        } else {
          this.listQuery.is_game_over = this.radio
        }
      },
      deleteAttr(row) {
        (this.matchStatus ? this.temp.ATTR : this.temp.VIP_ATTR).splice(row.index - 1, 1)
      },
      addAttr() {
        // 获取序号
        const _index = (this.matchStatus ? this.temp.ATTR : this.temp.VIP_ATTR).length + 1;
        (this.matchStatus ? this.temp.ATTR : this.temp.VIP_ATTR).push({
          index: _index
        })
      },
      getList() {
        this.listLoading = true
        getMatchList(this.listQuery).then(response => {
          this.listLoading = false
          this.list = response.items
          this.list.forEach(element => {
            element.settlementLoading = false
            element.cancelLoading = false

            element.HOST_TEAM_RESULT == '100'
              ? (element.HOST_TEAM_RESULT = '-')
              : ''
            element.GUEST_TEAM_RESULT == '100'
              ? (element.GUEST_TEAM_RESULT = '-')
              : ''
          })
          this.total = response.total
          // Just to simulate the time of the request
        })
      },
      getMatchDetail(data) {
        let _this = this
        _this.dialogLoading = true
        let para = {
          id:data.MATCH_ID
        }
        getMatchDetail(para).then(response => {
          _this.dialogLoading = false
          if(response.code ===20000){
            let row = response.items
            _this.temp = Object.assign({}, row) // copy obj
            _this.temp.MATCH_TIME = stringToDate(this.temp.MATCH_TIME)
            _this.temp.CLOSING_TIME = stringToDate(this.temp.CLOSING_TIME)

            // 子列表添加序号
            const _attr = _this.temp.ATTR
            for (var i = 0; i < _attr.length; i++) {
              const element = _attr[i]
              element.index = i + 1
            }
            const _bttr = _this.temp.VIP_ATTR
            for (var j = 0; j < _bttr.length; j++) {
              const element = _bttr[j]
              element.index = j + 1
            }
            _this.dialogStatus = 'update'
            _this.dialogFormVisible = true
            _this.$nextTick(() => {
              _this.$refs['dataForm'].clearValidate()
            })
          }
        })
      },
      handleFilter() {
        this.listQuery.page = 1
        this.getList()
      },
      handleModifyStatus(row, status) {
        this.$message({
          message: 'Success',
          type: 'success'
        })
        row.status = status
      },
      showSettlement(row) {
        this.temp = Object.assign({}, row) // copy obj

        this.temp.MATCH_TIME = stringToDate(this.temp.MATCH_TIME)
        this.temp.CLOSING_TIME = stringToDate(this.temp.CLOSING_TIME)

        if (this.temp.IS_GAME_OVER === '1') {
          this.$message({
            message: 'The game is settled',
            type: 'error'
          })
          return
        }

        if (this.temp.HOST_TEAM_RESULT && this.temp.GUEST_TEAM_RESULT) {
          this.settlementDialogs = true
        } else {
          this.$message({
            message: 'Please enter the score of this field first',
            type: 'error'
          })
        }
      },
      // 0 指的是用旧的结算 ， 1 指的是用新的结算算法
      handleSettlement(run_type) {
        var _this = this
        _this.temp.settlementLoading = false
        var para = {
          match_id: _this.temp.MATCH_ID,
          run_type:  run_type,
          // HOST_TEAM_RESULT: _this.temp.HOST_TEAM_RESULT,
          // GUEST_TEAM_RESULT: _this.temp.GUEST_TEAM_RESULT
        }

        const loading = this.$loading({
          lock: true,
          text: 'Loading',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        })

        setTimeout(() => {
          loading.close()
        }, 1.5 * 1000);
        // addMatchSettle(para).then(res => {
        settlementMatch(para).then(res => {
          loading.close()
          if (res.code === 20000) {
            _this.$message({
              message: 'Add settlement Success',
              type: 'success'
            })
            _this.list.forEach((ele, index) => {
              if (ele.MATCH_ID === _this.temp.MATCH_ID) {
                ele.STATUS = 1
              }
            })
            // _this.getList()
          } else {
            _this.$message({
              message: 'Add settlement Fail',
              type: 'fail'
            })
          }
          _this.temp.settlementLoading = true
          _this.settlementDialogs = false
        })
      },
      addSettle(row) {
        var _this = this
        if (row.IS_GAME_OVER === '1') {
          this.$message({
            message: 'The game is settled',
            type: 'error'
          })
          return
        }

        if (!(row.HOST_TEAM_RESULT && row.GUEST_TEAM_RESULT)) {
          this.$message({
            message: 'Please enter the score of this field first',
            type: 'error'
          })
          return;
        }
        var para = {
          match_id: row.MATCH_ID
        }
        const loading = this.$loading({
          lock: true,
          text: 'Loading',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        })
        setTimeout(() => {
          loading.close()
        }, 1.5 * 1000);
        addMatchSettle(para).then(res => {
          loading.close()
          if (res.code === 20000) {
            _this.$message({
              message: 'Add settle Success',
              type: 'success'
            })
            _this.getList()
          } else {
            _this.$message({
              message: 'Add settlement Fail',
              type: 'fail'
            })
          }
        })
      },
      reverseMatch(row,runType=0) {
        var _this = this
        var para = {
          match_id: row.MATCH_ID,
          run_type: runType
        }
        const loading = this.$loading({
          lock: true,
          text: 'Loading',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        })
        setTimeout(() => {
          loading.close()
        }, 1.5 * 1000);
        reverseMatchSettle(para).then(res => {
          loading.close()
          if (res.code === 20000) {
            _this.$message({
              message: 'Add reverse Success',
              type: 'success'
            })
            _this.getList()
          } else {
            _this.$message({
              message: 'Add reverse Fail',
              type: 'fail'
            })
          }
        })
      },
      resetTemp() {
        this.temp = {
          MATCH_ID: '',
          REMARK: '',
          MATCH_TIME: new Date(),
          MATCH_DESC: '',
          CLOSING_TIME: new Date(),
          CLOSING_STATE: null,
          HOST_TEAM: '',
          GUEST_TEAM: '',
          HOST_TEAM_RESULT: '',
          GUEST_TEAM_RESULT: '',
          ATTR: []
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
      cancelMatchHandle(runType=0) {
        var row = this.selectedMatch
        this.temp = Object.assign({}, row) // copy obj
        this.temp.MATCH_TIME = stringToDate(this.temp.MATCH_TIME)
        this.temp.CLOSING_TIME = stringToDate(this.temp.CLOSING_TIME)

        this.temp.cancelLoading = true

        var para = {
          match_id: this.temp.MATCH_ID,
          run_type: runType
        }

        if (this.temp.IS_GAME_OVER === '1') {
          this.$message({
            message: 'The game has ended and cannot be cancelled!',
            type: 'error'
          })
          return
        }

        cancelMatch(para).then(res => {
          if (res.code === 20000) {
            this.getList()
            this.$message({
              message: 'Cancel Success!',
              type: 'success'
            })
          } else {
            this.$message({
              message: 'Cancel Fail!',
              type: 'success'
            })
          }
          this.dialogCancelVisible = false
          this.temp.cancelLoading = false
        })
      },
      createData() {
        var _this = this
        this.$refs['dataForm'].validate(valid => {
          if (valid) {
            this.temp.id = parseInt(Math.random() * 100) + 1024 // mock a id
            this.temp.author = 'vue-element-admin'
          } else {
            return
          }
        })

        var mian_date = this.temp.MATCH_TIME - 5400 * 1000
        mian_date = new Date(mian_date)

        const para = {
          MATCH_DESC: this.temp.MATCH_DESC,
          MATCH_TIME: dateToString(this.temp.MATCH_TIME),
          CLOSING_TIME: dateToString(this.temp.CLOSING_TIME),
          MATCH_MD_TIME: dateToString(mian_date),
          CLOSING_STATE: this.temp.CLOSING_STATE,
          REMARK: this.temp.REMARK,
          HOST_TEAM: this.temp.HOST_TEAM,
          GUEST_TEAM: this.temp.GUEST_TEAM,
          HOST_TEAM_RESULT: this.temp.HOST_TEAM_RESULT,
          GUEST_TEAM_RESULT: this.temp.GUEST_TEAM_RESULT,
          ATTR: this.temp.ATTR,
          VIP_ATTR: this.temp.VIP_ATTR,
          IS_GAME_OVER: 0,
          HIDE: 0
        }

        this.dialogFormVisible = false
        addMatch(para).then(response => {
          if (response.code === 20000) {
            _this.$message({
              message: response.message,
              type: 'success'
            })
            _this.getList()
          }
        })
      },
      handleUpdate(row) {
        // this.getMatchDetail(row)
        let _this = this
        _this.temp = Object.assign({}, row) // copy obj
        _this.temp.MATCH_TIME = stringToDate(this.temp.MATCH_TIME)
        _this.temp.CLOSING_TIME = stringToDate(this.temp.CLOSING_TIME)

        this.temp.MATCH_TIME = stringToDate(this.temp.MATCH_TIME)
        this.temp.CLOSING_TIME = stringToDate(this.temp.CLOSING_TIME)

        // 子列表添加序号
        const _attr = _this.temp.ATTR
        for (var i = 0; i < _attr.length; i++) {
          const element = _attr[i]
          element.index = i + 1
        }
        const _bttr = _this.temp.VIP_ATTR
        for (var j = 0; j < _bttr.length; j++) {
          const element = _bttr[j]
          element.index = j + 1
        }
        _this.dialogStatus = 'update'
        _this.dialogFormVisible = true
        _this.$nextTick(() => {
          _this.$refs['dataForm'].clearValidate()
        })
        // this.temp.timestamp = new Date(this.temp.timestamp)
        //
        //
        // // 子列表添加序号
        // const _attr = this.temp.ATTR
        // for (var i = 0; i < _attr.length; i++) {
        //   const element = _attr[i]
        //   element.index = i + 1
        // }
        // const _bttr = this.temp.VIP_ATTR
        // for (var j = 0; j < _bttr.length; j++) {
        //   const element = _bttr[j]
        //   element.index = j + 1
        // }
      },
      updateData() {
        var _this = this

        const para = {
          MATCH_ID: this.temp.MATCH_ID,
          MATCH_DESC: this.temp.MATCH_DESC,
          MATCH_TIME: dateToString(this.temp.MATCH_TIME),
          MATCH_MD_TIME: dateToString(this.temp.MATCH_TIME - 5400 * 1000),
          CLOSING_TIME: dateToString(this.temp.CLOSING_TIME),
          CLOSING_STATE: this.temp.CLOSING_STATE,
          REMARK: this.temp.REMARK,
          HOST_TEAM: this.temp.HOST_TEAM,
          GUEST_TEAM: this.temp.GUEST_TEAM,
          HOST_TEAM_RESULT: this.temp.HOST_TEAM_RESULT,
          GUEST_TEAM_RESULT: this.temp.GUEST_TEAM_RESULT,
          ATTR: this.temp.ATTR,
          VIP_ATTR: this.temp.VIP_ATTR,
          hide: this.temp.hide,
          exception: this.temp.exception,
        }

        // 删除这两个字段
        para.ATTR.forEach(element => {
          delete element.CREATE_TIME
          delete element.UPDATE_TIME
        })

        editMatch(para).then(response => {
          if (response.code === 20000) {
            _this.$message({
              message: response.message,
              type: 'success'
            })
            _this.getList()
          }
        })
      },
      deleteMatch: function () {
        this.dialogPvVisible = false
        setTimeout(() => {
          this.listLoading = false
        }, 1.5 * 1000)
        delMatch({match_id: this.selectedMatch.MATCH_ID}).then(response => {
          this.listLoading = false
        })
        this.$notify({
          title: 'Success',
          message: 'Delete Successfully',
          type: 'success',
          duration: 2000
        })
        const index = this.list.indexOf(this.selectedMatch)
        this.list.splice(index, 1)
      },
      handleDelete(row) {
        this.dialogPvVisible = true
        this.selectedMatch = row
      },
      handleFetchPv(pv) {
      },
      handleDownload() {
        this.downloadLoading = true
        import('@/vendor/Export2Excel').then(excel => {
          const tHeader = ['timestamp', 'title', 'type', 'importance', 'status']
          const filterVal = [
            'timestamp',
            'title',
            'type',
            'importance',
            'status'
          ]
          const data = this.formatJson(filterVal, this.list)
          excel.export_json_to_excel({
            header: tHeader,
            data,
            filename: 'table-list'
          })
          this.downloadLoading = false
        })
      },
      formatJson(filterVal, jsonData) {
        return jsonData.map(v =>
          filterVal.map(j => {
            if (j === 'timestamp') {
              return parseTime(v[j])
            } else {
              return v[j]
            }
          })
        )
      },
      tableFormat(row, column, index) {
        // console.log(row, column, index)
        let str = ''
        switch (column.property) {
          default:
            str = number_format(row[column.property])
            break
        }
        return str
      },
	GetMatchHideWarning() {
        let _this = this
        getMatchHideWarning({}).then(response => {
          let items = response.items
          if (response.code == 20000 && items.length > 0) {
            _this.HideMatchList = items
            _this.HideMatchList.forEach(element => {
              element.settlementLoading = false
              element.cancelLoading = false

              element.HOST_TEAM_RESULT === '100'
                ? (element.HOST_TEAM_RESULT = '-')
                : ''
              element.GUEST_TEAM_RESULT === '100'
                ? (element.GUEST_TEAM_RESULT = '-')
                : ''
            })
            // _this.dialogVisible = true;
          }

        })
      },
      HideConfirm(HideList) {
        let _this = this
        let ids = []
        let hide_states = []
        HideList.forEach((match) => {
          ids.push(match.MATCH_ID)
          hide_states.push(match.hide)
        })
        let para = {}
        para.match_ids = ids.join(',')
        para.hide_state = hide_states.join(',')
        console.log(para)
        setMatchHideState(para).then(response => {
          if (response.code === 20000) {
            _this.$message({
              message: response.message,
              type: 'success'
            })
            _this.GetMatchHideWarning()
          }
        })
      },
      showHideList() {
        this.dialogVisible = true
      },
      hide_format(hide) {
        let label = ['Show', 'Hide'];
        return label[hide] || 'Unknown'; // 防止越界，默认返回 'Unknown'
      },
    }
  }
</script>
<style>
  .row-red {
    color: red;
  }

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
  .el-table .danger-row {
    background: #ffb2b2;
  }
  .el-table .warning-row {
    background: #fdf1b1;
  }

  .sublist {
    display: flex;
    align-items: center;
  }
</style>
