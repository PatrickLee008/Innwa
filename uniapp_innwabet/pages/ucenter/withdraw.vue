<template>
	<view class="mybg-grey full-page">
		<!--  #ifdef APP-PLUS-->
		<cu-custom isBack="true" backUrl="/pages/ucenter/home">

			<block slot="content">{{language.withdraw}}
			</block>
		</cu-custom>
		<!-- #endif-->
		<!--  #ifdef  H5 -->
		<cu-custom isBack="true" backUrl="/pages/ucenter/home">
			<block slot="content">{{language.withdraw}}
			</block>
		</cu-custom>
		<!-- #endif-->

		<view class="cu-list menu">
			<view class="bar-row flex-row myrect box-shadow cu-item">
				<view class="flex-row content" style="text-align: left;">
					<view class="bar-icon">
						<image class="bar-icon-image" src="../../static/image/pocket.png"></image>
					</view>
					<text class="text-grey myfont-bold">{{language.withdraw_limit}}</text>
				</view>
				<view class="action">
					<text class="mycolor-red myfont-bold">{{configs.withdraw_min_limit}}</text>
				</view>
			</view>

			<view class="bar-row flex-column myrect box-shadow cu-item">
				<view class="flex-row content" style="text-align: left;line-height: 40px;">
					<view class="bar-icon">
						<image class="bar-icon-image" src="../../static/image/pocket.png"></image>
					</view>
					<text class="text-grey myfont-bold">{{language.withdraw_amount}}</text>
				</view>
				<view class="flex-row content-row myrect mybg-grey" style="width: 100%;padding: 0 15px 0 15px;">
					<view class="myfont-bold text-left">Money</view>
					<input class="text-bold mycolor-red" style="text-align: right;" type="number" @input='inputNum'
						v-model="amount" :placeholder="language.input_withdraw_amount"></input>
				</view>
			</view>


			<view class="bar-row flex-row myrect box-shadow cu-item">
				<view class="flex-row content" style="text-align: left;">
					<view class="bar-icon">
						<image class="bar-icon-image" src="../../static/image/pocket.png"></image>
					</view>
					<text class="text-grey myfont-bold">{{userInfo.TOTAL_MONEY}}</text>
				</view>
				<view class="action" @click="allWithdrawBtn()">
					<text class="mycolor-red myfont-bold">{{language.withdraw_all}}</text>
				</view>
			</view>
			<button class="my-button-orange" style="width: 70%;margin: 20px 15% 10px 15%;" @click="submit()">
				OK</button>
		</view>





		<uni-popup ref="popup" type="center">
			<view class="bg-white">
				<form>
					<view class="cu-form-group border-bottom">
						<view class="title">{{language.withdrawAmount}}</view>
						<input type="number" placeholder="" v-model="amount"></input>
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
	import Vue from "vue";


	export default {
		data() {
			return {
				index: -1,
				status: 'more',
				page: 1,
				limit: 15,
				picture: '',
				list: [],
				amount: 0,
				contentText: {
					contentdown: 'more',
					contentrefresh: 'loading',
					contentnomore: 'no more'
				},
				cartList: [],
				cartId: [],
				userInfo: null,
				configs: null,
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
			allWithdrawBtn() {
				let info = Object.assign({}, this.userInfo)
				Vue.set(this, 'amount', info.TOTAL_MONEY.replace(',', ''))
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
							// console.log(_this.list)
							_this.list.push(element);
						})
						if (results.length == 0) {
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
				this.page++;
				// this.getList();
			},
			add() {
				this.$refs.popup.open()
			},
			inputNum: function(evt) {
				let amount = evt.detail.value.replace('.', '')
				amount = amount ? parseInt(amount) : '0'
				this.$nextTick(function() {
					Vue.set(this, 'amount', amount)
				})
			},
			submit() {
				var _this = this;
				var para = {
					'MONEY': parseInt(_this.amount)
				}

				//判断提现金额是否为最小限额  ,如果未满足禁止体现
				if (_this.amount < parseInt(_this.$store.state.configs['withdraw_min_limit'])) {

					uni.showModal({
						title: 'tips',
						content: this.language.withdrawTips3 + _this.$store.state.configs['withdraw_min_limit'],
						showCancel: false,
						confirmText: 'ok',
						success: function(res) {}
					});

					return;
				}

				// if (_this.amount > parseInt(_this.$store.state.userInfo.TOTAL_MONEY.replace(',', ''))) {
				// 	uni.showModal({
				// 		title: 'tips',
				// 		content: this.language.withdrawTips2,
				// 		showCancel: false,
				// 		confirmText: 'ok',
				// 		success: function(res) {}
				// 	});
				// 	return;
				// }

				if (_this.amount < 0) {

					uni.showModal({
						title: 'tips',
						content: this.language.withdrawTips1,
						showCancel: false,
						confirmText: 'ok',
						success: function(res) {}
					});

					return;
				}
				uni.showLoading({
					title: 'Withdrawing!'
				})
				_this.$http.post('/withdraw/apply', para, (res) => {
					uni.hideLoading()
					if (res.data.code == 20000) {
						uni.showToast({
							title: 'withdraw success',
							icon: 'success',
							duration: 2000
						})

						var userInfo = _this.$store.state.userInfo

						userInfo.TOTAL_MONEY = String(parseInt(userInfo.TOTAL_MONEY.replace(',', '')) - parseInt(
							_this.amount));
						_this.userInfo = userInfo
						_this.$store.dispatch('saveUserInfo', userInfo);

						_this.page = 1;
						_this.list.length = 0;
						// _this.getList();
					} else {

						var tips = '';

						if (_this.language[res.data.message]) {
							//未达到最低提现额，则提示最低提现额额度 
							tips = res.data.code == 50003 ? _this.language[res.data.message] + "(" + this.$store
								.state.configs[res.data.message] + ")" : _this.language[res.data.message];
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
			// this.getList();
			this.getBankList()
			this.userInfo = Object.assign({}, this.$store.state.userInfo)
			this.configs = Object.assign({}, this.$store.state.configs)

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

	.submit {
		border-radius: 0;
	}

	.bg-green {
		background-color: rgb(185, 1, 0);
	}

	.input {
		background-color: lightgrey;
		height: 30px;
		border-radius: 4px;
		padding-left: 5px;
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

	.content-row {
		justify-content: space-around;
		line-height: 30px;
		margin: 5px 0 15px 0;
	}

	.content-row view {
		padding: 5px 0 5px 0;
	}

	.content-row view:first-child {
		width: 50%;
	}

	.content-row view:nth-child(2) {
		width: 50%;
	}
</style>
