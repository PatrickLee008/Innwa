<template>
	<view class="mybg-grey full-page">
		<!--  #ifdef APP-PLUS-->
		<cu-custom isBack="true" backUrl="/pages/ucenter/home">

			<block slot="content">{{language.withdraw_history}}
			</block>
		</cu-custom>
		<!-- #endif-->
		<!--  #ifdef  H5 -->
		<cu-custom isBack="true" backUrl="/pages/ucenter/home">
			<block slot="content">{{language.withdraw_history}}
			</block>
		</cu-custom>
		<!-- #endif-->


		<scroll-view scroll-y class="page " style="height:calc(100vh - 90px);" @scrolltolower="clickLoadMore">
			<view class="myrect box-shadow flex-column bg-white" style="width: 90vw;justify-content: flex-start;">
				<view class="flex-row" style="margin-top: 9px;padding: 2vw;">
					<view class="mybg-red" style="width: 3px;border-radius: 9px;height: 13px;margin: 0 5px 0;"></view>
					<view class="myfont-bold">{{language.withdraw_total}}:{{total_withdraw}}</view>
				</view>
				<view v-for="(element,index) in list" :keys='element.WITHDRAWAL_ID'>
					<view class="mybg-grey" style="width: 90vw;height: 2px;"></view>
					<view class="flex-column">
						<view class="flex-row myfont-bold content-row"
							style="justify-content: space-around;width: 90%;">
							<view>
								{{element.IS_PAY=='0'?language.have_not_transfer:element.IS_PAY=='1'?'paid':element.IS_PAY=='2'?'reject':'unknow'}}
							</view>
							<view>{{language.withdraw_code}}</view>
							<view>{{language.withdraw_history_amount}}</view>
						</view>
						<view class="content-row2 flex-row content-row myrect mybg-grey" style="width: 95%;">
							<view style="margin-left: 2px;">{{element.CREATE_TIME}}</view>
							<view>
								<text class="myfont-bold"
									:style="'color:' + element.color">{{element.Work_Group + '-'}}</text>
								<text>{{element.WITHDRAWAL_CODE}}</text>
							</view>
							<view>{{numberFormat(element.MONEY)}}</view>
						</view>
					</view>
				</view>
			</view>
			<!-- <view class="cu-item  padding-sm" v-for="(element,index) in list" :keys='element.WITHDRAWAL_ID'
			 :style="{'background-color':(index%2==0?'white':'#F2F2F2')}">
				<view class="content-row">
					<view>{{element.IS_PAY=='0'?language.have_not_transfer:element.IS_PAY=='1'?'paid':element.IS_PAY=='2'?'reject':'unknow'}}</view>
					<view>{{language.withdraw_code}}</view>
					<view>{{language.withdraw_history_amount}}</view>
				</view>
				<view class="content-row">
					<view>{{element.CREATE_TIME}}</view>
					<view>
						<text :style="'color:' + element.color">{{element.Work_Group}}</text>
						<text>{{'-' + element.WITHDRAWAL_CODE}}</text>
					</view>
					<view>{{numberFormat(element.MONEY)}}</view>
				</view>
			</view> -->
		</scroll-view>

		<!-- <image @click="add" src="../../static/icon/add.png" class="add"></image> -->

		<uni-popup ref="popup" type="center">
			<view class="bg-white">
				<form>
					<view class="cu-form-group border-bottom">
						<view class="title">{{language.withdrawAmount}}</view>
						<input type="number" placeholder="" v-model="money"></input>
					</view>
					<button @click="$noMultipleClicks(submit)" class="bg-green margin-top-sm submit">Yes</button>
				</form>
			</view>
		</uni-popup>
	</view>
</template>

<script>
	import config from '../../utils/config.js';
	import dateFormatUtils from "../../utils/utils.js"


	export default {
		data() {
			return {
				index: -1,
				status: 'more',
				page: 1,
				list_end: false,
				limit: 15,
				picture: '',
				list: [],
				total_withdraw: '',
				money: 0,
				contentText: {
					contentdown: 'more',
					contentrefresh: 'loading',
					contentnomore: 'no more'
				},
				cartList: [],
				cartId: [],
				language: config.language
			}
		},
		methods: {
			toHome() {
				uni.reLaunch({
					url: '/pages/ucenter/home'
				})
			},
			clickLoadMore() {
				this.page++;
				this.getList();
			},
			PickerChange(e) {
				this.index = e.detail.value
			},
			numberFormat(number) {
				return dateFormatUtils.numFormat(number);
			},
			getList() {
				var _this = this;
				var para = {
					page: _this.page,
					limit: _this.limit
				}
				uni.showLoading({
					'title': 'loading'
				})
				_this.list = []
				_this.$http.get('/withdraw/get', {
					data: para
				}, (res) => {
					if (res.data.code == 20000) {
						uni.hideLoading();
						var results = res.data.items;
						_this.total_withdraw = parseInt(res.data.total_amount)
						results.forEach(element => {
							element.CREATE_TIME = element.CREATE_TIME.substring(0, 16);
							switch (element.Work_Group) {
								case 'A':
									element.color = 'red'
									break;
								case 'B':
									element.color = 'blue'
									break;
								case 'C':
									element.color = 'green'
									break;

							}
							console.log(_this.list)
							_this.list.push(element);
						})
						if (results.length == 0) {
							_this.list_end = true
							uni.showToast({
								'title': 'no more',
								'icon': 'none'
							})
						}
					}
				})
			},
			getBankList() {
				var _this = this;
				_this.$http.get('/bank_card/get', {}, (res) => {
					if (res.data.code == 20000) {
						var results = res.data.bank_cards;
						_this.cartList.length = 0;
						results.forEach(element => {
							var temp = element.BANK_TYPE + '->' + element.CARD_NUM;
							_this.cartList.push(temp);
							_this.cartId.push(element.ID);
						})
					}
				})
			},
			clickLoadMore() {
				if (this.list_end) {
					return
				}
				this.page++;
				this.getList();
			},
			add() {
				this.$refs.popup.open()
			},
			submit() {
				var _this = this;
				var para = {
					'MONEY': _this.money
				}

				//判断提现金额是否为最小限额  ,如果未满足禁止体现
				if (_this.money < parseInt(_this.$store.state.configs['withdraw_min_limit'])) {

					uni.showModal({
						title: 'tips',
						content: this.language.withdrawTips3 + _this.$store.state.configs['withdraw_min_limit'],
						showCancel: false,
						confirmText: 'ok',
						success: function(res) {}
					});

					return;
				}

				if (_this.money > parseInt(_this.$store.state.userInfo.TOTAL_MONEY.replace(',', ''))) {

					uni.showModal({
						title: 'tips',
						content: this.language.withdrawTips2,
						showCancel: false,
						confirmText: 'ok',
						success: function(res) {}
					});

					return;
				}

				if (_this.money < 0) {

					uni.showModal({
						title: 'tips',
						content: this.language.withdrawTips1,
						showCancel: false,
						confirmText: 'ok',
						success: function(res) {}
					});

					return;
				}
				_this.$http.post('/withdraw/apply', para, (res) => {
					if (res.data.code == 20000) {
						uni.showToast({
							title: 'withdraw success',
							icon: 'success',
							duration: 2000
						})

						var userInfo = _this.$store.state.userInfo

						userInfo.TOTAL_MONEY = parseInt(userInfo.TOTAL_MONEY) - parseInt(_this.money);
						_this.$store.dispatch('saveUserInfo', userInfo);

						_this.page = 1;
						_this.list.length = 0;
						_this.getList();
					} else {

						var tips = '';
						if (_this.language[res.data.message]) {
							tips = _this.language[res.data.message] + "(" + this.$store.state.configs[res.data
								.message] + ")";
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
					this.$refs.popup.close()
				})
			}
		},
		onLoad() {
			this.getList();
			this.getBankList()
		}
	}
</script>

<style>
	.action {
		width: 100px !important;
	}

	.submit {
		border-radius: 0;
	}

	.bg-green {
		background-color: rgb(185, 1, 0);
	}

	input {
		background-color: lightgrey;
		height: 30px;
		border-radius: 4px;
		padding-left: 5px;
	}

	.content-row2 {
		justify-content: space-around;
		line-height: 30px;
		margin: 5px 0 15px 0;
		/* font-weight: 550; */
	}

	.content {
		left: 10px !important;
	}

	.content-row {
		width: 90vw;
	}

	.content-row view {
		padding: 5px 0 5px 0;
	}

	.content-row view:first-child {
		width: 40%;
	}

	.content-row view:nth-child(2) {
		width: 30%;
	}

	.content-row view:nth-child(3) {
		width: 30%;
	}

	.add {
		position: fixed;
		height: 20vw;
		width: 20vw;
		bottom: 2px;
		left: 40vw;
	}

	.border-bottom {
		border: 1px solid lightgrey;
	}
</style>
