<template>
	<view class="mybg-grey full-page">
		<cu-custom isBack backUrl="/pages/index/index">
			<block slot="content">{{language.single}}
			</block>
			<block slot="right">
				<view style="width: 30vw;" @tap="showModal" class="padding-xs" data-target="Modal">
					<image style="width:25px;height: 25px;float: right;margin-right: 10px;" :style="filterScale"
						src="../../static/image/shaixuan.png"></image>
				</view>
			</block>
		</cu-custom>

		<view class="cu-modal drawer-modal justify-start" :class="modalName=='Modal'?'show':''" @tap="hideModal">
			<view class="cu-dialog basis-lg">

				<!--  #ifdef  APP-PLUS -->
				<scroll-view scroll-y @tap.stop="" style="margin-top: 50px;"
					:style="[{top:CustomBar+'px',height:'calc(100vh - 50px - ' + CustomBar + 'px)'}]">
					<!--  #endif -->
					<!--  #ifdef  H5 -->
					<scroll-view scroll-y @tap.stop="" style="margin-top: 50px;height:80vh"
						:style="[{top:CustomBar+'px'}]">
						<!--  #endif -->

						<view class="cu-list menu text-left">

							<view class="league-row">
								<image v-show="allStatus" src="../../static/icon/checked.png" @click="selectAll">
								</image>
								<image v-show="!allStatus" src="../../static/icon/unchecked.png" @click="selectAll">
								</image>
								<text class="margin-left-sm" style="width: 160px;">
									All
								</text>
							</view>
							<view class="league-row" @tap="ChooseCheckbox" :data-value="item.name"
								v-for="(item,index) in leagueObjs" :key="index">

								<image v-show="item.checked" src="../../static/icon/checked.png"></image>
								<image v-show="!item.checked" src="../../static/icon/unchecked.png"></image>

								<text class="margin-left-sm" style="width: 160px;">
									{{item.name}}
								</text>
							</view>

						</view>
					</scroll-view>
					<view class="padding-sm flex flex-direction">
						<button class="cu-btn mybg-red lh" @click="setLeagueFilter"> Ok </button>
					</view>
			</view>
		</view>

		<!-- <scroll-view scroll-y class="page" style="height:calc(100vh - 123px);" @scrolltolower="clickLoadMore"> -->
		<scroll-view scroll-y class="page" style="height:calc(100vh - 123px);">
			<view style="padding-bottom: 30px;">
				<view style="margin-top: 10px;" v-for="(league,index) in filterList" :key="index">
					<view class="myrect box-shadow flex-column bg-white"
						style="width: 96vw;justify-content: flex-start;margin-left: 2vw;">
						<view class="flex-row" style="margin-top: 9px;padding: 2vw;">
							<view class="mybg-orange"
								style="width: 3px;border-radius: 9px;height: 13px;margin: 0 5px 0;"></view>
							<view class="myfont-bold">{{league.name}}</view>
						</view>

						<view v-for="(match,_index) in league.matchList" :key="match.MATCH_ID" class="">
							<view class="mybg-dgrey" style="width: 96%;height: 2px;margin-left: 2%;"></view>
							<view class="flex-column margin" style="width: 96vw;">
								<!-- 比赛时间 -->
								<view class="flex-row text-lpadding text-bold"
									style="justify-content: flex-start;padding: 6px 0 6px;">
									<image style="height: 15px;width: 15px;margin: 0 5px 0 15px;"
										src="../../static/image/shijian.png"></image>
									<text>{{match.MATCH_MD_TIME}}</text>
								</view>

								<!-- 队伍名称 -->
								<view class="content-row flex-row myfont-bold text-black" style="padding: 5px 0 5px 0;">
									<view class="text-lpadding">{{language.bet_team}}</view>
									<view class="flex-row" style="width: 72%;line-height: 18px;">
										<view style="width: 37%;"
											:class="{'mycolor-blue':match.ATTR[0].LOSE_TEAM=='1'}">{{match.HOST_TEAM}}
										</view>
										<view style="width: 26%;">
											<image style="height: 10px;width: 20px;" src="../../static/image/vs.png">
											</image>
										</view>
										<view style="width: 37%;"
											:class="{'mycolor-blue':match.ATTR[0].LOSE_TEAM=='2'}">{{match.GUEST_TEAM}}
										</view>
									</view>
								</view>

								<view v-for="(attr,__index) in match.ATTR" :key="attr.MATCH_ATTR_ID" style="">

									<view class="content-row flex-row text-bold" style="line-height: 25px;"
										v-if="attr.MATCH_ATTR_TYPE==bet_type.SINGLE_BODY">
										<view class="text-lpadding">
											<text>{{language.bet_body}}</text>
										</view>
										<view class="content-row2 flex-row mybg-grey"
											style="width: 72%;margin-right: 3px;line-height: 40px;">
											<view style="width: 33%;" @click="betClick(1,index,_index,__index,attr)"
												:class="{' mybg-orange':attr.host_selected}">
												{{language.home}}
											</view>

											<view style="width: 33%;">{{attr.REAL_ODDS}}</view>

											<view style="width: 33%;" @click="betClick(2,index,_index,__index,attr)"
												:class="{'mybg-orange':attr.guest_selected}">
												{{language.away}}
											</view>
										</view>
									</view>

									<view class="flex-row content-row text-bold" style="line-height: 25px;"
										v-if="attr.MATCH_ATTR_TYPE==bet_type.SINGLE_GOAL">
										<view class="text-lpadding">
											<text>{{language.bet_goal}}</text>
										</view>
										<view class="content-row2 flex-row mybg-grey"
											style="width: 72%;margin-right: 3px;line-height: 40px;">
											<view style="width: 33%;" @click="betClick(1,index,_index,__index,attr)"
												:class="{'mybg-orange':attr.host_selected}">
												{{language.over}}
											</view>

											<view style="width: 33%;">{{attr.REAL_ODDS}}</view>

											<view style="width: 33%;" @click="betClick(2,index,_index,__index,attr)"
												:class="{'mybg-orange':attr.guest_selected}">
												{{language.under}}
											</view>
										</view>
									</view>

									<view class="flex-row content-row text-bold" style="line-height: 30px;"
										v-if="attr.MATCH_ATTR_TYPE==bet_type.SINGLE_WDL">
										<view class="text-lpadding">
											<text>1X2</text>
										</view>
										<view class="content-row flex-row mybg-grey"
											style="width: 72%;margin-right: 3px;line-height: 40px;">
											<view style="width: 33%;" @click="betClick(1,index,_index,__index,attr)"
												:class="{'mybg-orange':attr.host_selected}">
												{{attr.ODDS}}
											</view>

											<view style="width: 33%;height: 40px;line-height: 40px;"
												@click="betClick(3,index,_index,__index,attr)"
												:class="{'mybg-orange':attr.draw_selected}">
												{{attr.DRAW_ODDS}}
											</view>

											<view style="width: 33%;" @click="betClick(2,index,_index,__index,attr)"
												:class="{'mybg-orange':attr.guest_selected}">
												{{attr.ODDS_GUEST}}
											</view>
										</view>
									</view>

									<!-- <view class="flex-row content-row text-bold" style="line-height: 25px;" v-if="attr.MATCH_ATTR_TYPE==bet_type.SINGLE_EVEN">
									<view class="text-lpadding">
										<text>{{language.odd_even}}</text>
									</view>
									<view class="content-row2 flex-row mybg-grey" style="width: 72%;margin-right: 3px;line-height: 40px;">
										<view style="width: 37%;" @click="betClick(1,index,_index,__index,attr)" :class="{'mybg-orange':attr.host_selected}">
											{{language.odd}}
										</view>

										<view style="width: 26%;">-</view>

										<view style="width: 37%;" @click="betClick(2,index,_index,__index,attr)" :class="{'mybg-orange':attr.guest_selected}">
											{{language.even}}
										</view>
									</view>
								</view> -->

								</view>
							</view>
						</view>
					</view>
				</view>
			</view>
		</scroll-view>
		<view class="amount-bar bg-white flex-row">
			<view class="flex-row text-black text-bold text-center padding" style="justify-content: space-around;">
				<text>{{language.selected}}<text space="nbsp"
						class="text-yellow text-bold">{{' '+num+' '}}</text>{{language.units}}</text>
				<input :placeholder="language.amount" class="mybg-grey myinput" v-model="amount"
					@input='inputNum($event)'></input>
				<button class="mybg-orange" style="width: 30%;height: 30px;line-height: 30px;" @click="confirm">
					{{'OK&nbsp'}}
					<image style="width: 13px;height: 10px;" src="../../static/image/dui.png"></image>
				</button>
			</view>

			<!-- <view style="width: 40%;font-size: 18px;font-weight: bold;line-height: 70px;text-align: center;background-color: rgb(185, 1, 0);color:white;height:70px"
			 @click="confirm">
				O K
			</view> -->
		</view>

		<uni-popup ref="popup" type="center">
			<view class="popup">
				<view class="text-center text-bold mybg-red border"
					style="border-radius:13px 13px 0 0;height: 46px;line-height: 46px;">{{language.detail}}</view>

				<view class="bg-white" style="padding-top: 10px;">
					<view class="myrect mybg-grey" style="width: 96%;margin: 0 2% 0 2%;font-size: 14px;">
						<view class="flex-row text-bold mycolor-red"
							style="padding: 3px 0px 3px 0px;line-height: 16px;font-size: 15px;">
							<view style="width: 40%;">
								<text>{{language.bet_host}}</text>
								<span style='font-size: 10px;' class="mycolor-orange">{{'V'}}</span>
								<text>{{language.bet_guest}}</text>
								<!-- <text v-if="language.lang=='myan'">{{language.bet_guest.slice(0,4)}}<br>
								<span style='float: right;'>{{language.bet_guest.slice(4)}}</span></text>
								<text v-else>{{language.bet_guest}}</text> -->
							</view>
							<view style="width: 20%;">{{language.bet_type}}</view>
							<view style="width: 15%;">{{language.bet_odds}}</view>
							<view style="width: 25%;">{{language.bet_bet}}</view>
						</view>
						<scroll-view scroll-y style="height: 40vh;" class="order bg-white">
							<view :class="index%2==0?'bg-white':'mybg-dgrey'" v-for="(order,index) in  orders"
								class="flex-row text-bold" style="padding:6px 0;min-height: 60px;">

								<view style="width: 35%;word-wrap:break-word;word-break:break-all;padding-left: 10px;" v-if="order.ATTR.MATCH_ATTR_TYPE == bet_type.SINGLE_GOAL">
									<text>{{order.HOST_TEAM}}</text>
									<text class="mycolor-orange">{{order.ATTR.ODDS_DESC}}</text>
									<text class="mycolor-red" style="margin:0 2px;font-weight: 1000;">VS</text>
									<text>{{order.GUEST_TEAM}}</text>
									<!-- <text v-if="order.ATTR.guest_selected"
										class="mycolor-orange">{{order.ATTR.ODDS_DESC}}</text> -->
								</view>
								<view style="width: 35%;word-wrap:break-word;word-break:break-all;padding-left: 10px;" v-else>
									<text>{{order.HOST_TEAM}}</text>
									<text v-if="order.ATTR.LOSE_TEAM=='1'"
										class="mycolor-orange">{{order.ATTR.ODDS_DESC}}</text>
									<text class="mycolor-red" style="margin:0 2px;font-weight: 1000;">VS</text>
									<text>{{order.GUEST_TEAM}}</text>
									<text v-if="order.ATTR.LOSE_TEAM=='2'"
										class="mycolor-orange">{{order.ATTR.ODDS_DESC}}</text>
								</view>

								<view style="width: 25%;">{{order.ATTR.ATTR_TYPE}}</view>
								<view style="width: 15%;">
									{{order.ATTR.MATCH_ATTR_TYPE == bet_type.SINGLE_WDL?calWDL_Odds(order.ATTR):'2'}}
								</view>

								<view style="width: 25%;">{{betContent(order)}}</view>
							</view>
						</scroll-view>
					</view>
				</view>

				<view style="background-color: white;padding-bottom: 10px;">

					<view class="myrect mybg-dgrey text-bold" style="width: 96%;margin: 0 2% 0 2%;">
						
						<view style="width: 100%;height: 38px; display: flex;flex-direction: row;justify-content: space-around;align-items: center;">
							<view style="text-align: left;width: 50%;padding-left:12px;">{{language.current_time}}</view>
							<view style="text-align: right;width: 50%;padding-right: 12px;">{{currentTime}}</view>
						</view>
						
						<view
							style="width: 100%;height: 38px; display: flex;flex-direction: row;justify-content: space-around;align-items: center;">
							<view style="text-align: left;width: 50%;padding-left:12px;">{{language.type}}</view>
							<view style="text-align: right;width: 50%;padding-right: 12px;">{{language.single}}</view>
						</view>

						<view
							style="width: 100%;height: 38px; display: flex;flex-direction: row;justify-content: space-around;align-items: center;">
							<view style="text-align: left;width: 50%;padding-left:12px;">{{language.amount}}</view>
							<view style="text-align: right;width: 50%;padding-right: 12px;">{{numberFormat(amount)}}
							</view>
						</view>

						<view
							style="width: 100%;height: 38px; display: flex;flex-direction: row;justify-content: space-around;align-items: center;">
							<view style="text-align: left;width: 50%;padding-left:12px;">{{language.benefitMax}}</view>
							<view style="text-align: right;width: 50%;padding-right: 12px;">{{numberFormat(benefitMax)}}
							</view>
						</view>
					</view>

				</view>
				<view class="mybg-pink text-center flex-row"
					style="border-radius: 0 0  13px 13px ;height: 46px;justify-content: space-around;">
					<button class="cu-btn mybg-red" style="width: 40%;" @click="$refs.popup.close()">cancel</button>
					<button class="cu-btn mybg-orange" style="width: 40%;"
						@click="$noMultipleClicks(submit)">OK</button>
				</view>
			</view>

		</uni-popup>
	</view>
</template>

<script>
	import config from '../../utils/config.js'
	import Vue from "vue";
	import uniPopup from "@/components/uni-popup/uni-popup.vue"
	import matchList from '../plugin/matchList.vue'
	import dateFormatUtils from "../../utils/utils.js"

	export default {
		components: {
			uniPopup,
			matchList
		},
		data() {
			return {
				language: config.language,
				status: 'more',
				amount: 0,
				bet_type: {
					'SINGLE_BODY': '1',
					'SINGLE_GOAL': '2',
					'SINGLE_EVEN': '6',
					'SINGLE_WDL': '10',
				},
				currentPage: 1,
				modalName: null,
				benefitMax: 0,
				orders: [],
				num: 0,
				limit: 300,
				matchList: [],
				currentTime:'',
				leagueList: [],
				list: [],
				allStatus: false,
				intervalId: '',
				confirmIntervalId:'',
				filterScale: '',
				filterList: [], //用作展示过滤后的数据
				leagueObjs: [], //联赛选择对象数组
				contentText: {
					contentdown: 'more',
					contentrefresh: 'loading',
					contentnomore: 'no more'
				},
				config: config
			}
		},
		watch: {
			'$store.state.configs.single_min': function() {
				this.amount = parseInt(this.$store.state.configs.single_min);
			}
		},
		methods: {
			hideConfirm() {
				this.$refs.popup.close();
				clearInterval(this.confirmIntervalId)
			},
			calWDL_Odds(attr) {
				if (attr.MATCH_ATTR_TYPE == this.bet_type.SINGLE_WDL) {
					if (attr.host_selected) {
						return attr.ODDS
					} else if (attr.draw_selected) {
						return attr.DRAW_ODDS
					} else {
						return attr.ODDS_GUEST
					}
				}
			},
			betContent(order) {
				switch (order.ATTR.MATCH_ATTR_TYPE) {
					case this.bet_type.SINGLE_BODY:
						if (order.ATTR.host_selected) {
							return order.HOST_TEAM
						} else {
							return order.GUEST_TEAM
						}
						break
					case this.bet_type.SINGLE_GOAL:
						if (order.ATTR.host_selected) {
							return this.language.over
						} else {
							return this.language.under
						}
						break
					case this.bet_type.SINGLE_EVEN:
						if (order.ATTR.host_selected) {
							return this.language.odd
						} else {
							return this.language.even
						}
						break
					case this.bet_type.SINGLE_WDL:
						if (order.ATTR.host_selected) {
							return this.language.wdl_home
						} else if (order.ATTR.guest_selected) {
							return this.language.wdl_away
						} else {
							return this.language.wdl_draw
						}
						break
				}
			},
			toHome() {
				uni.reLaunch({
					url: '/pages/index/index'
				})
			},
			hideOrder() {
				// this.music.play_dede()
				this.$refs.popup.close()
			},
			numberFormat(num) {
				return dateFormatUtils.numFormat(num)
			},
			selectAll() {
				// this.music.play_dede()
				if (!this.allStatus) {
					this.allStatus = true;
					this.leagueObjs.forEach(element => {
						element.checked = true;
					})
				} else {
					this.allStatus = false;
					this.leagueObjs.forEach(element => {
						element.checked = false;
					})
				}
			},
			confirm() {
				// this.music.play_dede()
				var _this = this;
				_this.orders = []
				
				var closeConfirm = 0;
				
				var date = new Date()
				//计算中时区
				var UTCTime = new Date(date.getUTCFullYear(), date.getUTCMonth(), date
					.getUTCDate(), date
					.getUTCHours(), date.getUTCMinutes(), date.getUTCSeconds()).getTime()
								
				UTCTime = UTCTime + +8 * 60 * 60 * 1000;
				UTCTime = new Date(UTCTime)
				_this.currentTime = dateFormatUtils.formatTime(UTCTime);
				_this.currentTime = _this.currentTime.substring(5, _this.currentTime.length-1)
				
				_this.confirmIntervalId = setInterval(function() {
					closeConfirm ++
					if(closeConfirm>=60){
						_this.$refs.popup.close();
						clearInterval(_this.confirmIntervalId)
					}
				}, 1000);
				
				_this.list.forEach(league => {
					league.matchList.forEach(match => {
						match.ATTR.forEach(attr => {
							if (attr.host_selected || attr.guest_selected || attr.draw_selected) {

								var ele = Object.assign({}, match)
								ele.ATTR = Object.assign({}, attr);
								// if (ele.ATTR.MATCH_ATTR_TYPE == this.bet_type.SINGLE_WDL) {
								// 	if (ele.ATTR.host_selected) {
								// 		ele.ATTR.WDL_ODDS = ele.ATTR.ODDS
								// 	} else if (ele.ATTR.draw_selected) {
								// 		ele.ATTR.WDL_ODDS = ele.ATTR.DRAW_ODDS
								// 	} else {
								// 		ele.ATTR.WDL_ODDS = ele.ATTR.ODDS_GUEST
								// 	}
								// } else 
								if (ele.ATTR.MATCH_ATTR_TYPE != '6') {
									var DRAW_BUNKO = ele.ATTR.DRAW_BUNKO == '0' ? '+' : '-';
									ele.ATTR.ODDS_DESC = '(' + ele.ATTR.LOSE_BALL_NUM +
										DRAW_BUNKO + ele.ATTR.DRAW_ODDS + ')' //(2-50)
								} else {
									ele.ATTR.ODDS_DESC = attr.host_selected ? ele.ATTR.ODDS : ele
										.ATTR.ODDS_GUEST;
								}

								if (ele.ATTR.MATCH_ATTR_TYPE == '1') {
									ele.ATTR.ATTR_TYPE = _this.language.body + '  '; //上下盘
								} else if (ele.ATTR.MATCH_ATTR_TYPE == '2') {
									ele.ATTR.ATTR_TYPE = config.language.goal + '  '; //大小盘
								} else if (ele.ATTR.MATCH_ATTR_TYPE == '6') {
									ele.ATTR.ATTR_TYPE = config.language.odd_even + '  '; //单双盘
								} else if (ele.ATTR.MATCH_ATTR_TYPE == _this.bet_type.SINGLE_WDL) {
									ele.ATTR.ATTR_TYPE = '1X2' + '  '; //胜平负
								}
								_this.orders.push(ele)
							}

						})
					})
				});
				if (_this.orders.length == 0) {
					uni.showModal({
						title: 'tips',
						content: _this.language.atLeastOneGame,
						showCancel: false,
						confirmText: 'ok',
						success: function(res) {}
					});

				} else {
					var totalAmount = _this.amount * _this.orders.length;
					_this.benefitMax = _this.amount
					_this.orders.forEach(ele => {
						if (ele.ATTR.MATCH_ATTR_TYPE == _this.bet_type.SINGLE_WDL) {
							_this.benefitMax = _this.benefitMax * parseFloat(_this.calWDL_Odds(ele.ATTR))
						} else {
							_this.benefitMax = _this.benefitMax * 2
						}
					})
					this.$refs.popup.open()
				}
				_this.amountFormat = dateFormatUtils.numFormat(_this.amount);
			},
			inputNum: function(evt) {
				let amount = evt.detail.value
				amount = amount ? parseInt(amount) : '0'
				this.$nextTick(function() {
					Vue.set(this, 'amount', amount)
				})
			},
			getMatchList() {
				var _this = this;
				uni.showLoading({
					title: 'loading'
				})
				var para = {
					page: _this.currentPage,
					limit: _this.limit,
					odds_type: 'single'
				}
				_this.$http.get('/match/get', {
					data: para
				}, (res) => {
					if (res.data.code == 20000) {
						_this.matchList = res.data.items;
						_this.loaddingData(res.data.total);

						uni.hideLoading();
						if (res.data.items.length == 0) {
							uni.showToast({
								title: 'no more',
								icon: 'none'
							})
						}
					}
				})

			},
			updateOdds() {
				var _this = this;
				this.$http.get('/match/get_odds', {}, (res) => {
					if (res.data.code == 20000) {
						res.data.items.forEach(element => {
							element.DRAW_BUNKO = element.DRAW_BUNKO == '0' ? '+' : '-';
							if (element.DRAW_ODDS == '0') {
								element.REAL_ODDS = element.LOSE_BALL_NUM + '='
							} else {
								element.REAL_ODDS = element.LOSE_BALL_NUM + element.DRAW_BUNKO + element
									.DRAW_ODDS;
							}
							_this.list.forEach((league, index) => {
								league.matchList.forEach((match, _index) => {
									match.ATTR.forEach((attr, __index) => {
										if (attr.MATCH_ATTR_ID == element
											.MATCH_ATTR_ID) {
											attr.REAL_ODDS = element.REAL_ODDS;
											attr.ODDS = element.ODDS;
											attr.ODDS_GUEST = element.ODDS_GUEST;
											attr.DRAW_ODDS = element.DRAW_ODDS;
											attr.change = true;
											Vue.set(_this.list[index].matchList[
													_index].ATTR, __index,
												attr);
											setTimeout(function() {
												attr.change = false;
												Vue.set(_this.list[index]
													.matchList[_index]
													.ATTR, __index,
													attr);
											}, 5000)
										}
									})
								})
							})
						})
					}
				})
			},
			betClick(type, index, _index, __index, temp) {
				// this.music.play_dede()
				var _this = this;
				var match = _this.filterList[index].matchList[_index];
				_this.num = 0;

				//选中的比赛,高亮显示
				if (type == '3') {
					if (!temp.draw_selected) {
						temp.draw_selected = true;
						temp.guest_selected = false;
						temp.host_selected = false;
					} else {
						temp.draw_selected = false;
						temp.guest_selected = false;
						temp.host_selected = false;
					}
				} else if (type == '1') {
					if (temp.MATCH_ATTR_TYPE == this.bet_type.SINGLE_WDL) {
						temp.draw_selected = false;
					}
					if (!temp.host_selected) {
						temp.host_selected = true;
						temp.guest_selected = false;
					} else {
						temp.host_selected = false;
					}
				} else {
					if (temp.MATCH_ATTR_TYPE == this.bet_type.SINGLE_WDL) {
						temp.draw_selected = false;
					}
					if (!temp.guest_selected) {
						temp.host_selected = false;
						temp.guest_selected = true;
					} else {
						temp.guest_selected = false;
					}
				}
				match[__index] = temp;
				_this.num++;
				// Vue.set(_this.list[index].matchList, _index, match);

				//未选中的比赛 , 全部取消高亮
				_this.list.forEach(_league => {
					//未选中的比赛,取消高亮
					_league.matchList.forEach(_match => {
						_match.ATTR.forEach(_attr => {
							if (temp.MATCH_ATTR_ID != _attr.MATCH_ATTR_ID) {
								_attr.host_selected = false;
								_attr.guest_selected = false;
								_attr.draw_selected = false;
							}
						})
					})
				})


			},
			reset() {
				// this.music.play_dede()
				var _this = this;
				_this.list.forEach((league, index) => {
					league.matchList.forEach((match, _index) => {
						Vue.set(_this.list[index].matchList, _index, match);
						match.ATTR.forEach(attr => {
							attr.host_selected = false;
							attr.guest_selected = false;
							attr.draw_selected = false;
						})
						Vue.set(_this.list[index].matchList, _index, match);
					})
				})
				_this.num = 0;
				_this.amount = _this.$store.state.configs.single_min;
			},
			submit() {
				// this.music.play_dede()
				var _this = this;
				uni.showLoading({
					title: 'loading',
				})
				clearInterval(this.confirmIntervalId)
				
				//console.log(JSON.stringify(order));
				var paras = [];
				var checkAttrs = {}
				_this.orders.forEach(element => {
					var temp = {
						matchId: element.MATCH_ID,
						attrType: element.ATTR.MATCH_ATTR_TYPE,
						betType: element.ATTR.draw_selected ? 3 : element.ATTR.host_selected || element.ATTR
							.over_selected ? 1 : 2,
						amount: parseInt(_this.amount)
					}
					checkAttrs[element.ATTR.MATCH_ATTR_ID] = element.ATTR;
					checkAttrs[element.ATTR.MATCH_ATTR_ID].BET_TYPE = element.ATTR.draw_selected ? 3 : element.ATTR
						.host_selected || element.ATTR.over_selected ? 1 : 2
					paras.push(temp)
				})
				//校验是否超出限额
				if (_this.amount > parseInt(_this.$store.state.configs.single_max)) {
					uni.hideLoading();

					uni.showModal({
						title: 'Tips',
						content: _this.language.single_max + " (" + _this.$store.state.configs.single_max + ")",
						showCancel: false,
						confirmText: 'ok',
						success: function(res) {}
					});
					return;
				}
				if (_this.amount < parseInt(_this.$store.state.configs.single_min)) {
					uni.hideLoading();
					uni.showModal({
						title: 'Tips',
						content: _this.language.single_min + " (" + _this.$store.state.configs.single_min + ")",
						showCancel: false,
						confirmText: 'ok',
						success: function(res) {}
					});

					return;
				}

				var changeList = [];
				_this.$http.post('/order/check_odds', {
					attrs: checkAttrs
				}, (res) => {
					if (res.data.code = 20000) {
						changeList = res.data.items;
						if (changeList.length > 0) {
							uni.showModal({
								title: 'tips',
								content: _this.language.odds_change,
								showCancel: false,
								confirmText: 'အတည်ပြုမည်',
								success: function(res) {
									_this.orders.forEach((element, index, ) => {
										changeList.forEach(ele => {
											if (ele.MATCH_ATTR_ID == element.ATTR
												.MATCH_ATTR_ID) {
												var DRAW_BUNKO = ele.DRAW_BUNKO ==
													'0' ? '+' : '-';

												element.ATTR.ODDS_DESC = '(' + ele
													.LOSE_BALL_NUM +
													DRAW_BUNKO + ele.DRAW_ODDS +
													')' //(2-50)

												element.ATTR.LOSE_BALL_NUM = ele
													.LOSE_BALL_NUM;
												element.ATTR.DRAW_BUNKO = ele
													.DRAW_BUNKO;
												element.ATTR.DRAW_ODDS = ele.DRAW_ODDS;
												element.ATTR.ODDS = ele.ODDS;
												element.ATTR.ODDS_GUEST = ele
													.ODDS_GUEST;
												Vue.set(_this.orders, index, element)
											}
										})
									})
									uni.hideLoading()
									return;
								}
							})
						} else {
							_this.hideOrder();
							_this.$http.post('/order/single_bet', {
								bets: paras
							}, (res) => {
								uni.hideLoading();
								if (res.data.code == 20000) {
									uni.showModal({
										content: _this.language.bettingSuccess,
										title: tips,
										showCancel: false,
										confirmText: 'ok',
										success: function() {
											var userInfo = _this.$store.state.userInfo
											userInfo.TOTAL_MONEY = parseInt(userInfo
												.TOTAL_MONEY) - parseInt(_this.amount);
											_this.$store.dispatch('saveUserInfo', userInfo);
											//把选过的比赛刷掉
											_this.reset();
										}
									});
								} else {
									var tips = '';
									if (_this.language[res.data.message]) {
										tips = _this.language[res.data.message] + "(" + _this.$store.state
											.configs[res.data.message] + ")"
									} else {
										tips = res.data.message;
									}
									uni.showModal({
										title: 'tips',
										content: tips,
										showCancel: false,
										confirmText: 'ok',
										success: function(res) {}
									});
								}
							})
						}
					}
				})



				// _this.hideOrder();
				// _this.$http.post('/order/single_bet', {
				// 	bets: paras
				// }, (res) => {
				// 	uni.hideLoading();
				// 	if (res.data.code == 20000) {
				// 		uni.showModal({
				// 			content: _this.language.bettingSuccess,
				// 			title: tips,
				// 			showCancel: false,
				// 			confirmText: 'ok',
				// 			success: function() {
				// 				var userInfo = _this.$store.state.userInfo
				// 				userInfo.TOTAL_MONEY = parseInt(userInfo.TOTAL_MONEY) - parseInt(_this.amount);
				// 				_this.$store.dispatch('saveUserInfo', userInfo);
				// 				//把选过的比赛刷掉
				// 				_this.reset();
				// 			}
				// 		});
				// 	} else {
				// 		var tips = '';
				// 		if (_this.language[res.data.message]) {
				// 			tips = _this.language[res.data.message] + "(" + _this.$store.state.configs[res.data.message] + ")"
				// 		} else {
				// 			tips = res.data.message;
				// 		}

				// 		uni.showModal({
				// 			title: 'tips',
				// 			content: tips,
				// 			showCancel: false,
				// 			confirmText: 'ok',
				// 			success: function(res) {}
				// 		});
				// 	}
				// })


			},
			loaddingData(more) {
				//获取联赛数组
				var _this = this;
				if (more) {
					var newLeagueList = []
					_this.matchList.forEach(match => {
						//加载上下盘,大小盘选中数据
						match.MATCH_MD_TIME = match.MATCH_MD_TIME.substring(5, 16);
						let match_attr = match.ATTR
						match_attr.sort(function(a, b) {
							return parseInt(a.MATCH_ATTR_TYPE) - parseInt(b.MATCH_ATTR_TYPE)
						})
						match_attr.forEach(attr => {
							attr.host_selected = false;
							attr.guest_selected = false;
							var DRAW_BUNKO = attr.DRAW_BUNKO == '0' ? '+' : '-';
							if (attr.DRAW_ODDS == '0') {
								attr.REAL_ODDS = attr.LOSE_BALL_NUM + '='
							} else {
								attr.REAL_ODDS = attr.LOSE_BALL_NUM + DRAW_BUNKO + attr.DRAW_ODDS;
							}

							// 测试
							// if(attr.MATCH_ATTR_TYPE == '10'){
							// 	attr.DRAW_ODDS = '5.00'
							// }
						})
						match.ATTR = match_attr
						if (_this.leagueList.indexOf(match.REMARK) < 0 && newLeagueList.indexOf(match.REMARK) <
							0) {
							newLeagueList.push(match.REMARK)
						}
						//如果当前联赛已存在
						if (_this.leagueList.indexOf(match.REMARK) > -1) {
							_this.list.forEach(element => {
								if (element.name == match.REMARK) {
									element.matchList.push(match)
								}
							})
						}
					})
					//装载当前没有的联赛
					newLeagueList.forEach(league => {
						//如果是同一个联赛 ，则加载到对应的matchList内
						var temp = {
							'name': league,
							matchList: []
						}
						_this.matchList.forEach(match => {

							var containBody = false;
							match.ATTR.forEach(attr => {
								if (attr.MATCH_ATTR_TYPE == '1') {
									containBody = true;
								}
							})

							if (match.REMARK == league && containBody) {
								temp.matchList.push(match);
							}
						})
						if (temp.matchList.length > 0) _this.list.push(temp);
					})

					//先把赛事根据首字母排列
					_this.list.sort(function(a, b) {
						return a.name.localeCompare(b.name)
						// return a.name.charCodeAt(0) - b.name.charCodeAt(0);
					})

					//将config中的联赛置顶
					config.leagues.forEach(leagueOfConfig => {
						_this.list.forEach((leagueOfList, index) => {
							if (leagueOfConfig.toUpperCase() == leagueOfList.name.toUpperCase()) {
								//将该元素 置顶
								_this.list.unshift(_this.list.splice(index, 1)[0]);
							}
						})
					})

					//把比赛加入显示数组
					_this.filterList = [].concat(_this.list);

					//把没有的联赛加入已有联赛
					_this.leagueList = _this.leagueList.concat(newLeagueList);

					//把联赛加入对象数组
					_this.leagueObjs = [];
					_this.leagueList.forEach(ele => {
						var temp = {
							name: ele,
							checked: false
						}
						_this.leagueObjs.push(temp);
					})

					_this.leagueObjs.sort(function(a, b) {
						// return a.name.charCodeAt(0) - b.name.charCodeAt(0);
						return a.name.localeCompare(b.name)
					})

					config.leagues.forEach(league => {
						this.leagueObjs.forEach((_league, index) => {
							if (league.toUpperCase() == _league.name.toUpperCase()) {
								this.leagueObjs.unshift(this.leagueObjs.splice(index, 1)[0]);
							}
						})
					})

					//读取config中的联赛,对比去重 ,然后拼接
					/*
					var config_leagues = [];
					config.leagues.forEach(league => {
						var temp = {
							name: league,
							checked: false
						}
						config_leagues.push(temp);
						_this.leagueObjs.forEach((_league, index) => {
							if (league.toUpperCase() == _league.name.toUpperCase()) {
								_this.leagueObjs.splice(index, 1);
							}
						})
					})
					_this.leagueObjs = config_leagues.concat(_this.leagueObjs)
					*/
				}
			},
			ChooseCheckbox(e) {
				// this.music.play_dede();
				let items = this.leagueObjs;
				let values = e.currentTarget.dataset.value;
				for (let i = 0, lenI = items.length; i < lenI; ++i) {
					if (items[i].name == values) {
						items[i].checked = !items[i].checked;
						break
					}
				}
			},
			showModal(e) {
				// this.music.play_dede();
				this.filterScale = 'filter: grayscale(100%)'
				this.modalName = e.currentTarget.dataset.target
			},
			hideModal(e) {
				// this.music.play_dede();
				this.modalName = null
				this.filterScale = ''
			},
			setLeagueFilter() {
				// this.music.play_dede();
				//全不选
				let noSelect = true;
				this.leagueObjs.forEach(league => {
					if (league.checked) {
						noSelect = false;
					}
				})
				if (!noSelect) {
					this.filterList = [];
					this.leagueObjs.forEach(league => {
						if (league.checked) {
							this.list.forEach(_league => {
								if (_league.name == league.name) {
									this.filterList.push(_league);
								}
							})
						}
					})
				}
				this.hideModal();
			},
			clickLoadMore() {
				// this.music.play_dede();
				var _this = this;
				_this.currentPage++;
				_this.getMatchList();
			}
		},
		onLoad() {
			this.getMatchList()
			let _this = this
			_this.intervalId = setInterval(function() {
				let page_list = getCurrentPages()
				if (page_list[page_list.length - 1].route.indexOf('pages/match/single') < 0) {
					clearInterval(_this.intervalId);
					_this.intervalId = null
				} else {
					_this.updateOdds()
				}
			}, 60*1000);

			// console.log('config', this.$store.state.configs)
			this.amount = parseInt(this.$store.state.configs.single_min);

		},
		//离开当前页面后执行
		destroyed: function() {
			clearInterval(this.intervalId);
		}
	}
</script>

<style>
	.league-row {
		padding: 5px;
		display: flex;
		flex-direction: row;
		justify-content: flex-start;
		align-items: center;
	}

	.league-row image {
		width: 25px;
		height: 25px;
	}

	.list {
		margin-top: 5px;
		background-color: #F2F2F2;
		padding: 12px 8px;
		border: 1px solid lightgrey;
	}

	.row {
		display: flex;
		flex-direction: row;
		text-align: center;
		justify-content: space-around;
		align-items: center;
	}

	.cell {
		width: 25%;
		height: 38px;
		line-height: 38px;
	}

	.page {
		width: 100vw;
		margin-bottom: 80px;
	}

	.bg-lightgrey {
		background-color: #F2F2F2;
	}

	.width_auto {
		width: calc(100% - 90px) !important;
	}

	.content {
		left: 12px !important
	}

	.yellow {
		background-color: #e3c817;
	}

	.popup {
		width: 96vw;
	}

	.page.show {
		overflow: hidden;
	}

	.padding-sm {
		padding-top: 5px;
		padding-bottom: 5px;
	}

	.border {
		border: 1px solid lightgrey;
	}

	.border-bottom {
		border-bottom: 1px solid #E2E2E2;
	}

	.cu-list {
		margin-top: 0;
	}

	.text-center {
		height: 32px;
		line-height: 32px;
	}

	.margin-top {
		margin-top: 8px;
	}

	.center {
		text-align: center;
	}

	.bg-green {
		background-color: rgb(41, 150, 56)
	}

	.grey {
		background-color: #F2F2F2;
		color: #666666;
	}

	.bg-orange {
		background-color: #e0620d !important;
	}

	.bg-gray {
		background-color: #373636;
	}

	.text-lpadding {
		text-align: left;
		padding-left: 15px;
		color: black;
	}

	.content-row {
		width: 96vw;
	}

	.content-row view:first-child {
		width: 24vw;
	}

	.content-row view:nth-child(2) {
		width: 72vw;
		line-height: 30px;
	}

	.order {
		height: 50vh;
	}

	.amount-bar {
		height: 70px;
		position: fixed;
		width: 100%;
		bottom: 0;
		color: white;
	}

	.myinput {
		font-size: 14px;
		height: 30px;
		border-radius: 8px;
		margin: 3vw 0 3vw 10px;
		text-align: center;
		width: 30%;
	}

	.topic_cont_text {
		overflow: hidden;
		word-break: break-all;
		/* break-all(允许在单词内换行。) */
		text-overflow: ellipsis;
		/* 超出部分省略号 */
		display: -webkit-box;
		/** 对象作为伸缩盒子模型显示 **/
		-webkit-box-orient: vertical;
		/** 设置或检索伸缩盒对象的子元素的排列方式 **/
		-webkit-line-clamp: 3;
		/** 显示的行数 **/
		max-height: 32px;
	}
</style>
