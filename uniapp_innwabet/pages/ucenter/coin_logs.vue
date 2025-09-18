<template>
	<view>
		<!--  #ifdef APP-PLUS-->
		<cu-custom isBack="true">
			<block slot="backText">
				<!--
				<navigator url="/pages/index/index" navigateTo>
					<text style="margin-left:5px">〈 {{language.back}} </text> </navigator>
					-->
			</block>
			<block slot="content">Coin logs
			</block>
		</cu-custom>
		<!-- #endif-->

		<!--  #ifdef  H5 -->
		<cu-custom>
			<block slot="right">
				<view @click="toHome">
					<image style="width:25px;height: 25px;" src="../../static/icon/return.png"></image>
				</view>
			</block>
			<block slot="content">{{language.coin_log}}
			</block>
		</cu-custom>
		<!-- #endif-->

		<view style="height:38px;display: flex;flex-direction: row;justify-content: space-around;align-items: center;text-align: center;font-weight: bold;">
			<view style="width: 20%;">before</view>
			<view style="width: 20%;">change</view>
			<view style="width: 20%;">alfter</view>
			<view style="width: 20%;">operate</view>
			<view style="width: 20%;">time</view>
		</view>

		<scroll-view scroll-y class="page bg-white" style="height:calc(100vh - 45px - 38px);" @scrolltolower="clickLoadMore">
			<view :style="{'background-color':(index%2==0?'white':'#F2F2F2')}" style="display: flex;flex-direction: row;justify-content: space-around;align-items: center;text-align: center;padding:8px 0"
			 v-for="(element,index) in list">
				<view style="width: 20%;">{{numberFormat(element.AMOUNT)}}</view>
				<view style="width: 20%;" :style="{'color':(element.CHANGE_AMOUNT<0?'grey':'red')}">{{numberFormat(element.CHANGE_AMOUNT)}}</view>
				<view style="width: 20%;">{{numberFormat(element.BALANCE)}}</view>
				<view style="width: 20%;">{{type[element.TYPE]}}</view>
				<view style="width: 20%;">{{element.CREATE_TIME}}</view>
			</view>
		</scroll-view>

	</view>
</template>

<script>
	import uniPopup from "@/components/uni-popup/uni-popup.vue";
	import dateFormatUtils from "../../utils/utils.js"
	import config from '../../utils/config.js';



	export default {
		components: {
			uniPopup
		},
		data() {
			return {
				index: -1,
				status: 'more',
				page: 1,
				limit: 15,
				picture: '',
				list: [],
				money: 0,
				type: ['charge', 'withdraw', 'bet', 'settlement', 'cancel'],
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
			clickLoadMore() {
				this.page++;
				this.getList();
			},
			toHome() {
				uni.reLaunch({
					url: '/pages/ucenter/home'
				})
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
				_this.$http.get('/app_operation/get', {
					data: para
				}, (res) => {
					if (res.data.code == 20000) {
						uni.hideLoading();
						var results = res.data.items;
						results.forEach(element => {
							element.CHANGE_AMOUNT = parseInt(element.BALANCE) - parseInt(element.AMOUNT);
							_this.list.push(element);
						})
						if (results.length == 0) {
							uni.showToast({
								'title': 'no more',
								'icon':'none'
							})
						}
					}
				})
			},
			clickLoadMore() {
				this.page++;
				this.getList();
			},

		},
		onLoad() {
			this.getList();
		}
	}
</script>

<style>
	.action {
		width: 100px !important;
	}


	input {
		background-color: lightgrey;
		height: 30px;
		border-radius: 4px;
		padding-left: 5px;
	}

	.content {
		left: 10px !important;
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
