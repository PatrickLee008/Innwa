<template>
	<view class="mybg-grey full-page">
		<cu-custom isBack backUrl="/pages/login/login">
			<block slot="content">{{language.registerTitle}}</block>
		</cu-custom>
		<form>
			
			<view style="text-align: center;">
				<image src="../../static/image/logo.png" style="width: 200px;height: 200px;"></image>
			</view>
			
			<view class="myrect bg-white" style="padding: 6vw;">
				<view class="flex-row">
					<image src="../../static/image/jiju.png" class="my-icon"></image>
					<text class="myfont-bold myfont-12px">{{language.account}}</text>
				</view>
	
				<input class="mybg-grey my-input" v-model="loginInfo.phone" placeholder="Please enter phone number " />
				
				<view class="flex-row">
					<image src="../../static/image/jiju.png" class="my-icon"></image>
					<text class="myfont-bold myfont-12px">{{language.name}}</text>
				</view>
	
				<input class="mybg-grey my-input" v-model="loginInfo.nickname" placeholder="Please enter your nickname" />
	
				<view class="flex-row">
					<image src="../../static/image/mima.png" class="my-icon"></image>
					<text class="myfont-bold myfont-12px">{{language.input_password}}</text>
				</view>
				<input class="mybg-grey my-input" v-model="loginInfo.password" password="true" placeholder="Please enter your password" />
	
				<view class="flex-row">
					<image src="../../static/image/mima.png" class="my-icon"></image>
					<text class="myfont-bold myfont-12px">{{language.passwordConfirm}}</text>
				</view>
				<input class="mybg-grey my-input" v-model="loginInfo.confirm_password" password="true" placeholder="Please confirm your password" />
				
	
	
				<button class="my-button-orange" style="width: 70%;margin: 10px 15% 10px 15%;" @click="register()" :disabled="loginDisabled">
					<text :class="loadding"></text>{{language.register}}</button>
				
			</view>
		</form>
	</view>
	<!-- <view>
		<cu-custom bgColor="bg-purple">
			<block slot="content">{{language.registerTitle}}</block>
		</cu-custom>

		<advertisement />

		<form>
			<view class="cu-form-group">
				<view class="title">Account</view>
				<input v-model="account"></input>
			</view>

			<view class="cu-form-group">
				<view class="title">Password</view>
				<input password="true" v-model="password"></input>
			</view>

			<view class="cu-form-group">
				<view class="title">Confirm Password</view>
				<input password="true" v-model="password2"></input>
			</view>
			
			<view class="cu-form-group">
				<view class="title">Phone</view>
				<input v-model="phone"></input>
			</view>
			

			<view class="padding-xl">
				<button class="cu-btn block bg-blue margin-tb-sm lg" @click="register()">{{language.register}}</button>
			</view>
		</form>
	</view> -->
</template>

<script>
	import advertisement from '../plugin/advertisement.vue'
	import config from '../../utils/config.js'
	export default {
		components: {
			advertisement
		},
		data() {
			return {
				loginDisabled:false,
				loginInfo:{
					nickname: '',
					phone: '',
					password: '',
					confirm_password:'',
				},
				loadding:'',
				language: config.language
			}
		},
		methods: {
			register() {
				let _this = this;
				if(!_this.loginInfo.password){
					uni.showModal({
						title: 'Tips',
						content:  _this.language['The password cannot be null'],
						showCancel: false,
						confirmText: 'ok',
						success: function(res) {}
					});
					return ;
				}
				if(_this.loginInfo.password != _this.loginInfo.confirm_password){
					uni.showModal({
						title: 'Tips',
						content: _this.language['The two passwords are inconsistent'],
						showCancel: false,
						confirmText: 'ok',
						success: function(res) {}
					});
					return ;
				}
				let para = {
					NICK_NAME: this.loginInfo.nickname,
					USER_PWD: this.loginInfo.password,
					PHONE: this.loginInfo.phone
				}
				_this.loadding = 'cuIcon-loading2 cuIconfont-spin';
				_this.loginDisabled = true
				uni.showLoading({
					title: "registering"
				})
				_this.$http.post('/app_user/add', para, (res) => {
					_this.loadding = ''
					if (res.data.code == 20000) {
						uni.showModal({
							title: 'Success!',
							content: 'Welcome to InnwaBet',
							showCancel: false,
							confirmText: 'ok',
							success: function(res) {
								uni.redirectTo({
									url: '../login/login'
								});
							}
						});
						
					} else {
						_this.loginDisabled = false
						uni.showModal({
							title: 'Error!',
							content: res.data.message,
							// content: this.language[res.data.message],
							showCancel: false,
							confirmText: 'ok',
							success: function(res) {}
						});
					}
					uni.hideLoading();
				})
			}
		}
	}
</script>

<style>

</style>
