<template>
	<view style="height: 100vh;">
		<cu-custom bgColor="bg-purple" isBack="true">
			<block slot="content">Charge Record</block>
		</cu-custom>

		<view class="padding-xs"></view>

		<!-- 充值记录 -->
		<scroll-view scroll-y style="height: calc(100vh - 80px);">
			<view class="cu-list menu-avatar">
				<view class="cu-item margin-bottom-xs "
					style="position:relative;background-size: 100% 100%;width: 93vw;margin-left: 3.5vw;height: 180px;"
					:style="{'background-image':element.CUSTOMER_BANK_CODE=='KBZ'?'url(/static/image/charge/kbz_record_bg.png)':'url(/static/image/charge/wave_record_bg.png)'}"
					v-for="(element,index) in list" @click="setCurrentAccount(element)">
					<!-- <view class="cu-avatar lg radius-6px" :style="'background-image:url('+element.PICTURE+');'"></view> -->

					<view class="text-white flex-row justify-start " style="position: absolute;top:18px;left:18px;">
						<image src="/static/image/charge/rili.png" style="width: 12px;height: 12px;"></image>
						<text class="margin-left-xs">{{element.CREATE_TIME}}</text>
					</view>

					<view class="cu-avatar lg radius-6px bg-img margin-left-xs"
						v-if="element.CUSTOMER_BANK_CODE == 'KBZ'"
						style="background-image: url('../../static/image/charge/2.png');height: 60px;width:60px;background-color: white">
					</view>

					<view class="cu-avatar lg radius-6px bg-img margin-left-xs" v-else
						style="background-image: url('../../static/image/charge/1.png');height: 60px;width:60px;background-color: white">
					</view>

					<view class="content margin-left">
						<view class="mycolor-deepgreen cuIcon-myfill"><text class="mycolor-deepgreen "
								style="padding-left:3px;">{{element.NICK_NAME}}</text></view>
						<view class="text-red cuIcon-moneybagfill"><text class="text-red "
								style="padding-left:3px;">{{element.AMOUNT}}</text></view>
						<!-- 	<view class="text-gray text-sm flex">
							<view class="text-cut">
								<text class="mycolor-deepgreen margin-right-xs"></text>
								{{element.REASON}}
							</view>
						</view> -->
					</view>
					<view class="action margin-right" style="width: 100px;">
						<view class="action" style="width: 100px;">
							<view v-if="element.STATUS == '0'" class="cu-tag radius bg-grey sm">
								{{language.chargeWaiting}}
							</view>
							<view v-if="element.STATUS == '1'" class="cu-tag radius bg-red sm ">
								{{language.chargeSuccess}}
							</view>
							<view v-if="element.STATUS == '2'" class="cu-tag radius bg-red sm">{{language.chargeFail}}
							</view>
						</view>
					</view>

					<view class="text-white flex-row justify-start margin-left-xs"
						style="position: absolute;bottom:25px;left:18px;width:86%;height:35px;background-size: 100% 100%;"
						:style="{'background-image':element.CUSTOMER_BANK_CODE=='KBZ'?'url(/static/image/charge/kbz_record_bottom.png)':'url(/static/image/charge/wave_record_bottom.png)'}">
						<text class="padding-left-xs text-black " style="margin-top: 3px;">Receiver Bank：&nbsp;&nbsp;{{element.RECEIVER_BANK_ACCOUNT}}</text>
					</view>

				</view>
			</view>
			<uni-load-more :status="status" :content-text="contentText" @clickLoadMore="clickLoadMore" />
		</scroll-view>

		<!-- <image @click="add" src="../../static/image/charge/add.png" class="add" mode="widthFix" style=""></image> -->
		<!-- 账单详情 -->
		<uni-popup ref="popup" type="center">
			<view class="bg-white" style="border-radius: 10px;width: 88vw;">
				<form>
					<view class="padding" v-if="currentAccount">
						<view class=" flex-row justify-start align-start padding-xs "
							style="border:1px solid grey;border-radius: 8px;">
							<view style="width: 68px;height:68px;">

								<image src="../../static/image/charge/1mini.png" mode="widthFix"
									v-if="currentAccount.CUSTOMER_BANK_CODE == 'WaveMoney'"></image>
								<image src="../../static/image/charge/2mini.png" mode="widthFix"
									v-if="currentAccount.CUSTOMER_BANK_CODE == 'KBZ'"></image>
								<!-- <image src="../../static/image/charge/1mini.png" mode="widthFix"></image> -->

							</view>
							<view class="flex-column margin-left-xs" style="align-items: flex-start;">
								<view style="">{{currentAccount.NICK_NAME}}</view>
								<view class="text-bold margin-tb-xs myfont-17px ">
									{{currentAccount.CUSTOMER_BANK_ACCOUNT}}
								</view>
							</view>
						</view>
					</view>

					<view v-if="currentAccount">
						<view class=" margin-bottom-xs padding-lr padding-tb-sm" style="">
							<view class="content flex-row justify-between">
								<view class=" ">
									<text class=" text-bold" style="padding-left:3px;">Transaction ID</text>
								</view>
								<view class=" ">
									<text class=" text-bold" style="padding-left:3px;">Amount</text>
								</view>
							</view>
							<view class=" flex-row justify-between margin-tb-xs">
								<view class="mycolor-deepgreen cuIcon-myfill">
									<text class="mycolor-deepgreen "
										style="padding-left:3px;">{{currentAccount.TRANSACTION_ID}}</text>
								</view>
								<view class="mycolor-deepgreen cuIcon-moneybagfill">
									<text class="mycolor-deepgreen "
										style="padding-left:3px;">{{currentAccount.AMOUNT}}</text>
								</view>
							</view>
						</view>
					</view>

					<!-- <view class="title margin-left text-bold  myfont-17px">Transaction Id </view>
					<view class="bg-img myrect flex-row justify-between "
						style="background-image: url(../../static/image/charge/input.png);height: 55px;">
						<view style="margin-left: 5%;" v-if="currentAccount">{{currentAccount.ID}}</view>
					</view> -->
					<!-- <view class="title margin-left text-bold padding-top-sm ">{{language.amount}}</view>
					<view class="bg-img myrect"
						style="background-image: url(../../static/image/charge/input.png);height: 55px;">
						<view class="myrect"
							style="margin-left: 5%;margin-top: 5%;" v-if="currentAccount">{{currentAccount.MONEY}}</view>
					</view> -->
					<view class="title margin-left text-bold  myfont-17px">Transaction Name </view>
					<view class="bg-img myrect flex-row justify-between "
						style="background-image: url(../../static/image/charge/input.png);height: 55px;">
						<view style="margin-left: 5%;" v-if="currentAccount">{{currentAccount.NICK_NAME}}</view>
					</view>

					<view class="title margin-left text-bold padding-top-sm ">Time</view>
					<view class="bg-img myrect"
						style="background-image: url(../../static/image/charge/input.png);height: 55px;">
						<view class="myrect" style="margin-left: 5%;margin-top: 5%;" v-if="currentAccount">
							{{currentAccount.CREATE_TIME}}
						</view>
					</view>

					<view class="padding margin-top-sm" style="padding-top:0">
						<view class="title text-bold  margin-bottom-xs myfont-17px">Screenshot Record</view>
						<view style="border:1px solid grey;border-radius: 8px;">
							<view class="flex-row myfont-17px">
								<view class="bg-img myrect1 flex-row justify-between">
									<view class="bg-img padding-sm" @tap="ViewImage" :data-url="picture"
										style="text-align: center;position: relative;">
										<image :src="picture" mode="aspectFill"
											style="width:80px;height:80px;border:1px dashed grey"></image>

										<!-- <view class="cu-tag bg-red" @tap.stop="DelImg"
											style="position: absolute;top:10px;height:18px;width:18px">
											<text class='cuIcon-close'></text>
										</view> -->
									</view>
									<view class="flex-column">
										<view></view>
									</view>
								</view>
							</view>
						</view>
					</view>

					<!-- <button class="bg-purple margin-top-sm submit"></button> -->

					<view class="padding-xs"></view>
				</form>
			</view>
		</uni-popup>

	</view>
</template>

<script>
	import uniLoadMore from "@/components/uni-load-more/uni-load-more.vue";
	import uniPopup from "@/components/uni-popup/uni-popup.vue";
	import config from '../../utils/config.js'
	// import ClipboardJS from '../../utils/clipboard.min.js';

	export default {
		components: {
			uniLoadMore,
			uniPopup
		},
		data() {
			return {
				status: 'more',
				page: 1,
				limit: 15,
				picture: '',
				list_end: false,
				language: config.language,
				list: [],
				currentAccount: null,
				trade_list: [],
				modalName: '',
				language_list: ['myan', 'en'],
				lang_index: uni.getStorageSync('lang_index') || 0,
				lang_select: uni.getStorageSync('lang_select') || config.language.lang,
				bank_card: 'bank card',
				bank_code: uni.getStorageSync('bank_code') || 'KBZ',
				first_in: uni.getStorageSync('first_in') || true,
				money: 0,
				bank_code_list: [
					'KBZ',
					'WaveMoney',
				],
				bankAccountList: [],
				chargeForm: {
					amount: 0,
					transaction_id: ''
				},
				contentText: {
					contentdown: 'more',
					contentrefresh: 'loading',
					contentnomore: 'no more'
				},
				lastOperate: null,
				imgList: [],
			}
		},

		mounted() {
			// 初始化Clipboard实例
			// this.clipboard = new ClipboardJS('.copy-button');

			// // 监听复制成功事件
			// this.clipboard.on('success', () => {
			// 	uni.showToast({
			// 		title: 'copy success'
			// 	})
			// });

			// // 监听复制失败事件
			// this.clipboard.on('error', () => {
			// 	uni.showToast({
			// 		title: 'copy error'
			// 	})
			// });
		},
		destroyed() {
			// 销毁Clipboard实例
			// if (this.clipboard) {
			// 	this.clipboard.destroy();
			// }
		},

		methods: {
			setCurrentAccount(item) {
				this.modalName = '';
				this.currentAccount = item;
				console.log(this.currentAccount)
				this.picture = item.PICTURE;
				this.$refs.popup.open()
			},
			clickToFast() {
				var result = false;
				let _this = this
				var now = new Date().getTime();
				if (_this.lastOperate != null) {
					var second = now - _this.lastOperate;
					if (second / 1000 < 3) {
						uni.showToast({
							title: 'requests are too frequent',
							icon: 'none',
						})
						result = true;;
					}
				}
				_this.lastOperate = now
				return result;
			},
			getList() {
				var _this = this;
				var para = {
					page: _this.page,
					limit: _this.limit
				}
				uni.showLoading({
					title: 'Loading...'
				})
				_this.$http.get('/charge/get', {
					data: para
				}, (res) => {

					uni.hideLoading()
					if (res.data.code == 20000) {
						var results = res.data.items;
						results.forEach(element => {
							element.CREATE_TIME = element.CREATE_TIME.substring(0, 16);
							element.PICTURE = _this.$http.baseUrl + '/static/img/charge_pics/' + element
								.PICTURE
							console.log(element.PICTURE);
							_this.list.push(element);
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
			// getBankList() {
			// 	var _this = this;
			// 	var para = {
			// 		bank_code: _this.bank_code,
			// 	}

			// 	_this.bankAccountList.length = 0
			// 	_this.$http.get('/charge/active_bankcard', {
			// 		data: para
			// 	}, (res) => {

			// 		if (res.data.code == 20000) {
			// 			uni.setStorageSync('bank_code', _this.bank_code)
			// 			_this.bankAccountList = res.data.items;

			// 		} else {
			// 			_this.bank_card = res.data.message
			// 		}
			// 	})
			// },
			clickLoadMore() {
				if (this.list_end) {
					return
				}
				this.page++;
				this.getList();
			},

			ViewImage() {
				if (!this.picture) {
					return; // 如果没有选择图片或图片为空，则不执行预览操作
				}
				uni.previewImage({
					urls: [this.picture],
					current: this.picture // 保持不变，当前预览图片URL
				});
			},
		},
		onLoad() {
			// this.clipboard = new ClipboardJS('.copy-btn');
			this.getList();
			// this.getBankList()
		}
	}
</script>

<style>
	.myrect {
		width: 90%;
		margin-left: 5%;
		margin-top: 10px;
		border-radius: 13px;
	}

	.myrect1 {
		width: 44%;
		margin-left: 4%;
		margin-top: 10px;
		border-radius: 13px;
	}

	.add {
		position: fixed;
		bottom: 5vh;
		margin-left: calc(50vw - 7.5vw);
		width: 15vw;

	}
</style>
