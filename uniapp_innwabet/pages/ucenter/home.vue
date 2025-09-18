<template name="ucenter">
	<view class="mybg-grey full-page">
		<!--  #ifdef APP-PLUS-->
		<cu-custom isBack="true" backUrl="/pages/index/index">
			<block slot="backText">
				<!--
				<navigator url="/pages/index/index" navigateTo>
					<text style="margin-left:5px">〈 {{language.back}} </text> </navigator>
					-->
			</block>
			<block slot="content">{{currentLanguage.ucenter}}
			</block>
		</cu-custom>
		<!-- #endif-->
		<!--  #ifdef  H5 -->
		<cu-custom isBack backUrl="/pages/index/index">
			<block slot="right">
			</block>
			<block slot="content">{{currentLanguage.ucenter}}
			</block>
		</cu-custom>
		<!-- #endif-->


		<!-- <view class="user-row">
			<view class="user-bar-cell" style="width: 35%;text-align: center;" @click="dislang(2)">
				<image style="width: 80px;height:80px;" src="../../static/icon/head.png"></image>
			</view>

			<view class="user-bar-cell" style="width: 55%;">
				<view><label class="text-bold">{{currentLanguage.name}}：{{$store.state.userInfo.NICK_NAME}}</label></view>
				<view>
					<label class="text-bold">{{currentLanguage.phone}}：{{$store.state.userInfo.PHONE}}</label>
				</view>
				<view>
					<label class="text-bold">{{currentLanguage.balance}}：{{$store.state.userInfo.TOTAL_MONEY}}</label>
				</view>
			</view>

			<view class="user-bar-cell" style="width: 10%;">

			</view>
		</view> -->
		<view class="myrect flex-row">
			<view>
				<image src="../../static/image/user_img.png" style="width: 70px;height: 70px;"></image>
			</view>
			<view class="flex-column" style="margin-left: 15px;">
				<view class="flex-row" style="font-size: 16px;">
					<text class="myfont-bold">{{currentLanguage.name}}：{{$store.state.userInfo.NICK_NAME}}</text>
				</view>
				<view class="flex-row">
					<text class="myfont-bold">{{currentLanguage.phone}}：{{$store.state.userInfo.PHONE}}</text>
				</view>
			</view>
		</view>

		<view class="balance-bar myrect box-shadow flex-row">
			<view>
				<image src="../../static/image/cash.png" style="width: 70px;height: 70px;margin-left: 5px;"></image>
			</view>
			<view class="flex-column" style="margin-left: 15px;">
				<view class="flex-row" style="font-size: 16px;">
					<text class="myfont-bold">{{currentLanguage.balance}}</text>
				</view>
				<view class="flex-row">
					<text class="myfont-bold">{{$store.state.userInfo.TOTAL_MONEY}}</text>
				</view>
			</view>
			
			<view class="flex-column" style="margin-left: 15px;padding:20px 0;">
				<view class="flex-row" style="font-size: 16px;">
					<text class="myfont-bold">{{currentLanguage.cashCode}}</text>
				</view>
				<view class="flex-row">
					<text class="myfont-bold">{{$store.state.userInfo.CASH_CODE}}</text>
				</view>
			</view>
			
		</view>
		<view class="cu-list menu " style="padding-bottom: 10px;">

			<view class="bar-row flex-row box-shadow myrect cu-item" v-for="(bar,index) in bar_list"
				@click="goto(bar.url)">
				<view class="flex-row content" style="text-align: left;">
					<view class="bar-icon">
						<image class="bar-icon-image" :src="bar.img"></image>
					</view>
					<text class="text-grey">{{bar.title}}</text>
				</view>
				<view class="action">
					<text class="text-grey text-sm">〉</text>
				</view>
			</view>
			
		


			<!-- #ifdef APP-PLUS -->
			<!-- <view class="cu-item">
				<view class="content">
					<text class="text-grey">version</text>
				</view>
				<view class="action">
					<text class="text-grey text-sm"> {{version}} </text>
				</view>
			</view> -->
			<view class="bar-row flex-row myrect cu-item">
				<view class="flex-row content" style="text-align: left;">
					<view class="bar-icon">
						<!-- <image class="bar-icon-image" :src="bar.img"></image> -->
					</view>
					<text class="text-grey">Version:{{version}}</text>
				</view>
				<view class="action">
					<text class="text-grey text-sm">〉</text>
				</view>
			</view>
			<!-- #endif-->

		</view>

		<view style="text-align: center;width: 100vw;">
			<button class="mybg-orange" style="width: 80%;border-radius: 10px;"
				@click="logout">{{currentLanguage.logout}}</button>
		</view>

		</scroll-view>

		<uni-popup ref="popup" type="center">
			<view style="width: 90vw;">
				<view>
					<view class="mybg-red text-bold text-center dialogsTitle" style="border-radius: 13px 13px 0 0 ;">
						{{temp.title}}</view>
					<view class="bg-white padding-sm">
						<!-- <view class="words_span">{{temp.content}}</view> -->
						<view class="words_span" v-if="temp.title===currentLanguage['about']">{{temp.content}}</view>

						<scroll-view scroll-y>
							<view v-for="(ele,index) in contact" class="flex"
								v-if="temp.title!=currentLanguage['about']">
								<text class="words_span" v-if='ele.type!=="site"'>
									{{ele.str}}</text>
								<text @click="toURL(ele.str)" class="words_span" v-if='ele.type=="site"'
									style="text-decoration: underline;font-size: 18px;">
									{{ele.str}}</text>
								<!-- <text @click="toURL(ele.str)" class="about-text" v-if='ele.type=="site"' style="text-decoration: underline;">
									{{ele.str}}</text> -->
								<a href </view>
						</scroll-view>

					</view>
				</view>
				<view class="mybg-pink text-center" style="border-radius: 0 0  13px 13px ;padding: 7px;">
					<button class="cu-btn" :class="temp.title!=currentLanguage['about']?'mybg-orange':'mybg-red'"
						style="width: 20%;" @click="hideDialogs">confirm</button>
				</view>
			</view>
		</uni-popup>

		<!--
		<uni-popup ref="contactDialogs" type="center">
			
			<view class="bg-white text-bold text-center dialogsTitle">{{temp.title}}</view>
			<view class="bg-white dialogs text-center span_box">
				<view class="words_span">{{temp.content}}</view>
			</view>
			
		</uni-popup>
		-->

	</view>
</template>

<script>
	import config from '../../utils/config.js'
	import language from '../../utils/language.js'
	import uniPopup from "@/components/uni-popup/uni-popup.vue";
	import dateFormatUtils from "../../utils/utils.js"

	export default {
		components: {
			uniPopup
		},
		name: "ucenter",
		data() {
			return {
				temp: {},
				about: '',
				currentLanguage: config.language,
				picker: '',
				contact2: '',
				contact: [],
				url_list: [
					'xxxxxxx',
					'https://innwa.link/D6',
					'https://innwa.link/D5',
					'https://innwa.link/D4.Bank.OK.KPay',
					'https://innwa.link/D3',
					'https://innwa.link/D2',
					'https://innwa.link/D1',
					'xxxxxxx',
					'https://innwa.link/withdrawl1',
					'https://innwa.link/w2',
				],
				bar_list: [{
						title: config.language.withdraw_history,
						url: 'withdraw-history',
						img: '../../static/image/withdraw_history.png',
					},
					{
						title: config.language.withdraw,
						url: 'withdraw',
						img: '../../static/image/withdraw.png',
					},
					{
						title: config.language.recharge,
						url: 'charge',
						img: '../../static/image/withdraw.png',
					},
					{
						title: config.language.depositRecords,
						url: 'charge_record',
						img: '../../static/image/withdraw_history.png',
					},
					// {
					// 	title: config.language.bank,
					// 	url: 'banks',
					// 	img: '../../static/image/withdraw_history.png',
					// },
					{
						title: config.language.changePassword,
						url: 'change_pwd',
						img: '../../static/image/change_pw.png',
					},
					// {
					// 	title: config.language.userCharge,
					// 	url: 'charge_upload',
					// 	img: '../../static/image/withdraw.png',
					// },
					{
						title: config.language.languageSelect,
						url: 'language',
						img: '../../static/image/select_lang.png',
					},
					{
						title: config.language.about,
						url: 'about',
						img: '../../static/image/about.png',
					},
					{
						title: config.language.contact2,
						url: 'contact2',
						img: '../../static/image/contact.png',
					},
				],
				contact: '',
				dislan: 0,
				dislan2: 0,
				version: uni.getStorageSync("version")
			}
		},

		methods: {
			dislang(ty) {
				switch (ty) {
					case 1:
						this.dislan++
						if (this.dislan > 5 && this.dislan2 > 5) {
							uni.navigateTo({
								url: '/pages/ucenter/language',
							})
						}
						break
					case 2:
						this.dislan2++
				}
			},
			toHome() {
				uni.reLaunch({
					url: '/pages/index/index'
				})
			},
			logout() {
				// this.music.play_dede();
				uni.removeStorageSync('Authorization');
				uni.redirectTo({
					url: '../login/login'
				})
			},
			numberFormat(num) {
				return dateFormatUtils.numFormat(num)
			},
			showContactDialogs() {
				// this.music.play_dede();
				this.$refs.contactDialogs.open()
			},
		
			goto(path) {
				// this.music.play_dede();
				let dialog = ['about','contact2']
				if (dialog.includes(path)) {
					this.showDialogs(path)
				} else {
					uni.navigateTo({
						url: '/pages/ucenter/' + path,
						animationType: 'slide-in-right',
						animationDuration: 100
					})

				}
			},
			showDialogs(title) {
				// this.music.play_dede();
				this.temp = {
					title: this.currentLanguage[title],
					content: this.$data[title]
				}
				this.$refs.popup.open()
			},
			hideDialogs() {
				this.$refs.popup.close()
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
			parseContact() {
				this.contact = []
				let arr = this.$store.state.configs.contact_us.split('\n')
				arr.forEach((ele, index) => {
					if (ele.indexOf('https') > -1) {
						this.contact.push({
							'str': ele,
							'type': 'site',
						})
					} else {
						this.contact.push({
							'str': ele,
							'type': 'str',
						})
					}
				})
			},
		},
		created() {
			this.rule = this.$store.state.configs.contact_us;
			this.contact2 = this.$store.state.configs.contact_us;
			this.about = this.$store.state.configs.help_content;
			this.parseContact()
			// console.log(this.contact)
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


	.balance-bar {
		width: 90vw;
		padding: 2px;
		background-color: #d54d4a;
		margin-top: 15px;
		color: white;
	}

	.dialogs {
		height: 50vh;
	}

	.about-text {
		color: rgb(129, 58, 58);
		font-size: 25px;
		width: 100%;
		display: inline-block;
		white-space: pre-wrap;
		word-wrap: break-word;
		height: auto;
	}

	.menu {
		margin-bottom: 60px;
	}

	.dialogsTitle {
		height: 5vh;
		line-height: 5vh;
		border-bottom: 1px solid lightgrey;
		font-size: 16px;
	}

	.span_box {
		display: table;
	}

	.words_span {
		display: table-cell;
		vertical-align: middle;
	}

	.border-right {
		border-right: 1px solid #E2E2E2;
	}

	.head {
		height: 60px;
		width: 100%;
		line-height: 60px
	}

	.height-150 {
		height: 150px;
		padding: 45px 0 0 12px;
		margin: 8px 0 8px 0;
	}

	.head image {
		float: left;
		height: 80px;
		width: 80px;
	}

	.cu-list {
		margin-top: 12px;
	}

	.head view {
		margin-left: 12px;
		float: left;
	}

	.user-row {
		width: 100%;
		color: white;
		height: 120px;
		display: flex;
		flex-direction: row;
		justify-content: space-around;
		align-items: center;
		background-image: url(../../static/image/user_msg_bg.png);
	}

	.user-info-loading {
		height: 15px;
		width: 15px;
		position: absolute;
		right: 5px
	}
</style>
