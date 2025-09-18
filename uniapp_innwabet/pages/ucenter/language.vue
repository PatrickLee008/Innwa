<template>
	<view class="full-page cu-list menu languageDialogs mybg-grey">		
			<!--  #ifdef APP-PLUS-->
			<cu-custom isBack="true" backUrl="/pages/ucenter/home">
		
				<block slot="content">{{language.languageSelect}}
				</block>
			</cu-custom>
			<!-- #endif-->
			<!--  #ifdef  H5 -->
			<cu-custom isBack="true" backUrl="/pages/ucenter/home">
				<block slot="content">{{language.languageSelect}}
				</block>
			</cu-custom>
			<!-- #endif-->
		
		<view class="mybg-grey flex-row">
			<!-- <view class="content">
				<text class="text-grey">English</text>
			</view> -->
			<button style="border-radius: 10px;width: 90%;margin: 5% 5% 0 5%;" :class="picker=='en'? 'mybg-red':'bg-white'" @click="pickerChange('en')">English</button>
		</view>
		<view class="mybg-grey flex-row">
			<!-- <view class="content">
				<text class="text-grey">English</text>
			</view> -->
			<button style="border-radius: 10px;width: 90%;margin: 4% 5% 0 5%;" :class="picker=='myan'? 'mybg-red':'bg-white'" @click="pickerChange('myan')">မြန်မာ</button>
		</view>
		<!-- <view class="myrect cu-item flex-row" :class="{'bg-gradual-purple':picker=='myan'}" @click="pickerChange('myan')">
			<view class="content">
				<text class="text-grey">မြန်မာ</text>
			</view>
		</view> -->
		<!--
		<view class="cu-item" :class="{'bg-gradual-pink':picker=='cn'}" @click="pickerChange('cn')">
			<view class="content">
				<text class="text-grey">中文</text>
			</view>
		</view>
		-->
		<button class="my-button-orange" style="width: 70%;margin: 10px 15% 10px 15%;" @click="submit()" >
			OK</button>
	</view>
</template>

<script>
	import language from '../../utils/language.js'
	import config from '../../utils/config.js'
	export default {
		data() {
			return {
				picker: '',
				language: config.language
			}
		},
		methods: {
			toHome(){
				uni.reLaunch({
					url: '/pages/ucenter/home'
				})
			},
			pickerChange(value) {
				// this.music.play_dede() ;
				this.picker = value;
			},
			submit() {
				// this.music.play_dede() ;
				if (!this.picker) this.picker = 'en';
				config.language = language[this.picker];
				uni.setStorageSync('language', this.picker);
				this.toHome()
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
