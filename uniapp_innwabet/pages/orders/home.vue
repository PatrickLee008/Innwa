<template name="orders">
	<view class="mybg-grey ">
		<!--  #ifdef APP-PLUS-->
		<cu-custom isBack backUrl="/pages/index/index">
			<block slot="content">{{language.myBet}}
			</block>
		</cu-custom>
		<!-- #endif-->
		<!--  #ifdef  H5 -->
		<cu-custom isBack backUrl="/pages/index/index">
			<block slot="content">{{language.myBet}}
			</block>
		</cu-custom>
		<!-- #endif-->
		
		<view class="flex flex-wrap grey">
			<view class="flex-row myfont-bold" style="justify-content: space-around;">
				<view class="basis-df" style="height: 35px;line-height: 35px;width: 50%;" :class="activeTab==0?'mycolor-red under-line':''" @click="handleTabChange(0)">{{language.unorderd}}</view>
				<view class="basis-df" style="height: 35px;line-height: 35px;width: 50%;" :class="activeTab==1?'mycolor-red under-line':''" @click="handleTabChange(1)">{{language.completed}}</view>
			</view>
		</view>

		<scroll-view scroll-y v-if="activeTab==0" style="padding-bottom: 80px;height: 90vh;">
			<view class="cu-list menu-avatar" v-for="order in unordered" @click="showOrderDetails(order,0)">
				<view class="myrect box-shadow flex-column bg-white" style="width: 96vw;justify-content: flex-start;margin: 1vw 2vw 1vw 2vw;">
					<view class="flex-column">
						<view class="flex-row myfont-bold content-row" style="width: 90%;">
							<text class="team-name" :class="{'mycolor-red':order.LOSE_TEAM == '1'}">{{order.HOME}}</text>
							<text class="margin-left-sm margin-right-sm text-bold mycolor-red">VS</text>
							<text class="team-name" :class="{'mycolor-red':order.LOSE_TEAM == '2'}">
								{{order.AWAY}}</text>
							<!-- <image v-if="order.IS_MIX=='1'" class="mix_icon" src="../../static/icon/M.png"></image> -->

							<view class="text-grey text-xs">{{order.CREATE_TIME}}</view>
						</view>

						<view class="content-row2 flex-row content-row myrect mybg-grey" style="width: 95%;">
							<!-- <text class="cuIcon-infofill text-red  margin-right-xs"></text> -->
							<text>{{order.ORDER_TYPE}}</text> <text space="nbsp"> {{order.ODDS_DESC}}</text>
							<text class="" space="nbsp">{{order.BET_CONTENT}}</text>
							<text style="vertical-align:baseline;height:16px;line-height: 16px;margin-left: 5px;" class="cu-tag radius bgp-colr sm">{{numberFormat(order.BET_MONEY)}}</text>
							<text v-if="order.IS_MIX=='1'" style="vertical-align:baseline;height:16px;line-height: 16px;" class="cu-tag radius bglg-colg sm">{{calParlay(order)}}</text>
						</view>
					</view>
				</view>
			</view>
			<uni-load-more :status="status" :content-text="ContentText" @clickLoadMore="clickLoadMore('unordered')" />
		</scroll-view>

		<scroll-view scroll-y class="page" v-if="activeTab==1" style="padding-bottom: 80px;height: 90vh;">
			<view class="cu-list menu-avatar" v-for="order in completed" @click="showOrderDetails(order,1)">
				<view class="myrect box-shadow flex-column bg-white" style="width: 96vw;justify-content: flex-start;margin: 1vw 2vw 1vw 2vw;">
					<view class="flex-column">
						<view class="flex-row myfont-bold content-row" style="width: 90%;">
							<text class="team-name" :class="{'mycolor-red':order.LOSE_TEAM == '1'}">{{order.HOME}}</text>
							<text class="cu-tag radius bgp-colr sm" style="font-size: 14px;">{{order.RESULT}}</text>
							<text class="team-name" :class="{'mycolor-red':order.LOSE_TEAM == '2'}">
								{{order.AWAY}}</text>
							<!-- <image v-if="order.IS_MIX=='1'" class="mix_icon" src="../../static/icon/M.png"></image> -->

							<view class="text-grey text-xs">{{order.CREATE_TIME}}</view>
						</view>

						<view class="content-row2 flex-row content-row myrect mybg-grey" style="width: 95%;justify-content: space-between;">
							<view>
								<!-- <text class="cuIcon-infofill text-red  margin-right-xs"></text> -->
								<text>{{order.ORDER_TYPE}}</text> <text space="nbsp"> {{order.ODDS_DESC}}</text>
								<text class="" space="nbsp">{{order.BET_CONTENT}}</text>
								<text style="vertical-align:baseline;height:16px;line-height: 16px;margin-left: 5px;" class="cu-tag radius bgp-colr sm">{{numberFormat(order.BET_MONEY)}}</text>
								<text v-if="order.IS_MIX=='1'" style="vertical-align:baseline;height:16px;line-height: 16px;" class="cu-tag radius bglg-colg sm">
									{{calParlay(order)}}
								</text>
							</view>

							<view v-if="order.IS_WIN=='2'">
								<!-- <view v-if="order.IS_WIN=='0'" class="mycolor-red myfont-bold">Lose</view> -->
								<view v-if="numberFormat(order.BONUS - order.BET_MONEY)>0" class="text-blue myfont-bold">+{{numberFormat(order.BONUS) }}</view>
								<view class="mycolor-orange myfont-bold">Waiting</view>
							</view>
							<view v-else>
								<!-- <view v-if="order.IS_WIN=='0'" class="mycolor-red myfont-bold">Lose</view> -->
								<!-- 奖金为0的情况，直接显示LOSE -->
								<view v-if="order.BONUS == 0" class="mycolor-red myfont-bold">Lose</view>
								
								<!-- 奖金大于0但是小于本金的情况下， 显示红色返回金额 -->
								<view v-if="order.BONUS - order.BET_MONEY>0" class="text-blue myfont-bold">+{{numberFormat(order.BONUS) }}</view>
								<view v-if="order.BONUS >0 && order.BONUS - order.BET_MONEY<0" class="mycolor-red myfont-bold">+{{numberFormat(order.BONUS) }}</view>
							</view>
						</view>
					</view>
				</view>
			</view>
			<uni-load-more :status="status" :content-text="ContentText" @clickLoadMore="clickLoadMore('completed')" />

		</scroll-view>
		<!-- <view class="amount-bar " style="background-color: rgb(81, 81, 81);display: flex;flex-direction: row;justify-content: space-between;align-items: center;"> -->
		<view class="amount-bar flex flex-wrap justify-center">
			<view class="basis-df">
				<button style="width: 80%;margin: 0 10% 0 10%;border-radius: 10px;" @tap='popupOpen(1)' class="mybg-orange">{{language.bet_time}}</button>
			</view>
			<view class="basis-df ">
				<button style="width: 80%;margin: 0 10% 0 10%;border-radius: 10px;" @tap='popupOpen(2)' class="mybg-red">{{language.bettype}}</button>
			</view>
		</view>
		<!-- </view> -->

		<uni-popup ref="popup" type="center">
			<view>
				<view class="text-center mybg-red text-bold" style="height:30px;line-height: 46px;border-bottom:1px solid #80808052;border-radius: 13px 13px 0 0 ;height: 46px;">{{language.detail}}</view>
				<scroll-view scroll-y class="order mybg-grey">
					<view class="cu-list border-bottom menu-avatar" v-for="(order,index) in  orderDetails.orders">

						<view class="myrect box-shadow flex-column bg-white" style="width: 96%;justify-content: flex-start;margin: 1vw 2vw 1vw 2vw;">
							<view class="flex-column">
								<view class="flex-row myfont-bold content-row" style="width: 90%;">
									<text class="team-name" :class="{'mycolor-red':order.LOSE_TEAM == '1'}">{{order.HOME}}</text>
									<text class="cu-tag radius bgp-colr sm" style="font-size: 14px;">{{order.RESULT ?order.RESULT:'VS'}}</text>
									<text class="team-name" :class="{'mycolor-red':order.LOSE_TEAM == '2'}">
										{{order.AWAY}}</text>
									<!-- <image v-if="order.IS_MIX=='1'" class="mix_icon" src="../../static/icon/M.png"></image> -->

									<view class="text-grey text-xs">{{order.CREATE_TIME}}</view>
								</view>

								<view class="content-row2 flex-row content-row myrect mybg-grey" style="width: 95%;">
									<!-- <text class="cuIcon-infofill text-red  margin-right-xs"></text> -->
									<text>{{order.ORDER_TYPE}}</text> <text space="nbsp"> {{order.ODDS_DESC}}</text>
									<text class="" space="nbsp">{{order.BET_CONTENT}}</text>
									<text style="vertical-align:baseline;height:16px;line-height: 16px;margin-left: 5px;" class="cu-tag radius bgp-colr sm">{{numberFormat(order.BET_MONEY)}}</text>
									<!-- <text v-if="order.IS_MIX=='1'" style="vertical-align:baseline;height:16px;line-height: 16px;" class="cu-tag radius bglg-colg sm">{{order.REMARK}}</text> -->
								</view>
							</view>
						</view>
					</view>
				</scroll-view>

				<view class="flex flex-wrap grey">
					<view class="basis-sm  text-bold basis-df text-center">{{language.type}}</view>
					<view v-if="orderDetails.detail.IS_MIX=='1'" class="basis-xs basis-df text-center">{{language.mixed}}</view>
					<view v-if="orderDetails.detail.IS_MIX=='0'" class="basis-xs basis-df text-center">{{language.single}}</view>
				</view>

				<view class="flex flex-wrap bg-white">
					<view class="basis-sm text-bold basis-df text-center">{{language.amount}}</view>
					<view class="basis-xs basis-df text-center">{{numberFormat(orderDetails.detail.BET_MONEY) }}</view>
				</view>

				<view class="flex flex-wrap grey">
					<view v-if="orderDetails.detail.STATUS=='1'" class="basis-sm  text-bold basis-df text-center">{{language.benefitMax}}</view>
					<view v-if="orderDetails.detail.STATUS=='0'" class="basis-sm  text-bold basis-df text-center">Bonus</view>
					<view v-if="orderDetails.detail.STATUS=='1'" class="basis-xs  basis-df text-center">{{numberFormat(orderDetails.benefit)}}</view>
					<view v-if="orderDetails.detail.STATUS=='0'" class="basis-xs text-red text-bold basis-df text-center">{{ numberFormat(orderDetails.detail.BONUS)}}</view>
				</view>

				<view class="mybg-pink text-center flex-column" style="border-radius: 0 0  13px 13px ;height: 46px;">
					<button class="cu-btn mybg-red" style="width: 20%;" @click="$refs.popup.close()">confirm</button>
				</view>
			</view>
		</uni-popup>

		<uni-popup ref="popup1" type="bottom">
			<view style="height: 100px;width: 100%;background-color: white;">
				<view style="width: 96%;height: 30px;line-height: 30px;margin: 2%;" class="text-center border-bottom">{{language.bet_time}}</view>
				<view class="flex flex-wrap" style="justify-content: space-around;">
					<button class="cu-btn" :class="listQuery.time==0?'mybg-red':''" @click="buttonPress(1,0)">{{language.all}}</button>
					<button class="cu-btn" :class="listQuery.time==1?'mybg-red':''" @click="buttonPress(1,1)">{{language.one_week}}</button>
					<button class="cu-btn" :class="listQuery.time==2?'mybg-red':''" @click="buttonPress(1,2)">{{language.one_month}}</button>
				</view>
			</view>
		</uni-popup>

		<uni-popup ref="popup2" type="bottom">
			<view class="text-center" style="height: 100px;width: 100vw;background-color: white;">
				<view style="width: 96%;height: 30px;line-height: 30px;margin: 2%;" class="border-bottom">{{language.bettype}}</view>
				<view class="flex flex-wrap" style="justify-content: space-around;">
					<button class="cu-btn" :class="listQuery.type==0?'mybg-red':''" @click="buttonPress(2,0)">{{language.all}}</button>
					<button class="cu-btn" :class="listQuery.type==1?'mybg-red':''" @click="buttonPress(2,1)">{{language.single_bet}}</button>
					<button class="cu-btn" :class="listQuery.type==2?'mybg-red':''" @click="buttonPress(2,2)">{{language.mix_bet}}</button>
					<!-- <button class="cu-btn" :class="listQuery.type==3?'mybg-red':''" @click="buttonPress(2,3)">{{language.correctScore}}</button> -->
				</view>
			</view>
		</uni-popup>
	</view>
</template>

<script>
	import Vue from 'vue';
	import sTabs from '@/components/s-tabs/index.vue';
	import sTab from '@/components/s-tab/index.vue';
	import config from '../../utils/config.js';
	import uniPopup from "@/components/uni-popup/uni-popup.vue";
	import uniLoadMore from "@/components/uni-load-more/uni-load-more.vue";
	import dateFormatUtils from "../../utils/utils.js";
	import DatePicker from '../component/date-picker';


	export default {
		name: 'orders',
		components: {
			sTabs,
			sTab,
			uniLoadMore,
			uniPopup,
			DatePicker
		},
		data() {
			return {
				bet_type: {
					'MIX_BODY': '4',
					'MIX_GOAL': '5',
					'MIX_EVEN': '7',
					'MIX_WDL': '11',
					'SINGLE_BODY': '1',
					'SINGLE_GOAL': '2',
					'SINGLE_EVEN': '6',
					'SINGLE_WDL': '10',
				},
				listQuery: {
					date: '',
					time: 0,
					type: 0,
					is_mix: '',
				},
				items: [{
						value: '1',
						name: config.language.single
					},
					{
						value: '2',
						name: config.language.mixed,
						checked: 'true'
					}
				],
				current: 0,
				list_end: false,
				unordered: [],
				completed: [],
				tabList: [1, 2],
				activeTab: 1,
				unorderedCurrentPage: 1,
				completedCurrentPage: 1,
				orderDetails: {
					detail: {},
					benefit: 0,
					orders: []
				},
				limit: 100,
				status:'more',
				ContentText: {
					contentdown: 'more',
					contentrefresh: 'loading',
					contentnomore: 'no more'
				},
				language: config.language
			};
		},
		methods: {
			toHome() {
				uni.reLaunch({
					url: '/pages/index/index'
				})
			},
			calParlay(betContent) {
				let a = ''
				if (this.language.lang == 'myan') {
					a = betContent.REMARK.slice(0, betContent.REMARK.indexOf('x')) + this.language.parlay
				} else {
					a = this.language.parlay + betContent.REMARK
				}
				return a
			},
			getCurrentDate(n) {
				var dd = new Date();
				if (n) {
					dd.setDate(dd.getDate() - n);
				}
				var year = dd.getFullYear();
				var month =
					dd.getMonth() + 1 < 10 ? "0" + (dd.getMonth() + 1) : dd.getMonth() + 1;
				var day = dd.getDate() < 10 ? "0" + dd.getDate() : dd.getDate();
				return year + "-" + month + "-" + day;
			},
			popupOpen(typ) {
				typ == 1 ? this.$refs.popup1.open() : this.$refs.popup2.open()
			},
			buttonPress(typ, val) {
				// console.log('type val',typ,val)
				this.unordered = []
				this.completed = []
				typ == 1 ? Vue.set(this.listQuery, 'time', val) : Vue.set(this.listQuery, 'type', val)
				typ == 1 ? this.$refs.popup1.close() : this.$refs.popup2.close()
				this.activeTab == 0 ? this.getUnorderedList() : this.getCompletedList();
			},
			numberFormat(num) {
				return dateFormatUtils.numFormat(num)
			},
			handleTabChange(typ) {
				switch (typ) {
					case 0:
						this.activeTab = 0
						break
					case 1:
						this.activeTab = 1
						break
				}
				this.reset_list()
				this.get_tab_list()
			},
			reset_list(){
				this.list_end = false
				this.unordered = [];
				this.unorderedCurrentPage = 1;
				this.completed = [];
				this.completedCurrentPage = 1;
			},
			get_tab_list(){
				if (this.activeTab == 0) {
					this.getUnorderedList();
				} else {
					this.getCompletedList();
				}
			},
			DateChange(filter) {
				this.listQuery.start_time = filter.start_time.substring(0, 10);
				this.listQuery.end_time = filter.start_time.substring(0, 10);
				this.reset_list()
				this.get_tab_list()
			},
			radioChange: function(evt) {
				for (let i = 0; i < this.items.length; i++) {
					if (this.items[i].value === evt.target.value) {
						this.current = i;
						break;
					}
				}
				this.current == 0 ? this.listQuery.is_mix = 0 : this.listQuery.is_mix = 1
				this.reset_list()
				this.get_tab_list()
			},
			clickLoadMore(type) {
				if(this.list_end){
					return
				}
				if (type == 'completed') {
					this.completedCurrentPage++;
				} else {
					this.unorderedCurrentPage++;
				}
				this.get_tab_list()
			},
			getUnorderedList() {
				var _this = this;
				var paras = {
					page: _this.unorderedCurrentPage,
					limit: _this.limit,
					status: 1,
					game_type:1,
					start_time: _this.listQuery.time == 0 ? '' : _this.listQuery.time == 1 ? _this.getCurrentDate(7) : _this.getCurrentDate(
						30),
					end_time: _this.listQuery.time == 0 ? '' : _this.getCurrentDate(0),
					order_type: _this.listQuery.type == 3 ? 3 : '',
					is_mix: _this.listQuery.type == 2 ? 1 : _this.listQuery.type == 0 ? '' : 0
				};
				uni.showLoading({
					title: 'Loading!'
				})
				_this.$http.get("/order/get", {
					data: paras
				}, (res) => {
					uni.hideLoading()
					if (res.data.code == 20000) {
						var results = res.data.items;
						results.forEach(ele => {

							var temp = ele.ORDER_DESC.split('||');
							ele.HOME = temp[0];
							ele.AWAY = temp[1];

							if (ele.ORDER_TYPE != '7' && ele.ORDER_TYPE != '6') {
								ele.DRAW_BUNKO = ele.DRAW_BUNKO == '0' ? '+' : '-';
								ele.ODDS_DESC = '   (' + ele.LOSE_BALL_NUM + ele.DRAW_BUNKO + ele.DRAW_ODDS + ')' //(2-50)
							} else {
								ele.ODDS_DESC = '  ' + ele.BET_ODDS;
							}
							ele.CREATE_TIME = ele.CREATE_TIME.substring(5, ele.CREATE_TIME.length);

							if (ele.ORDER_TYPE == "1" || ele.ORDER_TYPE == "4") { //上下盘
								ele.ORDER_TYPE = _this.language.body
								ele.BET_CONTENT = ele.BET_TYPE == '1' ? '   ' + ele.HOME : '   ' + ele.AWAY;
							} else if (ele.ORDER_TYPE == "2" || ele.ORDER_TYPE == "5") { //大小盘
								ele.ORDER_TYPE = _this.language.goal
								ele.BET_CONTENT = ele.BALL_TYPE == '1' ? '   ' + _this.language.over : '   ' + _this.language.under;
							} else if (ele.ORDER_TYPE == "6" || ele.ORDER_TYPE == "7") { //大小盘
								ele.ORDER_TYPE = _this.language.odd_even
								ele.BET_CONTENT = ele.BET_TYPE == '1' ? '   ' + _this.language.odd : '   ' + _this.language.even;
							} else if (ele.ORDER_TYPE == "10" || ele.ORDER_TYPE == "11") { //胜平负盘
								ele.ORDER_TYPE = '1X2'
								ele.BET_CONTENT = '   ' + (ele.BET_TYPE == '3' ? 'DRAW' : ele.BET_TYPE == '1' ? 'HOME WIN' : 'AWAY WIN') + '@' + ele.BET_ODDS
								ele.ODDS_DESC =  '';
							}

							ele.REMARK = ele.REMARK.replace('串', 'x')

							_this.unordered.push(ele);
						})

						if (results.length == 0) {
							_this.list_end = true
							_this.status = 'noMore'
						} else {
							_this.status = 'more'
						}
					}
				})
			},
			getCompletedList() {
				var _this = this;
				uni.showLoading({
					title: 'Loading!'
				})
				var paras = {
					page: _this.completedCurrentPage,
					limit: _this.limit,
					status: 0,
					game_type:1,
					start_time: _this.listQuery.time == 0 ? '' : _this.listQuery.time == 1 ? _this.getCurrentDate(7) : _this.getCurrentDate(
						30),
					end_time: _this.listQuery.time == 0 ? '' : _this.getCurrentDate(0),
					order_type: _this.listQuery.type == 3 ? 3 : '',
					is_mix: _this.listQuery.type == 2 ? 1 : _this.listQuery.type == 0 ? '' : 0,
				};
				_this.$http.get("/order/get_history", {
					data: paras
				}, (res) => {
					uni.hideLoading()
					if (res.data.code == 20000) {
						var results = res.data.items;
						results.forEach(ele => {
							//ele.ORDER_DESC = ele.ORDER_DESC.replace('||', 'VS')
							var temp = ele.ORDER_DESC.split('||');
							ele.HOME = temp[0];
							ele.AWAY = temp[1];

							//已经出结果的赛事 , 直接显示比分 ,
							ele.RESULT = ele.BET_HOST_TEAM_RESULT + '-' + ele.BET_GUEST_TEAM_RESULT;

							if (ele.BET_HOST_TEAM_RESULT == '100') {
								ele.RESULT = '--';
							}

							//大小盘和上下盘,显示盘口如:  2-50
							if (ele.ORDER_TYPE != '7' && ele.ORDER_TYPE != '6') {
								ele.DRAW_BUNKO = ele.DRAW_BUNKO == '0' ? '+' : '-';
								ele.ODDS_DESC = '   (' + ele.LOSE_BALL_NUM + ele.DRAW_BUNKO + ele.DRAW_ODDS + ')' //(2-50)
							}
							//单双盘 , 直接显示赔率 , 如 0.98
							else {
								ele.ODDS_DESC = '  ' + ele.BET_ODDS;
							}

							ele.CREATE_TIME = ele.CREATE_TIME.substring(5, ele.CREATE_TIME.length);

							if (ele.ORDER_TYPE == "1" || ele.ORDER_TYPE == "4") { //上下盘
								ele.ORDER_TYPE = _this.language.body
								ele.BET_CONTENT = ele.BET_TYPE == '1' ? '   ' + ele.HOME : '   ' + ele.AWAY;
							} else if (ele.ORDER_TYPE == "2" || ele.ORDER_TYPE == "5") { //大小盘
								ele.ORDER_TYPE = _this.language.goal
								ele.BET_CONTENT = ele.BALL_TYPE == '1' ? '   ' + _this.language.over : '   ' + _this.language.under;
							} else if (ele.ORDER_TYPE == "6" || ele.ORDER_TYPE == "7") { //单双盘
								ele.ORDER_TYPE = _this.language.odd_even
								ele.BET_CONTENT = ele.BET_TYPE == '1' ? '   ' + _this.language.odd : '   ' + _this.language.even;
							} else if (ele.ORDER_TYPE == "10" || ele.ORDER_TYPE == "11") { //胜平负盘
								ele.ORDER_TYPE = '1X2'
								ele.BET_CONTENT = '   ' + (ele.BET_TYPE == '3' ? 'DRAW' : ele.BET_TYPE == '1' ? 'HOME WIN' : 'AWAY WIN') + '@' + ele.BET_ODDS
								ele.ODDS_DESC =  '';
							}

							ele.REMARK = ele.REMARK.replace('串', 'x')
							_this.completed.push(ele);
						})

						if (results.length == 0) {
							_this.list_end = true
							_this.status = 'noMore'
						} else {
							_this.status = 'more'
						}
					}
				})
			},
			showOrderDetails(row, type) {
				if (row.IS_MIX != '1') return;
				var url = type == 0 ? '/order/get' : '/order/get_history';
				this.orderDetails.detail = Object.assign({}, row);

				var _this = this;

				var paras = {
					order_id: row.ORDER_ID.replace(/\s*/g, ""),
					is_detail: true
				};
				_this.orderDetails.orders = []
				_this.$http.get(url, {
					data: paras
				}, (res) => {
					if (res.data.code == 20000) {
						_this.orderDetails.orders = res.data.items;
						_this.orderDetails.orders.forEach(ele => {

							if (ele.ORDER_DESC.indexOf('||') > -1) {
								//ele.ORDER_DESC = ele.ORDER_DESC.replace('||', 'VS')
								var temp = ele.ORDER_DESC.split('||');
								ele.HOME = temp[0] + ' ';
								ele.AWAY = ' ' + temp[1];
							}

							if (ele.BET_HOST_TEAM_RESULT != null && ele.BET_GUEST_TEAM_RESULT != null) {
								ele.RESULT = ele.BET_HOST_TEAM_RESULT + '-' + ele.BET_GUEST_TEAM_RESULT;
							}

							if (ele.BET_HOST_TEAM_RESULT == '100') {
								ele.RESULT = '--';
							}

							//大小盘和上下盘,显示盘口如:  2-50
							if (ele.ORDER_TYPE != '7' && ele.ORDER_TYPE != '6') {
								ele.DRAW_BUNKO = ele.DRAW_BUNKO == '0' ? '+' : '-';
								ele.ODDS_DESC = '   (' + ele.LOSE_BALL_NUM + ele.DRAW_BUNKO + ele.DRAW_ODDS + ')' //(2-50)
							}
							//单双盘 , 直接显示赔率 , 如 0.98
							else {
								ele.ODDS_DESC = '  ' + ele.BET_ODDS;
							}
							ele.CREATE_TIME = ele.CREATE_TIME.substring(5, ele.CREATE_TIME.length);

							if (ele.ORDER_TYPE == "1" || ele.ORDER_TYPE == "4") { //上下盘
								ele.ORDER_TYPE = _this.language.body
								ele.BET_CONTENT = ele.BET_TYPE == '1' ? '   ' + ele.HOME : '   ' + ele.AWAY;
							} else if (ele.ORDER_TYPE == "2" || ele.ORDER_TYPE == "5") { //大小盘
								ele.ORDER_TYPE = _this.language.goal
								ele.BET_CONTENT = ele.BALL_TYPE == '1' ? '   ' + _this.language.over : '   ' + _this.language.under;
							} else if (ele.ORDER_TYPE == "6" || ele.ORDER_TYPE == "7") { //单双盘
								ele.ORDER_TYPE = _this.language.odd_even
								ele.BET_CONTENT = ele.BET_TYPE == '1' ? '   ' + _this.language.odd : '   ' + _this.language.even;
							} else if (ele.ORDER_TYPE == "10" || ele.ORDER_TYPE == "11") { //胜平负盘
								ele.ORDER_TYPE = '1X2'
								ele.BET_CONTENT = '1X2'
							}

							ele.MATCH_TIME = ele.MATCH_TIME.substring(5, 16);

							_this.orderDetails.benefit = this.orderDetails.detail.BET_MONEY * Math.pow(2, this.orderDetails.orders.length)
						})
					}
				})

				this.$refs.popup.open()
			}
		},
		created() {
			this.listQuery.date = dateFormatUtils.formatDate(new Date().getTime(), 'Y-M-D');

			// this.listQuery.start_time = this.listQuery.date;
			// this.listQuery.end_time = this.listQuery.date;

			this.activeTab == 0 ? this.getUnorderedList() : this.getCompletedList();
		}
	}
</script>

<style>
	.bar-row {
		width: 90vw;
		margin-top: 10px;
		justify-content: space-between;
	}

	.bar-icon {
		width: 14px;
		height: 15px;
		margin-right: 5px;

	}

	.bar-icon-image {
		width: 100%;
		height: 100%;
	}


	.content-row {
		justify-content: space-between;
		width: 90vw;
	}

	.content-row2 {
		padding: 0 10px 0 10px;
		margin: 5px 0 15px 0;
		line-height: 45px;
		justify-content: flex-start;
		/* font-weight: 550; */
	}

	.content-row view {
		line-height: 30px;
		padding: 5px 0 5px 0;
	}

	.content-row view:first-child {}

	.content-row view:nth-child(2) {}

	.page {
		width: 100vw;
	}

	.team-name {
		text-align: center;
		width: 90px;
		word-wrap: break-word;
		word-break: break-all;
	}

	.page.show {
		overflow: hidden;
	}

	.text-center {
		height: 32px;
		line-height: 32px;
	}

	.order {
		height: 55vh;
	}

	.switch-sex::after {
		content: "\e716";
	}

	.switch-sex::before {
		content: "\e7a9";
	}

	.switch-music::after {
		content: "\e66a";
	}

	.switch-music::before {
		content: "\e6db";
	}

	.bg-green {
		background-color: rgb(41, 150, 56);
		padding: 0 5px;
	}

	.cu-list {
		margin-top: 0;
	}

	.content {
		left: 12px !important
	}

	.grey {
		background-color: #F2F2F2;
		color: #666666;
	}

	.mix_icon {
		width: 13px;
		height: 13px;
		margin-left: 12px;
	}

	.content {
		width: calc(100% - 30px - 60px - 10px) !important;
	}

	.active-tab {
		background-color: red;
		color: white;
	}

	.unactive-tab {
		color: white;
		background-color: #555555;
	}

	.amount-bar {
		height: 50px;
		position: fixed;
		width: 100%;
		bottom: 30px;
		color: white;
	}

	.Tabs-Page {
		.article {
			&:not(:first-child) {
				margin-top: 40rpx;
			}

			.title {
				padding: 20rpx;
				font-size: 28rpx;
				text-align: center;
			}

			.desc {
				padding: 0 40rpx;
				font-size: 26rpx;
			}
		}

		/deep/.s-tabs {
			.s-tab-panel {
				padding: 30rpx;
			}
		}

		.custom-tabs {
			/deep/.s-tab-nav-view {
				display: flex;
				justify-content: center;

				.s-tab-nav {
					&:not(:first-child) {
						margin-left: 40rpx;
					}
				}
			}
		}
	}
</style>
