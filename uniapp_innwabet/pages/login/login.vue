<template>
	<view class="mybg-grey full-page">
		<form>
			<view class="text-title">Members Login</view>
			<view style="text-align: center;">
				<image src="../../static/image/logo.png" style="width: 200px;height: 200px;"></image>
			</view>

			<view class="myrect bg-white" style="padding: 6vw;">
				<view class="flex-row">
					<image src="../../static/image/jiju.png" class="my-icon"></image>
					<text class="myfont-bold myfont-12px">{{language.account}}</text>
				</view>

				<input class="mybg-grey my-input" v-model="loginInfo.account" placeholder="Please enter phone number" />

				<view class="flex-row">
					<image src="../../static/image/mima.png" class="my-icon"></image>
					<text class="myfont-bold myfont-12px">{{language.input_password}}</text>
				</view>
				<input class="mybg-grey my-input" v-model="loginInfo.password" password="true"
					placeholder="Please enter your password" />

				<!-- 			<view class="flex-row" style="justify-content: space-between;">
					<text class="mycolor-orange myfont-bold myfont-12px">Remeber Me</text>
					<switch :checked="loginInfo.rememberMe" @change="switchChange" />
				</view> -->
				<!-- <input class="mybg-grey my-input" v-model="password" password="true" placeholder="Please enter your password" /> -->


				<button class="my-button-orange" style="width: 70%;margin: 10px 15% 10px 15%;" @click="login()"
					:disabled="loginDisabled">
					<text :class="loadding"></text>{{language.login}}</button>

				<view>
					<text class="mycolor-orange" style="padding: 5px;text-decoration: underline;"
						@click="toRegister()">register</text>

					<!--  #ifdef  H5 -->
					<!-- 			<text class="mycolor-orange" style="padding: 5px;text-decoration: underline;"
						@click="downloadApp()">DownLoad APP</text> -->
					<!-- #endif-->
				</view>

				<!-- AI助手按钮 -->
				<view class="ai-button" @click="toAI()">
					<image v-if="!showAIModal" src="/static/image/message.png" mode="heightFix" class="ai-avatar">
					</image>
					<image v-if="showAIModal" src="/static/image/close.png" mode="heightFix" class="ai-avatar"></image>
				</view>

			</view>
			<view style="position: fixed;right: 10px;bottom:10px;">{{version}}</view>
		</form>

		<!-- AI助手弹框 -->
		<view class="ai-modal" style="z-index: 1;" v-if="showAIModal" @click="closeAIModal">
			<view class="ai-modal-content" @click.stop="">
				<view class="ai-modal-header">
					<view class="ai-modal-title">
						<text class="ai-modal-title-text">
							{{'Welcome to INNWA AI'}}
						</text>
						<text class="myfont-12px" style="color: rgb(255,255,255,0.5);"
							@click="show_navigate=false">{{'How can we help you today?'}}</text>
					</view>
				</view>

				<!-- 问题列表模式 -->
				<view class="ai-modal-body" v-if="aiModalMode === 'list'">

					<view class="ai-questions">
						<view class="ai-question-item" v-for="(item, index) in aiQuestions" :key="index"
							:class="{ 'has-border-bottom': index < aiQuestions.length - 1 }"
							@click="selectQuestion(item)">
							<text class="ai-question-text">{{item.question}}</text>
							<text class="cuIcon-right ai-question-arrow"></text>
						</view>
					</view>
					<view class="ai-full-chat-btn" @click="goToFullChat">
						<view class="flex-row justify-between">
							<view class="flex-column justify-between text-left" style="align-items: start;">
								<text
									class="text-black text-bold margin-tb-xs myfont-14px">{{'Chat with Ai Agent'}}</text>
								<text class="myfont-12px" style="color: #AEAEAE;"
									@click="show_navigate=false">{{'Have questions? Innwa AI is here to assist you'}}</text>
							</view>
							<image src="/static/image/right.png" mode="heightFix" style="height: 15px;"></image>
						</view>
					</view>
					<view class="ai-modal-footer">
						<view class="ai-full-chat-btn" @click="showServiceNotAvailable">
							<view class="icon-light margin-right-xs"></view>
							<text class="ai-full-chat-text">ခန့်မှန်းသုံးသပ်ချက်</text>
						</view>
					</view>
				</view>

				<!-- 答案详情模式 -->
				<view class="ai-modal-body ai-answer-body" v-if="aiModalMode === 'answer'">
					<view class="ai-answer-content">
						<!-- 返回按钮 -->
						<view class="ai-answer-simple">
							<view class="ai-back-header" @click="backToQuestions" v-if="aiModalMode === 'answer'">
								<image src="/static/image/back.png" class="ai-back-icon"></image>
								<text class="ai-back-text">Back</text>
							</view>
							<view class="text-bold margin-tb-sm">{{ currentQuestion && currentQuestion.question }}
							</view>
							<text class="ai-answer-content-text">{{ currentQuestion && currentQuestion.answer }}</text>
						</view>
					</view>

					<view class="ai-full-chat-btn" @click="goToFullChat">
						<view class="flex-row justify-between">
							<view class="flex-column justify-between text-left" style="align-items: start;">
								<text
									class="text-black text-bold margin-tb-xs myfont-14px">{{'Chat with AI Agent'}}</text>
								<text class="myfont-12px"
									style="color: #AEAEAE;">{{'Have questions? Innwa AI is here to assist you'}}</text>
							</view>
							<image src="/static/image/right.png" mode="heightFix" style="height: 15px;"></image>
						</view>
					</view>
					<view class="ai-modal-footer">
						<view class="ai-full-chat-btn" @click="showServiceNotAvailable">
							<view class="icon-light margin-right-xs"></view>
							<text class="ai-full-chat-text">ခန့်မှန်းသုံးသပ်ချက်</text>
						</view>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	import advertisement from '../plugin/advertisement.vue'
	import config from '../../utils/config.js'
	import CryptoJS from 'crypto-js';

	const key = CryptoJS.enc.Utf8.parse('innwa'.padEnd(16, '\0'));
	const iv = CryptoJS.enc.Utf8.parse('1234567890123456'); // 初始向量，16字节

	function encrypt(text) {
		const encrypted = CryptoJS.AES.encrypt(text, key, {
			iv: iv,
			mode: CryptoJS.mode.CBC,
			padding: CryptoJS.pad.Pkcs7
		});
		return encrypted.toString();
	}


	export default {
		components: {
			advertisement
		},
		data() {
			return {
				swiperList: [{
					id: 0,
					type: 'image',
					url: 'http://swiper.innwabet.com/show_img_1.png'
				}, {
					id: 1,
					type: 'image',
					url: 'http://swiper.innwabet.com/show_img_2.png'
				}, {
					id: 2,
					type: 'image',
					url: 'http://swiper.innwabet.com/show_img_3.png'
				}, {
					id: 3,
					type: 'image',
					url: 'http://swiper.innwabet.com/show_img_4.png'
				}],
				loginDisabled: false,
				loadding: '',
				loginInfo: {
					account: '',
					password: '',
					rememberMe: true,
				},
				intervalID: '',
				version: uni.getStorageSync("version"),
				language: config.language,
				showAIModal: false,
				aiModalMode: 'list', // 'list' 或 'answer'
				currentQuestion: null,
				aiQuestions: [{
						question: 'ငွေဘယ်လိုသွင်းရပါသလဲ?',
						answer: 'အင်းဝမန်ဘာများများလွယ်ကူရိုးရှင်းစွာ ငွေသွင်းနိုင်ရန်အတွက်ပုံလေးနှင့်တကွ ရှင်းပြပေးထားပါတယ်ရှင့်\n\nဦးစွာပထမအင်းဝအကောင့်ထဲရှိကိုယ်ရေးအချက်အလက်ထဲဝင်ပြီး ငွေသွင်းရန်မှာ Wave Money သို့မဟုတ် KBZ Pay လေးကိုရွေးပေးပါရှင့်…\n\n1-1 KBZ Pay အကောင့်ဖြင့်ငွေ့သွင်းမည်ဆိုပါက\n\nအင်းဝအကောင့်ရှိကိုယ်ရေးအချက်အလက်ထဲက ငွေသွင်းရန်မှာ KBZ Pay Acc ကို Copy ယူပီး KBZ Pay မှတဆင့်ပုံမှန်ငွေလွှဲနေကျအတိုင်းလွှဲမည့်ငွေပမာဏဖြည့်ပြီး Kpay Note (မှတ်ချက်) မှာ မိမိတိုရဲ့အင်းဝအကောင့် "ငွေသွင်းကုဒ်" မှန်ကန်စွာဖြည့်ပေးပါရှင့်.\n\n*** အချက်လက်အားလုံးမှန်ကန်ပါက အင်းဝအကောင့်ထဲသို့အော်တို ငွေဝင်သွားပြီမှာဘဲဖြစ်ပါတယ်ရှင့် ***\n\nသတိပြုရန်မှာ: ငွေသွင်းကုဒ် အား Kpay Note ( မှတ်ချက်) တွင် မထည့်ပေးမိ၍သော်လည်ကောင်း ငွေသွင်းကုဒ်မှန်ကန်စွာမထည့်မိလျှင်လည်းကောင်း မိမိတို့ Innwa အကောင့်ထဲသို့ ငွေဝင်လာမည် မဟုတ်ပါဘူးရှင့်...'
					},
					{
						question: 'အင်းဝအကောင့်ဖွင့်ချင်လို့ပါ',
						answer: `အင်းဝအကောင့်ဖွင့်လှစ်ရန်အတွက် Google Chrome သို့မဟုတ် Phone Browser ထဲတွင်
www.innwamaung.com ဟုမှန်ကန်စွာရိုက်ထည့်ပြီး ရှာပေးပါနော်.. 

ဒေါင်းလုပ်ဆွဲရန်နေရာတွင် ANDROID (OR) IOS ရွေးပေးပါ အင်းဝဆော့ဝဲဒေါင်းပြီးပါက register ကိုနှိပ်ပါ။ 

📱 အကောင့်ဖွင့်လှစ်ခြင်း လုပ်ငန်းစဉ်:
• ဖုန်းနံပါတ် နှင့် အမည် 
• အသုံးပြုမည့် လျှို့ဝှက်နံပါတ်ကိုဖြည့်စွက်ပြီး 
• အတည်ပြုမည် ကိုနှိပ်ပါကအကောင့်ဖွင့်လှစ်ခြင်းပြီးဆုံးပါပြီရှင့်…

⚠️ မှတ်ချက် - အင်းဝအကောင့်ဖွင့်လှစ်ထားသော နာမည်နှင့် ဖုန်းနံပါတ်သည်ဘဏ်အကောင့်အချက်များနှင့်ကိုက်ညီ မှရှိမှာသာငွေထုတ်ဆောင်ရွက်နိုင်မည်ဖြစ်ပါတယ်ရှင့်...`
					},
					{
						question: 'ငွေထုတ်ချင်လို့ပါ',
						answer: `ငွေထုတ်မည်ဆိုပါက ကိုယ်ရေးအချက်လက်ထဲရှိ ငွေထုတ်ရန်ထဲသို့ဝင်ပြီး ထုတ်ယူမည့် ပမာဏဖြည့် ပေးရပါမည်။

💰 ငွေထုတ်ခြင်း အချက်အလက်များ:
• အနည်းဆုံး (10,000)ကျပ်မှစတင်၍ အကန့်သတ်မရှိထုတ်ယူနိုင်ပါသည်။
• သတိပြုရန်အချက်မှာ (OK) အားအကြိမ်ကြိမ်နှိပ်ပါကဆက်တိုက်ငွေထုတ်တင်ထားသလိုဖြစ်မည်ဖြစ်ပါသဖြင့် တစ်ကြိမ်နှိပ်ပြီးပြန်ထွက်လျှင်ရပါပီရှင့်။

📋 ငွေထုတ်လုပ်ငန်းစဉ်:
ငွေထုတ်မှတ်တမ်းကိုနှိပ်ပါ ငွေထုတ်ကုဒ်နေရာတွင် ABC နှင့် ဂဏာန်း 6 လုံးပါပါမည်။

🔗 ဆက်သွယ်ရန်လင့်များ:
ငွေထုတ်ကုဒ်မှာ A ပါရင် https://innwa.link/withdraw1
ငွေထုတ်ကုဒ်မှာ B ပါရင် https://innwa.link/w2 မှာပြောလိုက်ပါ
ငွေထုတ်ကုဒ်မှာ C ပါရင် https://cutt.ly/viberinnwawd3 မှာပြောလိုက်ပါ

📱 telegram အသုံးပြုတယ်ဆိုရင်:
ငွေထုတ်ကုဒ်မှာ A ပါရင် innwa.link/telegram/w1
ငွေထုတ်ကုဒ်မှာ B ပါရင် innwa.link/telegram/w2
ငွေထုတ်ကုဒ်မှာ C ပါရင် https://cutt.ly/telegraminnwawd3`
					},
					{
						question: 'ငွေသွင်းရမည့်ဘဏ်အကောင့်နံပါတ်လေးပို့ပေးပါ',
						answer: `ငွေသွင်းရမည့် ဘဏ်အကောင့်နံပါတ်များ ရယူနိုင်သည့်နေရာ:

📱 အင်းဝဆော့ဝဲထဲမှ ကိုယ်ရေး အချက်လက်ထဲဝင်ပါ 
📞 ဆက်သွယ်ရန်ကိုနှိပ်ပါ
💳 ပေးထားသော ငွေသွင်းရန်လင့်များမှ တဆင့် ငွေသွင်းနံပါတ်အားတောင်းခံနိုင်ပါသည်။

🏦 ရရှိနိုင်သည့် ငွေသွင်းနံပါတ်များ:
• KBZ Pay အကောင့်နံပါတ်
• Wave Money အကောင့်နံပါတ်
• အခြားဘဏ်အကောင့်နံပါတ်များ

ℹ️ အသေးစိတ်အတွက် ကိုယ်ရေးအချက်အလက် → ဆက်သွယ်ရန် သို့ဝင်ရောက်ကြည့်ရှုပါ။`
					}
				]
			};
		},
		mounted() {
			this.reloadUser()
		},
		methods: {
			toAI() {
				this.showAIModal = !this.showAIModal;
			},
			closeAIModal() {
				this.showAIModal = false;
				this.aiModalMode = 'list';
				this.currentQuestion = null;
			},
			selectQuestion(item) {
				// 切换到答案详情模式
				this.currentQuestion = item;
				this.aiModalMode = 'answer';
			},
			backToQuestions() {
				// 返回问题列表模式
				this.aiModalMode = 'list';
				this.currentQuestion = null;
			},
			goToFullChat() {
				this.closeAIModal();
				uni.navigateTo({
					url: '/pages/deepseek/index',
					animationType: 'slide-in-right',
					animationDuration: 300
				});
			},
			showServiceNotAvailable() {
				uni.showModal({
					title: 'Notice',
					content: 'Service is not available now',
					showCancel: false,
					confirmText: 'OK',
					success: function(res) {}
				});
			},
			downloadApp() {
				var u = navigator.userAgent;
				var isAndroid = u.indexOf('Android') > -1 || u.indexOf('Adr') > -1; //android终端
				var isiOS = !!u.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/); //ios终端

				var url = '';
				if (isAndroid) {
					url = 'http://dl.innwabet.net/android/InnwaBet_Android_New.apk'
				} else if (isiOS) {
					url = 'http://dl.innwabet.net/ios/InnwaBet_New.mobileconfig'
				} else {
					url = 'http://dl.innwabet.net/android/InnwaBet_Android_New.apk'
				}
				// #ifdef APP-PLUS
				plus.runtime.openURL(url) //这里默认使用外部浏览器打开而不是内部web-view组件打开
				// #endif
				// #ifdef H5
				window.open(url)
				// #endif
			},

			toRegister() {
				uni.navigateTo({
					url: "./register"
				})
			},

			switchChange(e) {
				this.rememberMe = e.target.value
			},
			reloadUser() {
				var _this = this;
				//缓存
				var loginInfo = uni.getStorageSync('loginInfo');
				//有缓存就赋值给文本
				if (loginInfo.account && loginInfo.password) {
					_this.loginInfo = loginInfo;
				}
			},
			login() {
				var _this = this;
				_this.loadding = 'cuIcon-loading2 cuIconfont-spin';
				_this.loginDisabled = true;

				const account = this.loginInfo.account;
				const password = this.loginInfo.password;


				const timestamp = new Date().getTime().toString();

				const params = JSON.stringify({
					account,
					password,
					timestamp
				});
				const encryptedParams = encrypt(params);

				var para = {
					encryptedParams: encryptedParams
				}


				_this.$http.post('/app_user/login', para, (res) => {
					_this.loadding = '';
					if (res.data.code == 20000) {
						// if (_this.loginInfo.rememberMe) {
						// 	uni.setStorageSync('loginInfo', _this.loginInfo);
						// } else {
						// 	uni.removeStorageSync('loginInfo');
						// };
						uni.setStorageSync('Authorization', res.data.token);
						uni.redirectTo({
							url: '../index/index'
						});
					} else if (res.data.code == 50002) {
						uni.showModal({
							title: 'Tips',
							content: this.language.wrong_pass_word,
							showCancel: false,
							confirmText: 'ok',
							success: function(res) {}
						});
						_this.loginDisabled = false;
					} else {
						uni.showModal({
							title: 'Tips',
							content: this.language[res.data.message],
							showCancel: false,
							confirmText: 'ok',
							success: function(res) {}
						});
						_this.loginDisabled = false;
					}
				})
			},
		}
	}
</script>
<style>
	.body {
		background-color: white;
	}

	.account {
		height: 250px;
		padding: 40px 15px 0 15px;
		border-radius: 8px;
		margin-top: 15px;
	}

	.bg-green {
		background-color: rgb(106, 0, 3);
	}

	.ai-button {
		position: fixed;
		right: 10px;
		bottom: 50px;
		width: 50px;
		height: 50px;
		border-radius: 25px;
		background-color: #6A0003;
		display: flex;
		align-items: center;
		justify-content: center;
		box-shadow: 0 2px 8px rgba(106, 0, 3, 0.3);
		transition: all 0.3s ease;
		z-index: 9999;
	}

	.ai-button:active {
		transform: scale(0.95);
		box-shadow: 0 1px 4px rgba(106, 0, 3, 0.5);
	}

	.ai-avatar {
		width: 20px;
		height: 20px;
	}

	/* AI弹框样式 */
	.ai-modal {
		position: fixed;
		top: 0;
		left: 0;
		width: 100vw;
		height: 100vh;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		padding: 20px;
		box-sizing: border-box;
	}

	.ai-modal-content {
		border-radius: 15px;
		width: 90%;
		max-width: 400px;
		max-height: 80vh;
		overflow: hidden;
		box-shadow: 0px 1px 1px 1px #00000040;
		border: 1px solid #6A000333;
		animation: modalSlideIn 0.3s ease-out;
	}

	@keyframes modalSlideIn {
		from {
			transform: translateY(-50px);
			opacity: 0;
		}

		to {
			transform: translateY(0);
			opacity: 1;
		}
	}

	.ai-modal-header {
		background: linear-gradient(135deg, #6A0003, #8B0004);
		color: white;
		padding: 15px 20px;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.ai-modal-title {
		display: flex;
		align-items: start;
		flex-direction: column;
		gap: 10px;
	}

	.ai-modal-avatar {
		width: 30px;
		height: 30px;
		border-radius: 15px;
		border: 2px solid rgba(255, 255, 255, 0.8);
	}

	.ai-modal-title-text {
		font-size: 16px;
		font-weight: bold;
		color: white;
		flex: 1;
		text-align: left;
	}

	.ai-modal-body {
		padding: 10px 20px 20px 20px;
		max-height: 60vh;
		overflow-y: auto;
		background-color: white;
	}

	.ai-questions {
		margin-bottom: 10px;
		border-radius: 12px;
		border: 1px solid #6A000333;
		background-color: white;
		padding: 10px;
	}

	.ai-question-item {
		/* border-radius: 8px; */
		padding: 10px;
		/* margin-bottom: 10px; */
		display: flex;
		align-items: center;
		justify-content: space-between;
		cursor: pointer;
		transition: all 0.2s ease;
	}

	.ai-question-item.has-border-bottom {
		border-bottom: 1px solid #6A000333;
	}

	.ai-question-item:hover {
		background: #e9ecef;
		border-color: #6A0003;
	}

	.ai-question-item:active {
		transform: scale(0.98);
	}

	.ai-question-text {
		font-size: 14px;
		color: black;
		flex: 1;
		line-height: 1.4;
		text-align: left;
		font-weight: bold;
	}

	.ai-question-arrow {
		color: black;
		font-size: 12px;
		font-weight: bold;
		margin-left: 10px;
	}

	.ai-modal-footer {
		border-top: 1px solid #e9ecef;
		padding-top: 10px;
	}

	.ai-full-chat-btn {
		/* background: linear-gradient(135deg, #6A0003, #8B0004); */
		background-color: white;
		color: #6A0003;
		border-radius: 8px;
		padding: 10px;
		text-align: center;
		cursor: pointer;
		transition: all 0.2s ease;
		border: 1px solid #6A000333;
	}

	.ai-full-chat-btn:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(106, 0, 3, 0.3);
	}

	.ai-full-chat-btn:active {
		transform: translateY(0);
	}

	.ai-full-chat-text {
		color: #6A0003;
		font-size: 14px;
		font-weight: bold;
		text-align: center;
	}

	/* 返回按钮样式 */
	.ai-back-header {
		display: flex;
		align-items: center;
		margin-bottom: 5px;
		cursor: pointer;
		transition: background-color 0.2s ease;
	}

	.ai-back-icon {
		width: 15px;
		height: 13px;
		margin-right: 10px;
	}

	.ai-back-text {
		font-size: 14px;
		color: #6A0003;
		font-weight: bold;
	}

	/* 答案详情页面样式 */
	.ai-answer-body {
		padding: 20px !important;
		max-height: 70vh !important;
		display: flex;
		flex-direction: column;
		background-color: white;
	}

	.ai-answer-content {
		/* padding: 20px; */
		flex: 1;
		overflow-y: auto;
	}

	.ai-answer-simple {
		background: #f8f9fa;
		border: 1px solid #e9ecef;
		border-radius: 8px;
		padding: 12px 8px;
		margin-bottom: 10px;
		transition: all 0.2s ease;
		text-align: left;
	}

	.ai-answer-content-text {
		font-size: 14px;
		line-height: 1.6;
		color: #333;
		white-space: pre-line;
		word-wrap: break-word;
	}

	/* 答案内容滚动条样式 */
	.ai-answer-content::-webkit-scrollbar {
		width: 4px;
	}

	.ai-answer-content::-webkit-scrollbar-thumb {
		background-color: rgba(106, 0, 3, 0.3);
		border-radius: 2px;
	}

	.ai-answer-content::-webkit-scrollbar-track {
		background-color: transparent;
	}
</style>