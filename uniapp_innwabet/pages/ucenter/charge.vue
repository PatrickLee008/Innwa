<template>
	<view
		style="background-image: url(../../static/image/charge/bg.png);background-position: center bottom;background-size:70%;background-repeat: no-repeat;height:100vh">
		<cu-custom bgColor="bg-purple" isBack="true">
			<block slot="content">{{language.userCharge}}</block>
		</cu-custom>

		<view class="padding-xs"></view>
		<!-- 银行卡示例 -->

		<view class=" flex-row margin-top-sm"
			style="border-radius: 12px;background-repeat:no-repeat;background-size:100% 100%;background-image: url('../../static/image/charge/bank_wave.png') ;background-position:center center; height: 15vh;width: 93vw;margin-left: 3.5vw;"
			@click="selectBank('WaveMoney')">
			<view style="margin-left: 15px">
				<image src="../../static/image/charge/1.png" mode="widthFix"
					style="width: 75px;margin-right: 13px;margin-top: 5px;">
				</image>
			</view>

			<view class="flex-column" style="margin-left: 5px;align-items: flex-start;">
				<view class="flex-row">
					<text class="myfont-bold" style="color: white; font-size: 20px;">Wave money</text>
				</view>
			</view>
			<view class="cu-tag line-white radius" style="margin: 6vh 2vw 0 0;">{{language.detail}}</view>
		</view>

		<view class="padding-top-sm"></view>

		<view class=" flex-row margin-top-sm"
			style="border-radius: 12px;background-repeat:no-repeat;background-size:100% 100%;background-image: url('../../static/image/charge/bank_kbz.png') ;background-position:center center; height: 15vh;width: 93vw;margin-left: 3.5vw;"
			@click="selectBank('KBZ')">
			<view style="margin-left: 15px">
				<image src="../../static/image/charge/2.png" mode="widthFix"
					style="width: 75px;margin-right: 13px;margin-top: 5px;">
				</image>
			</view>

			<view class="flex-column" style="margin-left: 5px;align-items: flex-start;">
				<view class="flex-row">
					<text class="myfont-bold" style="color: white; font-size: 20px;">KBZ Pay</text>
				</view>
			</view>
			<view class="cu-tag line-white " style="margin: 6vh 2vw 0 0;">{{language.detail}}</view>
		</view>

	<!-- 	<view class=" flex-row margin-top-sm"
			style="border-radius: 12px;background-repeat:no-repeat;background-size:100% 100%;background-image: url('../../static/image/charge/bank_kbz.png') ;background-position:center center; height: 15vh;width: 93vw;margin-left: 3.5vw;"
			@click="modalName = 'kbz_auto_modal'">
			<view style="margin-left: 15px">
				<image src="../../static/image/charge/2.png" mode="widthFix"
					style="width: 75px;margin-right: 13px;margin-top: 5px;">
				</image>
			</view>

			<view class="flex-column" style="margin-left: 5px;align-items: flex-start;">
				<view class="flex-row">
					<text class="myfont-bold" style="color: white; font-size: 20px;">KBZ Pay Auto</text>
				</view>
			</view>
			<view class="cu-tag line-white " style="margin: 6vh 2vw 0 0;">{{language.detail}}</view>
		</view> -->

		<!-- 

		<view class="flex-row justify-center" style="position:fixed;bottom:180px">
			<image src="" mode="aspectFit"></image>
		</view> -->


		<view class="flex-row justify-center" style="margin-top:60px;">
			<image src="../../static/image/charge/charge_tips.png" mode="aspectFit" style="width: 90%;"></image>
		</view>


		<!-- 自动充值 -->
		<view class="cu-modal" :class="modalName=='kbz_auto_modal'?'show':''">
			<view class="cu-dialog" style="border-radius: 12px;">
				<view class="cu-bar bg-white justify-end">
					<view class="content text-bold">KBZ Info</view>
					<view class="action" @tap="modalName = ''">
						<text class="cuIcon-close text-grey"></text>
					</view>
				</view>
				<form>
					<view class="padding">
						<view class=" flex-row justify-start align-start padding "
							style="background-image: url('/static/image/charge/account_bg.png');background-size: 100% 100%;">
							<view style="width: 48px;height:48px;">
								<image src="../../static/image/charge/2mini.png" mode="widthFix" />
							</view>
							<view class="flex-column margin-left-xs" style="align-items: flex-start;">
								<view style="">{{'KBZ Auto'}}</view>
								<view class="text-bold margin-tb-xs myfont-17px ">
									{{'target account'}}
								</view>
							</view>
						</view>
					</view>

					<view class="bg-img myrect  flex-row justify-between"
						style="background-image: url(../../static/image/charge/input.png);border-bottom: 1px solid lightgrey;border-radius: 0">
						<view class="width-25 text-left">Amount</view>
					<!-- 	<image src="/static/image/charge/charge_amount.png" mode="aspectFit" style="width: 68px;">
						</image> -->
						<input class="width-75 text-left" :placeholder="language.amount" type="number" v-model="kbz_auto_config.amount"
							style="padding-left: 12px;"></input>
					</view>

					<view class="bg-img myrect  flex-row justify-between"
						style="background-image: url(../../static/image/charge/input.png);border-bottom: 1px solid lightgrey;border-radius: 0">
						<!-- <image src="/static/image/charge/charge_amount.png" mode="aspectFit" style="width: 68px;">
						</image> -->
						<view class="width-25 text-left">UserName</view>
						<input class="width-75 text-left" placeholder="language.realname" v-model="kbz_auto_config.realname"
							style="padding-left: 12px;"></input>
					</view>

					<view class="bg-img myrect  flex-row justify-between"
						style="background-image: url(../../static/image/charge/input.png);border-bottom: 1px solid lightgrey;border-radius: 0">
					<!-- 	<image src="/static/image/charge/charge_amount.png" mode="aspectFit" style="width: 68px;">
						</image> -->
						<view class="width-25 text-left">Phone</view>
						<input class="width-75 text-left" placeholder="language.phone" type="number" v-model="kbz_auto_config.phone"
							style="padding-left: 12px;"></input>
					</view>

					<!-- <button class="bg-purple margin-top-sm submit"></button> -->
					<button @click="kbz_auto_submit()" class="bg-red text-white "
						style="border-radius: 32px;height: 50px;margin:30px 20px">Confirm</button>
					<view class="padding-xs"></view>
				</form>
			</view>
		</view>


		<!-- 银行选择 -->
		<view class="cu-modal" :class="modalName=='select_modal'?'show':''">
			<view class="cu-dialog" style="border-radius: 12px;">
				<view class="cu-bar bg-white justify-end">
					<view class="content text-bold">Bank Account Select</view>
					<view class="action" @tap="modalName = ''">
						<text class="cuIcon-close text-grey"></text>
					</view>
				</view>
				<view class="">
					<view class="">
						<!-- <view class="flex-row margin-tb justify-between padding-lr" v-for="i in bank_code_list"
							@click="select_bank_code(i)">
							<view class="text-bold text-grey">{{i}}</view>
							<view class="">
								<view class="cuIcon-check text-green"
									:style="{visibility: bank_code===i?'':'hidden'}" />
							</view>
						</view>
						<view class="flex-row  align-center bg-white padding-lr padding-tb-sm mybg-lightgreen">
							<view class="myfont-17px" style="">Account：</view>
							<view class="mycolor-deepgreen" style="font-size: 20px;">{{bankAccountList.length}}</view>
						</view> -->
						<view class=" text-center">
							<!-- <view class="flex-row justify-between align-center bg-white text-bold padding">
								<view style="width: 30%;">name</view>
								<view style="width: 50%;">account</view>
								<view style="width: 20%;"></view>
							</view> -->

							<view class="flex-row justify-between align-center bg-white padding-xs"
								style="border-top:1px dashed grey" v-for="(item,index) in bankAccountList">
								<view class="flex-row justify-start align-start">
									<!-- <view style="">{{item.BANK_CODE}}</view> -->
									<view style="width: 58px;height:58px;">
										<image src="../../static/image/charge/1mini.png" mode="widthFix"
											v-if="item.BANK_CODE == 'WaveMoney'"></image>
										<image src="../../static/image/charge/2mini.png" mode="widthFix"
											v-if="item.BANK_CODE == 'KBZ'"></image>
									</view>
									<view class="flex-column margin-left-xs" style="align-items: flex-start;">
										<view style="">{{item.NAME}}</view>
										<view class="text-bold margin-tb-xs myfont-17px ">
											{{item.ACCOUNT.match(/.{1,4}/g).join(' ')}}
										</view>
									</view>

								</view>

								<!-- <button style="width: 100rpx;height: 31px;" class="cu-btn mybg-deepgreen text-white "
									@click="setCurrentAccount(item)" :data-clipboard-text="item.ACCOUNT">Copy</button> -->

								<button style="width: 100rpx;height: 31px;" class="cu-btn bg-red text-white "
									@click="copyBankCode(item)">Copy</button>


								<!-- 				<button style="width: 100rpx;height: 31px;" class="cu-btn mybg-deepgreen text-white "
										@click="copyBankCode(item)" :data-clipboard-text="item.ACCOUNT">Copy</button> -->


							</view>
						</view>
					</view>
				</view>
			</view>
		</view>

		<!-- 上传账单 -->
		<uni-popup ref="popup" type="center">
			<view class="bg-white" style="border-radius: 10px;width: 88vw;">
				<form>
					<view class="padding" v-if="currentAccount">
						<view class=" flex-row justify-start align-start padding "
							style="background-image: url('/static/image/charge/account_bg.png');background-size: 100% 100%;">
							<view style="width: 48px;height:48px;">
								<image src="../../static/image/charge/1mini.png" mode="widthFix"
									v-if="currentAccount.BANK_CODE == 'WaveMoney'"></image>
								<image src="../../static/image/charge/2mini.png" mode="widthFix"
									v-if="currentAccount.BANK_CODE == 'KBZ'"></image>
							</view>
							<view class="flex-column margin-left-xs" style="align-items: flex-start;">
								<view style="">{{currentAccount.NAME}}</view>
								<view class="text-bold margin-tb-xs myfont-17px ">
									{{currentAccount.ACCOUNT.match(/.{1,4}/g).join(' ')}}
								</view>
							</view>
						</view>
					</view>

					<!-- <view class="padding" style="padding-top:0" v-if="bank_code == 'KBZ'">

						<view class="title text-bold  margin-bottom-xs myfont-17px">Screenshot Upload</view>


						<view class="flex-row myfont-17px">

							<view class="bg-img myrect1 flex-row justify-between">


								<view class="bg-img padding-sm" @tap="ViewImage" :data-url="picture"
									style="text-align: center;position: relative;">
									<image :src="picture" mode="aspectFill"
										style="width:80px;height:80px;border:1px dashed lightgrey;border-radius: 12px;background-color: #F2F2F2;">
									</image>

									<view class="cu-tag bg-red" @tap.stop="DelImg"
										style="position: absolute;top:10px;height:18px;width:18px">
										<text class='cuIcon-close'></text>
									</view>
								</view>

							</view>

							<view class="bg-img myrect1 flex-row justify-between">
								<button class="cu-btn bg-red text-white " @tap="ChooseImage">Upload</button>
							</view>

						</view>



					</view> -->

					<!-- <scroll-view style="max-height: 40vh;" scroll-y>
						<checkbox-group>
							<view class="cu-form-group border-bottom flex-row text-center"
								v-for="(trade,index) in trade_list" @click="checkboxChange(trade)">
								<view class="width-60">{{trade.transaction_id}}</view>
								<view class="width-40">{{trade.amount}}</view>
								<view class="width-10">
									<image class="league-image" v-show="trade.checked"
										src="../../static/icon/checked.png"></image>
									<image class="league-image" v-show="!trade.checked"
										src="../../static/icon/unchecked.png"></image>
								</view>
							</view>
						</checkbox-group>
					</scroll-view> -->
					<!-- 选择语言 -->






					<view class="bg-img myrect flex-row justify-between"
						style="background-image: url(../../static/image/charge/input.png);height: 55px;">
						<image src="/static/image/charge/transaction_id.png" mode="aspectFit" style="width: 68px;">
						</image>
						<input placeholder="Transaction Id" type="number" v-model="chargeForm.transaction_id"
							style="width: 100%;padding-left: 12px;"></input>
					</view>

					<scroll-view scroll-y style="max-height: 40vh;">
						<view class=" ">
							<view class=" margin-bottom-xs padding-lr-lg padding-tb-sm" style=""
								v-for="(trade,index) in trade_list" @click="checkboxChange(trade)">
								<view class="content flex-row justify-between">
									<view class=" ">
										<text class="mycolor-deepgreen text-bold"
											style="padding-left:3px;">transaction_id</text>
									</view>
									<view class=" ">
										<text class="mycolor-deepgreen text-bold"
											style="padding-left:3px;">amount</text>
									</view>
								</view>
								<view class=" flex-row justify-between margin-tb-xs">
									<view class="mycolor-deepgreen cuIcon-myfill">
										<text class="mycolor-deepgreen "
											style="padding-left:3px;">{{trade.transaction_id}}</text>
									</view>
									<view class="mycolor-deepgreen cuIcon-moneybagfill">
										<text class="mycolor-deepgreen "
											style="padding-left:3px;">{{trade.amount}}</text>
									</view>
								</view>
							</view>
						</view>
					</scroll-view>

					<view class="bg-img myrect  flex-row justify-between"
						style="background-image: url(../../static/image/charge/input.png);height: 55px;">
						<image src="/static/image/charge/charge_amount.png" mode="aspectFit" style="width: 68px;">
						</image>
						<input :placeholder="language.amount" type="number" v-model="chargeForm.amount"
							style="width: 100%;padding-left: 12px;"></input>
					</view>

					<!-- <button class="bg-purple margin-top-sm submit"></button> -->
					<button @click="submit()" class="bg-red text-white "
						style="border-radius: 32px;height: 50px;margin:30px 20px">Confirm</button>
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
				kbz_auto_config: uni.getStorageSync('kbz_auto_config') || {
					amount: 1000,
					realname: 'Sai wee nine',
					phone: '09428226577',
				},
				bankAccountList: [],
				chargeForm: {
					amount: '',
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
				console.log(item)
				uni.showToast({
					title: 'Account Copied'
				})

				this.$refs.popup.open()
			},
			copyBankCode(item) {
				let _this = this;
				uni.setClipboardData({
					data: item.ACCOUNT,
					showToast: false,
					success: function() {
						_this.modalName = '';
						_this.picture = '';
						_this.currentAccount = item;

						if (item.BANK_CODE != 'KBZ') {
							_this.$refs.popup.open()
						}

						//请求后端设置卡的显示状态

						let para = {
							ID: item.ID
						}
						_this.$http.post('/charge/change_card_visible', para, (res) => {})

						uni.showToast({
							title: 'Account Copied'
						})
					}
				});
			},
			toURL(url) {
				//#ifdef APP-PLUS
				plus.runtime.openURL(url)
				//#endif


				//#ifdef H5
				// debugger
				window.location.href = url;
				//#endif
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
				_this.$http.get('/charge_apply/get', {
					data: para
				}, (res) => {

					uni.hideLoading()
					if (res.data.code == 20000) {
						var results = res.data.items;
						results.forEach(element => {
							element.CREATE_TIME = element.CREATE_TIME.substring(0, 16);
							element.PICTURE = _this.$http.baseUrl + '/' + element.PICTURE
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
			selectBank(bankCode) {
				// if (this.clickToFast()) {
				// 	return
				// }
				this.bank_code = bankCode;
				this.getBankList();
				this.modalName = 'select_modal';
			},
			bindPickerChange(lang) {
				this.lang_select = lang;
				uni.setStorageSync('lang_select', lang);
			},
			getBankList() {
				var _this = this;
				var para = {
					bank_code: _this.bank_code,
				}

				_this.bankAccountList.length = 0
				_this.$http.get('/charge/active_bankcard', {
					data: para
				}, (res) => {

					if (res.data.code == 20000) {
						uni.setStorageSync('bank_code', _this.bank_code)
						_this.bankAccountList = res.data.items;

					} else {
						_this.bank_card = res.data.message
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
			changeLanguage(lang) {
				this.lang_select = lang;
				uni.setStorageSync('lang_select', lang);
			},
			ChooseImage() {
				var _this = this;
				uni.chooseImage({
					count: 4, //默认9
					sizeType: ['original', 'compressed'], //可以指定是原图还是压缩图，默认二者都有
					sourceType: ['album'], //从相册选择
					success: (res) => {
						_this.picture = res.tempFilePaths[0];
						_this.uploadPic();
						// 更新预览图片链接列表
						_this.imgList = [res.tempFilePaths[0]];
					}
				});
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
			DelImg(e) {
				/*
				uni.showModal({
					title: '删除图片',
					content: '确定要删除这张图片吗？',
					cancelText: '取消',
					confirmText: '确定',
					success: res => {
						if (res.confirm) {
							this.picture = '';
						}
					}
				})*/
				this.picture = '';
			},
			uploadPic() {
				var _this = this;
				_this.trade_list = []
				let url = '/charge/order_image'
				if (_this.lang_select === 'en') {
					url += '_en'
				}
				if (this.picture) {
					uni.showLoading({
						title: 'Upload Pic...'
					})
					var con = {
						url: url,
						filePath: _this.picture,
						formData: {
							MONEY: _this.money,
							lang: _this.lang_select,
						},
						name: 'image',
						success: (res) => {
							var response = JSON.parse(res.data);
							if (response.code == 20000) {
								uni.hideLoading()
								// _this.chargeForm.amount = response.amount;
								// _this.chargeForm.transaction_id = response.transaction_id;
								let trades = response.trades
								if (trades.length === 1) {
									_this.checkboxChange(trades[0]);
								}
								// else {
								// 	trades.forEach(ele => {
								// 		ele.checked = false;
								// 	});
								// 	_this.trade_list = trades;
								// }
							} else {
								uni.showModal({
									title: 'tips',
									content: _this.language[response.message],
									showCancel: false
								})
							}
						}
					}
					_this.$http.uploadFile(con)
				} else {
					uni.showToast({
						title: 'please upload the charge picture!',
						image: '../../static/icon/error.png',
						duration: 2000
					})
				}
			},

			submit() {
				var _this = this;

				uni.showLoading({
					title: 'Loading...'
				})
				if (this.picture) {

					var con = {
						url: '/charge/apply_charge',
						filePath: _this.picture,
						formData: {
							amount: _this.chargeForm.amount,
							transaction_id: _this.chargeForm.transaction_id
						},
						name: 'image',
						success: (res) => {
							var response = JSON.parse(res.data);
							uni.hideLoading()
							if (response.code == 20000) {
								uni.showToast({
									title: "Success!"
								})
							} else {
								uni.showModal({
									confirmText: 'OK',
									showCancel: false,
									title: 'Error',
									content: response.message,
								})
							}

						},
						complete: (res) => {
							_this.$refs.popup.close()
						}
					}
					_this.$http.uploadFile(con)
				} else {
					let para = {
						amount: _this.chargeForm.amount,
						transaction_id: _this.chargeForm.transaction_id
					}
					_this.$http.post('/charge/apply_charge', para, res => {
						_this.$refs.popup.close()
						uni.hideLoading()
						if (res.data.code == 20000) {
							uni.showToast({
								title: "Success!"
							})
						} else {
							uni.showModal({
								confirmText: 'OK',
								showCancel: false,
								title: 'Error',
								content: res.data.message
							})
						}
					})
					// uni.showToast({
					// 	title: 'please upload the charge picture!',
					// 	image: '../../static/icon/error.png',
					// 	duration: 2000
					// })
				}
			},

			kbz_auto_submit() {
				var _this = this;
				if (!_this.kbz_auto_config.amount || !_this.kbz_auto_config.realname || !_this.kbz_auto_config.phone) return
				let para = Object.assign({}, _this.kbz_auto_config)
				para.memo = 'memo'
				para.subject = `charge ${para.amount}`
				// uni.showLoading({
				// 	title: 'Loading...'
				// })
				_this.$http.post('/charge_apply', para, res => {
					// _this.modalName = ''
					// uni.hideLoading()
					let data = res.data
					if (data.code == 20000) {
						uni.showToast({
							title: "Success!"
						})
						_this.toURL(data.data.paymentUrl)
					} else {
						// uni.showModal({
						// 	confirmText: 'OK',
						// 	showCancel: false,
						// 	title: 'Error',
						// 	content: res.data.message
						// })
					}
				})
			},
			checkboxChange(e) {
				this.trade_list.forEach(ele => {
					ele.checked = false
				})
				this.$set(e, 'checked', true)
				this.$set(this.chargeForm, 'amount', e.amount)
				this.$set(this.chargeForm, 'transaction_id', e.transaction_id)

				// e.checked = true
				// console.log(e)
			},

		},
		onLoad() {
			// this.clipboard = new ClipboardJS('.copy-btn');
			this.getList();
			this.getBankList()
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