<template name="orders">
	<view class="mybg-grey full-page">
		<cu-custom isBack :backUrl="navi2D3D=='3D'? '/pages/number/3d-number-bet' : '/pages/number/number-bet'">
			<block slot="content" style="width: 100%;">
				<view style="font-size: 13px;">{{language.myBet_digit}}</view>
			</block>
		</cu-custom>

		<view class="article flex-row myfont-bold" style="justify-content: space-around;">
			<view style="height: 35px;line-height: 35px;width: 50%;" @click="handleTabChange(0)"><text
					:class="activeTab==0?'mycolor-green under-line':''">{{language.unorderd_digit}}</text></view>
			<view style="height: 35px;line-height: 35px;width: 50%;" @click="handleTabChange(1)"><text
					:class="activeTab==1?'mycolor-green under-line':''">{{language.completed_digit}}</text></view>
		</view>

		<scroll-view scroll-y v-show="activeTab==0" style="height: calc(100vh - 90px);">
			<view class="cu-list menu-avatar" v-for="(order,index) in unordered" @click="showOrderDetails(order,0)"
				:key="index">
				<view class="myrect box-shadow flex-column bg-white"
					style="width: 96vw;justify-content: flex-start;margin: 2vw;">
					<view class="flex-column">
						<view class="flex-row myfont-bold content-row" style="width: 90%;">
							<text class="team-name mycolor-green">{{order.ORDER_DESC}}</text>
							<image v-if="order.IS_MIX=='1'" class="mix_icon" src="../../static/icon/M.png"></image>

							<view class="text-grey text-xs">{{order.CREATE_TIME}}</view>
						</view>

						<view class="content-row2 flex-row content-row myrect mybg-grey"
							style="width: 95%;justify-content: space-between;">
							<view>
								<text class="cuIcon-infofill text-red  margin-right-xs"></text>
								<text>{{order.BET_TYPE}}</text> <text space="nbsp"> {{order.ODDS_DESC}}</text>
								<text class="text-blue" space="nbsp">{{order.BET_CONTENT}}</text>
								<text style="vertical-align:baseline;height:16px;line-height: 16px;margin-left: 5px;"
									class="cu-tag radius bgp-colr sm">{{numberFormat(order.BET_MONEY)}}</text>
								<text v-if="order.IS_MIX=='1'"
									style="vertical-align:baseline;height:16px;line-height: 16px;"
									class="cu-tag radius bglg-colg sm">{{order.REMARK}}</text>
							</view>

							<view>
								<view class="mycolor-orange myfont-bold">
									{{order.IS_WIN=='0'?'Lose':order.IS_WIN=='1'?'Win':'Waiting'}}
								</view>
							</view>
						</view>
					</view>
				</view>
			</view>

		</scroll-view>

		<scroll-view scroll-y v-show="activeTab==1" style="height: calc(100vh - 90px);">
			<view class="cu-list menu-avatar" v-for="(order,index) in completed" @click="showOrderDetails(order,1)"
				:key="index">
				<view class="myrect box-shadow flex-column bg-white"
					style="width: 96vw;justify-content: flex-start;margin: 2vw;">
					<view class="flex-column">
						<view class="flex-row myfont-bold content-row" style="width: 90%;">
							<text class="team-name mycolor-green">{{order.ORDER_DESC}}</text>
							<image v-if="order.IS_MIX=='1'" class="mix_icon" src="../../static/icon/M.png"></image>

							<view class="text-grey text-xs">{{order.CREATE_TIME}}</view>
						</view>

						<view class="content-row2 flex-row content-row myrect mybg-grey"
							style="width: 95%;justify-content: space-between;">
							<view>
								<text class="cuIcon-infofill text-red  margin-right-xs"></text>
								<text>{{order.BET_TYPE}}</text> <text space="nbsp"> {{order.ODDS_DESC}}</text>
								<text class="text-blue" space="nbsp">{{order.BET_CONTENT}}</text>
								<text style="vertical-align:baseline;height:16px;line-height: 16px;margin-left: 5px;"
									class="cu-tag radius bgp-colr sm">{{numberFormat(order.BET_MONEY)}}</text>
								<text v-if="order.IS_MIX=='1'"
									style="vertical-align:baseline;height:16px;line-height: 16px;"
									class="cu-tag radius bglg-colg sm">{{order.REMARK}}</text>
							</view>

							<view>
								<view v-if="order.IS_WIN=='0'" class="mycolor-green myfont-bold">Lose</view>
								<view v-if="order.IS_WIN=='1'" class="mycolor-green myfont-bold">
									+{{numberFormat(order.BONUS) }}</view>
								<view v-if="order.IS_WIN=='2'" class="mycolor-orange myfont-bold">Waiting</view>
							</view>
						</view>
					</view>
				</view>
			</view>
		</scroll-view>
		<view class="amount-bar flex flex-wrap justify-center">
			<view style="width: 100%;">
				<!-- <button @tap='popupOpen(1)' style="" class="mybg-orange">{{language.bet_time}}</button> -->
				<button style="width: 40%;border-radius: 10px;" @tap='popupOpen(1)'
					class="cu-btn margin-sm shadow mybg-orange">{{language.bet_time}}</button>
			</view>
		</view>

		<uni-popup ref="popup1" type="bottom">
			<view style="height: 120px;width: 100vw;background-color: white;">
				<view style="width: 100vw;height: 30px;line-height: 30px;" class="text-center border-bottom margin">
					{{language.bet_time}}
				</view>
				<view class="flex flex-wrap" style="justify-content: space-around;">
					<button class="cu-btn" :class="listQuery.time==0?'mybg-green':''"
						@click="buttonPress(1,0)">{{language.all}}</button>
					<button class="cu-btn" :class="listQuery.time==1?'mybg-green':''"
						@click="buttonPress(1,1)">{{language.one_week}}</button>
					<button class="cu-btn" :class="listQuery.time==2?'mybg-green':''"
						@click="buttonPress(1,2)">{{language.one_month}}</button>
				</view>
			</view>
		</uni-popup>


		<view class="cu-modal" :class="modalName=='order_modal'?'show':''">
			<view class="cu-dialog" style="border-radius: 13px;">
				<view class="text-center mybg-green text-bold"
					style="height:30px;line-height: 46px;border-bottom:1px solid #80808052;height: 46px;">
					{{language.detail}}
				</view>

				<view class="mycolor-green text-bold"
					style="display: flex;flex-direction: row;justify-content: space-around;align-items: center;text-align: center;background-color: #F2F2F2;padding:8px">
					<view style="width: 10%;">No.</view>
					<view style="width: 25%;">2D/3D</view>
					<view style="width: 15%;">Odds</view>
					<view style="width: 25%;">Bet</view>
					<view style="width: 25%;">Bonus</view>
				</view>

				<scroll-view scroll-y class="bg-white order">
					<view
						:style="{'background-color':(index%2==0?'none':'#f5f5f5'),'color':order.IS_WIN == null ? 'black' : order.IS_WIN =='1' ? 'red':'green',}"
						style="display: flex;flex-direction: row;justify-content: space-around;align-items: center;text-align: center;padding:8px 0;"
						v-for="(order,index) in  orderDetails.orders" :key="index">
						<view style="width: 10%;">{{index + 1}}</view>
						<view style="width: 25%;">
							<view>{{order.BET_TYPE}}</view>
						</view>
						<view style="width: 15%;">{{order.BET_ODDS}}</view>

						<view style="width: 25%;">{{order.BET_MONEY}}</view>
						<view style="width: 25%;">{{order.IS_WIN == null ? 'Waiting':order.BONUS}}</view>

					</view>
				</scroll-view>


				<view class="flex flex-wrap grey">
					<view class="basis-sm  text-bold basis-df text-center">{{language.type}}</view>
					<view class="basis-xs basis-df text-center">{{orderDetails.detail.REMARK}}</view>
				</view>

				<view class="flex flex-wrap bg-white">
					<view class="basis-sm text-bold basis-df text-center">{{language.amount}}</view>
					<view class="basis-xs basis-df text-center">{{numberFormat(orderDetails.detail.BET_MONEY) }}</view>
				</view>

				<view class="flex flex-wrap grey">
					<view v-if="orderDetails.detail.STATUS=='1'" class="basis-sm  text-bold basis-df text-center">
						{{language.benefitMax}}
					</view>
					<view v-if="orderDetails.detail.STATUS=='0'" class="basis-sm  text-bold basis-df text-center">Bonus
					</view>
					<view v-if="orderDetails.detail.STATUS=='1'" class="basis-xs  basis-df text-center">
						{{numberFormat(orderDetails.benefit)}}
					</view>
					<view v-if="orderDetails.detail.STATUS=='0'"
						class="basis-xs text-red text-bold basis-df text-center">
						{{ numberFormat(orderDetails.detail.BONUS)}}
					</view>
				</view>
				<view class="text-center flex-column" style="border-radius: 0 0  13px 13px ;height: 46px;">
					<button class="cu-btn mybg-green" style="width: 20%;" @click="modalName = ''">confirm</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	import Vue from 'vue';
	import sTabs from '@/components/s-tabs/index.vue';
	import sTab from '@/components/s-tab/index.vue';
	import config from '../../utils/config.js';
	import dateFormatUtils from "../../utils/utils.js"
	import DatePicker from '../component/date-picker'

	const order_type ={
		digital_3d:9,
		digital_2d:8,
	}
	export default {
		name: 'orders',
		components: {
			sTabs,
			sTab,
			DatePicker
		},
		data() {
			return {
				listQuery: {
					date: '',
					navi2D3D: null,
					time: 0,
					start_time: '',
					end_time: '',
					// is_mix: 0
				},
				modalName: '',
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
				url_prefix: '',
				current: 0,
				currentList: [],
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
				language: config.language
			};
		},
		methods: {
			toHome() {
				uni.reLaunch({
					url: '/pages/index/index'
				})
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
						this.unordered = [];
						this.unorderedCurrentPage = 1;
						this.getUnorderedList();
						break
					case 1:
						this.activeTab = 1
						this.completed = [];
						this.completedCurrentPage = 1;
						this.getCompletedList();
						break
				}
			},
			DateChange(filter) {

				this.listQuery.start_time = filter.start_time.substring(0, 10);
				this.listQuery.end_time = filter.start_time.substring(0, 10);

				if (this.activeTab == 0) {
					this.unordered = [];
					this.unorderedCurrentPage = 1;
					this.getUnorderedList();
				} else {
					this.completed = [];
					this.completedCurrentPage = 1;
					this.getCompletedList();
				}
			},
			radioChange: function(evt) {
				for (let i = 0; i < this.items.length; i++) {
					if (this.items[i].value === evt.target.value) {
						this.current = i;
						break;
					}
				}
				this.current == 0 ? this.listQuery.is_mix = 0 : this.listQuery.is_mix = 1
				if (this.activeTab == 0) {
					this.unordered = [];
					this.unorderedCurrentPage = 1;
					this.getUnorderedList();
				} else {
					this.completed = [];
					this.completedCurrentPage = 1;
					this.getCompletedList();
				}
			},
			clickLoadMore(type) {
				if (type == 'completed') {
					this.completedCurrentPage++;
					this.getCompletedList();
				} else {
					this.unorderedCurrentPage++;
					this.getUnorderedList();
				}
			},
			getUnorderedList() {
				var _this = this;
				uni.showLoading({
					title: 'Loading!'
				})
				var paras = {
					page: _this.unorderedCurrentPage,
					limit: _this.limit,
					status: 1,
					start_time: _this.listQuery.time == 0 ? '' : _this.listQuery.time == 1 ? _this.getCurrentDate(7) :
						_this.getCurrentDate(
							30),
					end_time: _this.listQuery.time == 0 ? '' : _this.getCurrentDate(0),
					// is_mix: _this.listQuery.is_mix
					game_type: 2,
				};
				uni.showLoading({
					title: 'loading'
				})
				_this.$http.get(_this.url_prefix + "/order", {
					data: paras
				}, (res) => {
					uni.hideLoading()
					if (res.data.code == 20000) {
						var results = res.data.items;
						let total = 0
						uni.hideLoading();
						results.forEach(ele => {
							ele.BET_TYPE.length == 2 ? ele.ORDER_DESC = ele.ORDER_DESC.slice(-7) : ''
							let pad = ele.ORDER_TYPE == order_type.digital_3d ? 3 : 2;
							ele.BET_TYPE = String(ele.BET_TYPE).padStart(pad, '0')
							ele.REMARK = ele.ORDER_TYPE == order_type.digital_3d ?'3D':'2D';
							ele.CREATE_TIME = dateFormatUtils.formatTime(new Date(new Date(ele.CREATE_TIME)
								.valueOf() - 5400 * 1000))
							_this.unordered.push(ele);
						})

						if (results.length == 0) {
							uni.showToast({
								title: 'no more',
								icon: 'none'
							})
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
					start_time: _this.listQuery.time == 0 ? '' : _this.listQuery.time == 1 ? _this.getCurrentDate(7) :
						_this.getCurrentDate(
							30),
					end_time: _this.listQuery.time == 0 ? '' : _this.getCurrentDate(0),
					is_mix: _this.listQuery.is_mix,
					game_type: 2,
				};
				uni.showLoading({
					title: 'loading'
				})
				_this.$http.get(_this.url_prefix + "/order_history", {
					data: paras
				}, (res) => {
					uni.hideLoading()
					if (res.data.code == 20000) {
						var results = res.data.items;
						uni.hideLoading()
						results.forEach(ele => {
							ele.BET_TYPE.length == 2 ? ele.ORDER_DESC = ele.ORDER_DESC.slice(-7) : '';
							let pad = ele.ORDER_TYPE == order_type.digital_3d ? 3 : 2;
							ele.BET_TYPE = String(ele.BET_TYPE).padStart(pad, '0')
							ele.REMARK = ele.ORDER_TYPE == order_type.digital_3d ?'3D':'2D';
							ele.CREATE_TIME = dateFormatUtils.formatTime(new Date(new Date(ele.CREATE_TIME)
								.valueOf() - 5400 * 1000))
							_this.completed.push(ele);
						})

						if (results.length == 0) {
							uni.showToast({
								title: 'no more',
								icon: 'none'
							})
						}
					}
				})
			},
			showOrderDetails(row, type) {
				if (row.IS_MIX != '1') return;
				this.orderDetails.detail = Object.assign({}, row);
				uni.showLoading({
					title: 'loading'
				})
				var _this = this;
				var url = _this.url_prefix + (type == 0 ? '/order' : '/order_history');
				var paras = {
					order_id: row.ORDER_ID,
					game_type: 2,
					limit: 1000,
					is_detail: _this.orderDetails.detail.IS_MIX == '1' ? 1 : 0,
				};
				_this.$http.get(url, {
					data: paras
				}, (res) => {
					uni.hideLoading()
					if (res.data.code == 20000) {
						res.data.items.sort(function(a, b) {
							return parseInt(a.BET_TYPE) - parseInt(b.BET_TYPE)
						})
						_this.orderDetails.orders = res.data.items;
						let total = 0
						let bonus = 0
						let bet_money = 0
						_this.orderDetails.orders.forEach(ele => {
							ele.BONUS = ele.BONUS ? parseInt(ele.BONUS) : 0
							let pad = ele.ORDER_TYPE == order_type.digital_3d ? 3 : 2;
							ele.BET_TYPE = String(ele.BET_TYPE).padStart(pad, '0')
							total += parseInt(ele.BET_MONEY)
							bonus += ele.BONUS
							ele.CREATE_TIME = dateFormatUtils.formatTime(new Date(new Date(ele.CREATE_TIME)
								.valueOf() - 5400 * 1000))
							bet_money = ele.BET_MONEY > bet_money ? ele.BET_MONEY : bet_money
						})

						_this.orderDetails.benefit = bet_money * parseFloat(_this.orderDetails.orders[0].BET_ODDS)
						_this.orderDetails.detail.BET_MONEY = total
						_this.orderDetails.detail.BONUS = bonus
						_this.modalName = 'order_modal'
					}
					// console.log(_this.orderDetails)
				})

			}
		},
		created() {
			this.listQuery.date = dateFormatUtils.formatDate(new Date().getTime(), 'Y-M-D');

			// this.listQuery.start_time = this.listQuery.date;
			// this.listQuery.end_time = this.listQuery.date;

			let navi2D3D = uni.getStorageSync('navi2D3D');
			this.navi2D3D = navi2D3D
			this.url_prefix = navi2D3D == '2D' ? '/digital' : '/digital_3d';
			this.activeTab == 0 ? this.getUnorderedList() : this.getCompletedList();
		}
	}
</script>

<style>
	.popup {
		width: 90vw;
	}

	.amount-bar {
		height: 50px;
		position: fixed;
		width: 100%;
		bottom: 0;
		color: white;
	}

	.page {
		width: 100vw;
	}

	.team-name {
		text-align: center;
		width: 90px;
		word-wrap: break-word;
		word-break: break-all;
	}

	.active-tab {
		background-color: red;
		color: white;
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

	.unactive-tab {
		color: white;
		background-color: #555555;
	}

	.page.show {
		overflow: hidden;
	}

	.text-center {
		height: 32px;
		line-height: 32px;
	}

	.order {
		height: 50vh;
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
