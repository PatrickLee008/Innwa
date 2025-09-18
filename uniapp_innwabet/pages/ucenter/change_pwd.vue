<template>
	<view class="full-page cu-list menu languageDialogs mybg-grey">
		<!--  #ifdef APP-PLUS-->
		<cu-custom isBack="true" backUrl="/pages/ucenter/home">
			<block slot="backText" >
			</block>
			<block slot="content">{{language.changePassword}}</block>
		</cu-custom>
		<!-- #endif-->
		<!--  #ifdef  H5 -->
		<cu-custom isBack="true" backUrl="/pages/ucenter/home">
			<block slot="content">{{language.changePassword}}
			</block>
		</cu-custom>
		<!-- #endif-->
		
		
		<view class="myrect box-shadow margin bg-white" style="padding: 6vw;">
			<view class="flex-row">
				<image src="../../static/image/jiju.png" class="my-icon"></image>
				<text class="myfont-bold myfont-12px">{{language.password}}</text>
			</view>
		
			<input class="mybg-grey my-input" password v-model="oldPassword" placeholder="Please enter your password" />
		
			<view class="flex-row">
				<image src="../../static/image/mima.png" class="my-icon"></image>
				<text class="myfont-bold myfont-12px">{{language.new_password}}</text>
			</view>
			<input class="mybg-grey my-input" v-model="password" password placeholder="Please enter your new password" />
		
			<view class="flex-row">
				<image src="../../static/image/mima.png" class="my-icon"></image>
				<text class="myfont-bold myfont-12px">{{language.passwordConfirm}}</text>
			</view>
			<input class="mybg-grey my-input" v-model="passwordConfirm" password placeholder="Please confirm your password" />
		
		
			<button class="my-button-orange" style="width: 70%;margin: 10px 15% 10px 15%;" @click="submit()" :disabled="loginDisabled">
				OK</button>
			
		</view>
		
		
		<!-- <view class="cu-form-group">
			<view class="title">{{language.password}}</view>
			<input password="true" v-model="oldPassword"></input>
		</view>

		<view class="cu-form-group">
			<view class="title">{{language.new_password}}</view>
			<input password="true" v-model="password"></input>
		</view>


		<view class="cu-form-group">
			<view class="title">{{language.passwordConfirm}}</view>
			<input password="true" v-model="passwordConfirm"></input>
		</view>
		<view class="cu-item" @click="submit">
			<button class="submit" style="background-color: rgb(185, 1, 0);color:white;" :disabled="loginDisabled">ok</button>
		</view> -->
	</view>
</template>

<script>
	import language from '../../utils/language.js'
	import config from '../../utils/config.js'
	export default {
		data() {
			return {
				picker: '',
				language: config.language,
				password: '',
				passwordConfirm: '',
				loginDisabled:false,
				oldPassword:''
			}
		},
		methods: {
			toHome(){
				uni.reLaunch({
					url: '/pages/ucenter/home'
				})
			},
			submit() {
				var _this = this;
				if(!this.password){
					uni.showModal({
						title: 'tips',
						content:  this.language['The password cannot be null'],
						showCancel: false,
						confirmText: 'ok',
						success: function(res) {}
					});
					return ;
				}
				if(this.password != this.passwordConfirm){
					uni.showModal({
						title: 'tips',
						content: this.language['The two passwords are inconsistent'],
						showCancel: false,
						confirmText: 'ok',
						success: function(res) {}
					});
					return ;
				}
				var para ={
					USER_PWD:this.password,
					OLD_PASSWORD:this.oldPassword
				}
				this.loginDisabled = true;
				_this.$http.post('/app_user/edit', para, (res) => {
					this.loginDisabled = false;
					if (res.data.code == 20000) {
						// uni.showToast({
						// 	title:  this.language['Change Password Success'],
						// 	icon: 'success',
						// 	duration: 2000
						// })
						uni.showModal({
							title: this.language['Change Password Success'],
							content: tips,
							showCancel: false,
							confirmText: 'ok',
						});
					} else {
						var tips = res.data.message;
						uni.showModal({
							title: 'tips',
							content: tips,
							showCancel: false,
							confirmText: 'ok',
							success: function(res) {}
						});
					}
					//this.$refs.popup.close()
				})
			}
		}
	}
</script>

<style>
	.submit {
		width: 100vw;
	}
	.bg-green{
		background-color: rgb(41, 150, 56)
	}
</style>
