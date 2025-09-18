<template>
	<view>
		<cu-custom bgColor="bg-purple" isBack="true">
			<block slot="content">{{currentLanguage.userCharge}}</block>
		</cu-custom>

		<view class="cu-form-group margin-top"  @click="PickerChange">
			
			<view class="title">BankType</view>
			<view class="picker flex-row justify-center align-center" style="width: auto;">
				<image style="width: 38px;height: 38px;border-radius:50%"
					:src="'/static/icon/'+currentBank+'.jpg'">
				</image>
				<text class="margin-left-sm">{{currentBank}}</text>
			</view>

			<!-- 	<picker @change="PickerChange" :value="bankOptionsIndex" :range="bankOptions">
				<view class="picker">
					{{bankOptions[bankOptionsIndex]}}
				</view>
			</picker> -->
		</view>

		<view class="flex-column bg-white padding-sm" v-if="backAccount">
			<text class="text-bold margin-tb-sm">{{currentLanguage['Please recharge to this account']}}</text>
			
			<view class="text-bold margin-tb-sm flex-row align-center justify-center "
				style="font-size: 18px;color:#eb2c01">
				<text >{{backName}}</text>
			</view>
			
			<view class="text-bold margin-tb-sm flex-row align-center justify-center "
				style="font-size: 18px;color:#eb2c01">
				
				<text >{{backAccount}}</text>
				<image src="../../static/icon/copy.png"
					style="width: 38rpx;height: 38rpx;margin-left:8px;margin-bottom:2px" @click="copy">
				</image>
				
			</view>
			
		</view>


		<view class="padding flex flex-wrap justify-between align-center bg-white">
			<button class="cu-btn round lg" @click="chooseImage()">{{currentLanguage.pictureUpload}}</button>
			<button class="cu-btn round lg bg-red" @click="chargeSubmit()">{{currentLanguage.upload}}</button>
		</view>

		<form>
			<view class="cu-form-group margin-top">
				<view class="title">{{currentLanguage['Transaction ID']}}:</view>
				<input :disabled="true" v-model="form.transaction_id"></input>
			</view>
			
			<view class="cu-form-group">
				<view class="title">{{currentLanguage.time}}:</view>
				<input :disabled="true" v-model="form.create_time"></input>
			</view>

			<view class="cu-form-group">
				<view class="title">{{currentLanguage.amount}}:</view>
				<input :disabled="true" v-model="form.amount"></input>
			</view>

		</form>

		<uni-popup ref="popup" type="center">

			<view class="popup">

				<view class="text-center text-bold bg-red border"
					style="border-radius:13px 13px 0 0;height: 46px;line-height: 46px;">Bank</view>

				<view class="bg-white" style="padding-top: 10px;">
					<view @click="setBank(item)" v-for="item in bankOptions"
						class="flex-row justify-around align-center padding-xs"
						style="border-bottom: 1px solid #F2F2F2;">
						<radio :class="item == currentBank?'checked':''" :checked="item == currentBank?true:false"></radio>
						<image style="width: 38px;height: 38px;border-radius:50%"
							:src="'/static/icon/'+item+'.jpg'">
						</image>
						<view style="width:50%" class="text-bold">{{item}}</view>
					</view>
				</view>

				<view class="cu-bar " style="background-color: #F2F2F2">
					<view class="action justify-center flex-row" @click="close">
						OK
					</view>
				</view>

			</view>

		</uni-popup>

		<image :src="imagePath" mode="aspectFit" style="width: 100vw;height: calc(100vh - 45px - 76px - 32px);"></image>

	</view>
</template>

<script>
	import config from '../../utils/config.js'
	import language from '../../utils/language.js'
	export default {
		data() {
			return {
				form: {
					transaction_id: '',
					create_time: '',
					amount: 0
				},
				backAccount: '',
				backName:'',
				imagePath: "",
				currentLanguage: config.language,
				currentBank: 'KBZ',
				bankOptions: ['KBZ','WaveMoney']
			}
		},
		methods: {

			// PickerChange(option) {
			// 	this.bankOptionsIndex = option.detail.value
			// 	this.getActiveBankCard()
			// },
			setBank(item) {
				this.currentBank =  item
			},
			close(){
				this.$refs.popup.close();
				this.getActiveBankCard()
			},
			PickerChange() {
				this.$refs.popup.open();
			},
			copy: function() {
				uni.setClipboardData({
					data: this.backAccount,
					success() {
						uni.showToast({
							title: 'copy success'
						})
					}
				});
			},
			chooseImage() {
				var _this = this;
				uni.chooseImage({
					count: 6, //默认9
					sizeType: ['original', 'compressed'], //可以指定是原图还是压缩图，默认二者都有
					sourceType: ['album'], //从相册选择
					success: function(res) {
						console.log(JSON.stringify(res.tempFilePaths));
						_this.imagePath = res.tempFilePaths[0]
						_this.uploadImage();
					}
				});
			},
			uploadImage: function() {
				let _this = this;
				let baseUrl = _this.$http.baseUrl
				uni.showLoading({
					title: 'loadding...',
				})
				uni.uploadFile({
					url: baseUrl + '/charge/order_image',
					filePath: _this.imagePath,
					name: 'image',
					header: {
						'Authorization': uni.getStorageSync('Authorization')
					},
					success(res) {
						res.data = JSON.parse(res.data)
						if (res.data.code == 20000) {
							uni.hideLoading()
							_this.form.transaction_id = res.data.transaction_id;
							_this.form.amount = res.data.amount;
							_this.form.create_time = res.data.create_time;
							// uni.showToast({
							// 	title:"Upload Success!"
							// })
						}
					}
				});
			},
			getActiveBankCard() {
				var _this = this;
				var para = {
					bank_code: _this.currentBank
				}
				_this.$http.get('/charge/active_bankcard', {
					data: para
				}, (res) => {
					if (res.data.code == 20000) {

						if (res.data.active_bankcard) {
							_this.backAccount = res.data.active_bankcard.ACCOUNT
							_this.backName = res.data.active_bankcard.NAME
						} else {
							_this.backAccount = ''
						}

					}
				})
			},
			chargeSubmit() {
				let _this = this;
				let baseUrl = _this.$http.baseUrl
				uni.showLoading({
					title: 'upload...',
				})
				uni.uploadFile({
					url: baseUrl + '/charge/apply_charge',
					filePath: _this.imagePath,
					name: 'image',
					formData: _this.form,
					header: {
						'Authorization': uni.getStorageSync('Authorization')
					},
					success(res) {
						res.data = JSON.parse(res.data)
						if (res.data.code == 20000) {
							uni.showToast({
								title: "Upload Success!"
							})
						}else{
							uni.showModal({
								title:'Tips',
								showCancel:false,
								content:res.data.message
							})
						}
					},
					complete() {
						uni.hideLoading()
					}
				});
			}

		},
		mounted() {
			this.getActiveBankCard()
		}
	}
</script>

<style>
	.popup {
		width: 85vw;
	}
</style>
