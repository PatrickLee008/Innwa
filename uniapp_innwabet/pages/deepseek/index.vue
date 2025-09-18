<template>
	<div class="page">
		<!-- ai -->
		<view class="custom-header">
			<view class="header-left" @click="navigateToHome">
				<image style="width: 19px;height: 13px;" src="../../static/image/fanhui.png" mode="aspectFit"></image>
			</view>
			<view class="header-center">
				<text class="header-title">INNWA AI Agent</text>
			</view>
			<view class="header-right flex align-center" @click="toggleMoreMenu">
				<image src="/static/image/ai/more.png" mode="aspectFit" class="more-icon"></image>
			</view>
		</view>
		<!-- app -->
		<!-- <cu-custom isBack>
			<block slot="content">INNWA AI Agent</block>
			<view slot="right" class="flex align-center" @click="toggleMoreMenu">
				<image src="/static/image/ai/more.png" mode="aspectFit" style="width: 20px; height: 20px;">
				</image>x
			</view>
		</cu-custom> -->
		<scroll-view ref="scroller" scroll-y style="height:calc(100vh);padding-top: 44px;" class="" @scrolltolower=""
			:scroll-top="scroll_top" :scroll-into-view="scroll_into_view">
			<view style="">

				<!-- More功能弹框 -->
				<view v-if="showMoreMenu" class="more-menu-dropdown" style="z-index: 1;" @click="closeMoreMenu">
					<view class="more-menu-content" @click.stop="">
						<view class="more-menu-item" @click="toggleNotification">
							<image src="/static/image/ai/notification.png" mode="aspectFit" class="more-menu-icon">
							</image>
							<text
								class="more-menu-text">{{ notificationEnabled ? 'Notification On' : 'Notification Off' }}</text>
						</view>
						<view class="more-menu-item" @click="showServiceNotAvailable">
							<view class="icon-light more-menu-icon"></view>
							<text class="more-menu-text">ခန့်မှန်းသုံးသပ်ချက်</text>
						</view>
						<view class="more-menu-item" @click="clear_message">
							<image src="/static/image/ai/clear.png" mode="aspectFit" class="more-menu-icon"></image>
							<text class="more-menu-text">Clear History</text>
						</view>
					</view>
				</view>

				<div class="answer" style="min-height: calc(100vh - 200px);">
					<div class="answerMain">
						<div class="answerMain-bd">
							<!-- 第一条消息的时间显示 -->
							<div v-if="answerList.length > 0" class="time-divider">
								<div class="time-header-first">
									{{ formatMessageTime(answerList[0].timestamp) }}
								</div>
							</div>

							<div class="answerMain-item">
								<!-- <img src="@/static/ai-avatar.png" class="answerMain-item__avatar" /> -->
								<div class="answerMain-item__content" style="padding: 10px 12px;">
									မင်္ဂလာပါ။ Innwa မှ ကြိုဆိုပါတယ်။ ဘယ်လိုကူညီလေးများပေးရမလဲရှင့်😊
									<!-- <div class="defaultQuestion">
										<div class="defaultQuestion-item" @click="onClickDefaultQuestion($event, item)"
											v-for="(item,index) in defaultQuestifrron.list" :key="index" :span="12">
											{{ item.value }}
										</div>
									</div> -->
								</div>
							</div>
							<div v-for="(item, index) in answerList" :key="index">
								<!-- 时间分割线 -->
								<div v-if="shouldShowTimeHeader(index)" class="time-divider">
									<div v-if="index === 0" class="time-header-first">
										{{ formatMessageTime(item.timestamp) }}
									</div>
									<div v-else class="time-header-with-line">
										<div class="time-line"></div>
										<div class="time-text">{{ formatMessageTime(item.timestamp) }}</div>
										<div class="time-line"></div>
									</div>
								</div>

								<div :class="['answerMain-item', {'roleUser': item.role === 'user' }]"
									class="message-item-animate">
									<img v-show="item.role === 'assistant' && item.content === 'ဖတ်ရှုနေပါသည်…'"
										src="@/static/ai-avatar.png" class="answerMain-item__avatar" />
									<img v-show="item.role === 'user'" src="@/static/ai-question-avatar.png"
										class="answerMain-item__avatar" />
									<div class="">

										<div v-if="item.role === 'user'"
											class="answerMain-item__content user-message-animate">
											{{ item.content }}
										</div>
										<div v-else-if="item.role === 'assistant'"
											:class="['answerMain-item__content', {'loading': item.content === 'ဖတ်ရှုနေပါသည်…'}]">
											<div class="answerMain-item__outputReasonContent">
												{{ item.reasoning_content }}
											</div>
											<div v-if="item.content === 'ဖတ်ရှုနေပါသည်…'" class="ai-loading-wrapper">
												<div class="ai-loading-text">ဖတ်ရှုနေပါသည်{{ loadingDots }}</div>
												<div class="ai-loading-animation">
													<div class="dot dot1"></div>
													<div class="dot dot2"></div>
													<div class="dot dot3"></div>
												</div>
											</div>
											<transition name="ai-response" mode="out-in">
												<zero-markdown-view v-if="item.content !== 'ဖတ်ရှုနေပါသည်…'"
													:markdown="item.content" themeColor="#05073b"
													class="ai-response-content"></zero-markdown-view>
											</transition>
										</div>
									</div>
								</div>

								<!-- 用户消息的时间显示（当下一条是加载消息时） -->
								<div v-if="item.role === 'user' && index < answerList.length - 1 && answerList[index + 1].content === 'ဖတ်ရှုနေပါသည်…'"
									class="last-message-time">
									{{ formatMessageTime(item.timestamp) }}
								</div>

								<!-- 最后一条消息的时间显示（非加载状态） -->
								<div v-else-if="isLastMessage(index) && item.content !== 'ဖတ်ရှုနေပါသည်…'"
									:class="['last-message-time', {'ai-message-time': item.role === 'assistant'}]">
									<div v-if="item.role === 'assistant'">
										By Innwa AI Agent {{ formatMessageTime(item.timestamp) }}
									</div>
									<div v-else>
										{{ formatMessageTime(item.timestamp) }}
									</div>
								</div>
							</div>
						</div>

					</div>
				</div>

				<view class="answerMain-ft" style="bottom: 0;position: fixed;width: 100vw;z-index: 100;">
					<!-- 建议回复 -->
					<view v-if="suggestedReplies.length > 0" class="suggested-replies suggested-replies-enter">
						<scroll-view scroll-x="true" class="suggested-replies-scroll">
							<view class="suggested-replies-container">
								<view v-for="(reply, index) in suggestedReplies" :key="index"
									class="suggested-reply-item" :style="{animationDelay: (index * 0.1) + 's'}"
									@click="selectSuggestedReply(reply)">
									{{ reply }}
								</view>
							</view>
						</scroll-view>
					</view>
					<div class="answerMain-input">
						<div style="display: flex; align-items: center; gap: 8px;">
							<textarea v-model.trim="answerKeyword" @keydown.enter.native="onSubmit"
								placeholder="ဤနေရာတွင် စာရိုက်ပါ...." class="answerMain-input__textarea"
								placeholder-style="font-size:12px"></textarea>
							<image @click="onSubmit"
								:src="answerKeyword && answerKeyword.length > 0 ? '/static/image/right.png' : '/static/image/ai/no_content.png'"
								mode="scaleToFill" style="width: 15px;height: 15px;"></image>
						</div>
						<!-- <div style="display: flex; justify-content: flex-end; margin-top: 8px;">
							<button @click="clear_message()" type="warn" class="answerMain-input__button">
								Clear
							</button>
						</div> -->
					</div>
				</view>
				<view id="scroll-bottom" style="height: .1px;"></view>
			</view>
		</scroll-view>

		<!-- <view class="cu-modal" style="z-index: 10;" :class="{'show':show_navigate,}" @click="">
			<view class="cu-dialog width-100  bg-white" style="vertical-align: top;border-radius: 0px;" @click.stop="">
				<scroll-view scroll-y class="height-90vh flex-column1 justify-start align-start text-black">
					<view class="flex-column justify-end height-40vh padding-left-sm text-white"
						style="background-color: rgb(7,102,255);align-items: start;justify-content: end;">
						<text class="myfont-30px">{{'Hi there!👋'}}</text>
						<text class="myfont-16px margin-top-lg"
							style="color: rgb(226,255,255);">{{'How can we help you?'}}</text>
						<view class="height-55px"></view>
					</view>
					<view class="flex-column padding-lr-sm bg-white radius-12px text-black text-bold"
						style="margin-left: 2%;width: 96%;margin-top: -30px;border: 1px solid #dcdcdc;">
						<view class="flex-row justify-between solid-bottom padding-tb"
							v-for="(item,index) in defaultQuestion.list" :key="index"
							@click="navigate_dafult_option($event, item)">
							<view class="">{{item.value}}</view>
							<text class="cuIcon-right"></text>
						</view>
					</view>
					<view class="flex-column padding-lr-sm bg-white radius-12px margin-top-sm"
						style="margin-left: 2%;width: 96%;border: 1px solid #dcdcdc;">
						<view class="flex-row justify-between solid-bottom padding-tb">
							<view class="flex-column justify-between" style="align-items: start;">
								<text class="text-black text-bold margin-tb-xs">{{'Chat with Lyro'}}</text>
								<text class="myfont-12px"
									@click="show_navigate=false">{{'Have questions? Lyro is here to assist you'}}</text>
							</view>
							<text class="cuIcon-right text-bold"></text>
						</view>
					</view>
				</scroll-view>
				<view class="height-10vh flex-row justify-around myfont-24px">
					<view class="flex-column">
						<text class="cuIcon-homefill" style="color: rgb(7,102,255);"></text>
						<text class="myfont-15px text-bold">{{'Home'}}</text>
					</view>
					<view class="flex-column" style="color: rgb(114,118,128);" @click="show_navigate=false">
						<text class="cuIcon-commentfill"></text>
						<text class="myfont-15px text-bold">{{'Chat'}}</text>
					</view>
				</view>
			</view>
		</view> -->
	</div>
</template>

<script>
	import {
		ref
	} from 'vue';
	// import test_text from './text.js'

	export default {
		components: {},
		data() {
			return {
				// show_navigate: false,
				showMoreMenu: false,
				loadingDots: '',
				loadingInterval: null,
				suggestedReplies: [],
				currentMessageId: null,
				notificationEnabled: uni.getStorageSync('notificationEnabled') !== false, // 默认开启
				buffer: '', // 用于存储流式数据不完整的行
				scroll_top: 0,
				config: {},
				request_token: '',
				// request_url:'https://179f-180-137-99-180.ngrok-free.app',
				request_url: '',
				scroll_into_view: '',
				defaultQuestion: {
					list: [{
							value: 'ငွေဘယ်လိုသွင်းရပါသလဲ?',
							answer: `အင်းဝမန်ဘာများများလွယ်ကူရိုးရှင်းစွာ ငွေသွင်းနိုင်ရန်အတွက်ပုံလေးနှင့်တကွ ရှင်းပြပေးထားပါတယ်ရှင့်
ဦးစွာပထမအင်းဝအကောင့်ထဲရှိကိုယ်ရေးအချက်အလက်ထဲဝင်ပြီး ငွေသွင်းရန်မှာ Wave Money သို့မဟုတ် KBZ Pay လေးကိုရွေးပေးပါရှင့်…
<img src="../../static/deepseek/test/q1-1.jpg"><br/>

1-1 KBZ Pay အကောင့်ဖြင့်ငွေ့သွင်းမည်ဆိုပါက
အင်းဝအကောင့်ရှိကိုယ်ရေးအချက်အလက်ထဲက ငွေသွင်းရန်မှာ KBZ Pay Acc ကို Copy ယူပီး KBZ Pay မှတဆင့်ပုံမှန်ငွေလွှဲနေကျအတိုင်းလွှဲမည့်ငွေပမာဏဖြည့်ပြီး ပုံမှာပြထားသည့်အတိုင်း Kpay Note (မှတ်ချက်) မှာ မိမိတိုရဲ့အင်းဝအကောင့် “ငွေသွင်းကုဒ်” မှန်ကန်စွာဖြည့်ပေးပါရှင့်.
<img src="../../static/deepseek/test/q1-2.jpg"><br/>
မိမိလွှဲမည့်ငွေပမာဏကိုဖြည့်ပါ၊ မှတ်ချက်နေရာတွင် ငွေသွင်းကုတ်အား ဖြည့်သွင်းပါ... ကိုယ်ရေးအချက်အလက်နေရာတွင် ငွေသွင်းကုန်အား ပြန်လည်စစ်ဆေးနိုင်ပါသည်။
*** အချက်လက်အားလုံးမှန်ကန်ပါက အင်းဝအကောင့်ထဲသို့အော်တို ငွေဝင်သွားပြီမှာဘဲဖြစ်ပါတယ်ရှင့် ***
👉 မမေ့နဲ့နော် Kpay Note (မှတ်ချက်) မှာမိမိတို့ရဲ့အင်းဝအကောင့်ငွေသွင်းကုဒ်ဖြည့်ဖြစ်အောင်ဖြည့်ပေးပါရှင့်
⚠️ သတိပြုရန်မှာ ⚠️ ငွေသွင်းကုဒ် အား Kpay Note ( မှတ်ချက်) တွင် မထည့်ပေးမိ၍သော်လည်ကောင်း ငွေသွင်းကုဒ်မှန်ကန်စွာမထည့်မိလျှင်လည်းကောင်း မိမိတို့ Innwa အကောင့်ထဲသို့ ငွေဝင်လာမည် မဟုတ်ပါဘူးရှင့်...
<img src="../../static/deepseek/test/q1-3.jpg"><br/>

1-2 Wave Money အကောင့်ဖြင့်ငွေသွင်းမည်ဆိုပါက
ကိုယ်ရေးအချက်လက်ထဲကိုသွားပီး ငွေသွင်းရန်ထဲက wave acc တစ်ခုကို copy ယူပေးပါရှင့်ပြီးပါက မိမိတိုရဲ့ wave acc ထဲဝင်ရောက်ပြီးပုံမှန်လွှဲနေကျအတိုင်း လွှဲမည့်ငွေပမာဏဖြည့်ပြီး ပုံမှာပြထားသည့်အတိုင်း Note (မှတ်ချက်) မှာ “ငွေသွင်းကုဒ်” သို့မဟုတ် "Online Shop” ဟုမှန်ကန်စွာဖြည့်ပေးပါရှင့်..ငွေလွှဲပြီးသွား ရင်တော့ ငွေသွင်းရန်ထဲပြန်ဝင်ပီးတော့ ကော်ပီထပ်နှိပ်ပြီး ဖြည့်ရမယ့်အကွက်ပေါ်လာလျှင် လုပ်ငန်းစဉ် id နှင့် လွှဲထားသည့်ငွေပမာဏကိုမှန်ကန်စွာဖြည့်စွက်ပြီး“Confirm”နိပ်ပေးရပါမယ်ရှင့်.. လွယ်ကူအောင် ပုံလေးတွေနဲ့ ရှင်းပြပေးထားလို့သေချာကြည့်ပေးပါအုံးရှင့်...
<img src="../../static/deepseek/test/q1-4.jpg"><br/>
ငွေလွှဲမည်ကိုနှိပ်ပါ... COPY ယူထားသောနံပါတ်အား ဖုန်းနံပါတ်ထည့်ပါနေရာတွင် ကူးထည့်ပြီးဆက်လုပ်ပါကိုနှိပ်ပါ။
<img src="../../static/deepseek/test/q1-5.jpg"><br/>
မိမိထည့်လိုသောငွေပမာဏအား ရိုက်ထည့်ပြီးဆက်လုပ်ပါကိုနှိပ်ပါ။ ငွေလွှဲပြီးနောက်ပေါ်လာသော စာမျက်နှာရှိ လုပ်ဆောင်ချက်အိုင်ဒီအား ကူးယူပြီးINWA APP ဆီပြန်သွားပါ။ ယခုနေရာတွင်မိမိလွှဲခဲ့သော ငွေပမာဏနှင့်လုပ်ဆောင်ချက် အိုင်ဒီအားဖြည့်ပြီးCONFIRM နှိပ်ပါ။
မှတ်ချက်- Wave Money ID နှင့် ငွေပမာဏမှန်ကန်စွာတင်သော်လည်း Error ပြလာပါက မိနစ်အနည်းငယ် စောင့်ဆိုင်ပြီးပြန်တင်ပေးလိုက်ယုံဖြင့် အကောင့်ထဲငွေဝင်လာမည်ဖြစ်ပါတယ်ရှင့်..
<img src="../../static/deepseek/test/q1-6.jpg"><br/>`,
						},
						{
							value: 'အင်းဝအကောင့်ဖွင့်ချင်လို့ပါ',
							answer: `အင်းဝအကောင့်ဖွင့်လှစ်ရန်အတွက် Google Chrome သို့မဟုတ် Phone Browser ထဲတွင် www.innwamaung.com ဟုမှန်ကန်စွာရိုက်ထည့်ပြီး ရှာပေးပါနော်.. အင်းဝ၏ဝပ်ဆိုက်ထဲသို့ရောက်ပြီဆိုပါက ပုံထဲတွင်ပြထည့်အတိုင်း ပေါ်လာမှာဘဲဖြစ်ပါတယ်ရှင့် ... ပုံမှာပြထားသည့်အတိုင်း ဒေါင်းလုပ်ဆွဲရန်နေရာတွင် ANDROID (OR) IOS ရွေးပေးပါ အင်းဝဆော့ဝဲဒေါင်းပြီးပါက register ကိုနှိပ်ပါ။ ဖုန်းနံပါတ် နှင့် အမည် အသုံးပြုမည့် လျှို့ဝှက်နံပါတ်ကိုဖြည့်စွက်ပြီး အတည်ပြုမည် ကိုနှိပ်ပါကအကောင့်ဖွင့်လှစ်ခြင်းပြီးဆုံးပါပြီရှင့်…မှတ်ချက် - အင်းဝအကောင့်ဖွင့်လှစ်ထားသော နာမည်နှင့် ဖုန်းနံပါတ်သည်ဘဏ်အကောင့်အချက်များနှင့်ကိုက်ညီ မှရှိမှာသာငွေထုတ်ဆောင်ရွက်နိုင်မည်ဖြစ်ပါတယ်ရှင့်...<img src="../../static/deepseek/test/q2-1.jpg"><br/>မိမိအသုံးပြုလိုသော APP ကို ရွေးချယ်ကာဒေါင်းလုတ်ဆွဲပါ။ ဒေါင်းလုတ်ဆွဲပြီးနောက် ဖုန်းတွင်INSTALL လုပ်ပါ။ INNWA APP ထဲတွင် အချက်အလက်များကိုဖြည့်ကာ အတည်ပြုမည်ကိုနှိပ်ပါ။<img src="../../static/deepseek/test/q2-2.jpg"><br/>`,
						},
						{
							value: 'ငွေထုတ်ချင်လို့ပါ',
							answer: `ငွေထုတ်မည်ဆိုပါက ကိုယ်ရေးအချက်လက်ထဲရှိ ငွေထုတ်ရန်ထဲသို့ဝင်ပြီး ထုတ်ယူမည့် ပမာဏဖြည့် ပေးရပါမည်။ အနည်းဆုံး (10,000)ကျပ်မှစတင်၍ အကန့်သတ်မရှိထုတ်ယူနိုင်ပါသည်။
သတိပြုရန်အချက်မှာ (OK) အားအကြိမ်ကြိမ်နှိပ်ပါကဆက်တိုက်ငွေထုတ်တင်ထားသလိုဖြစ်မည်ဖြစ်ပါသဖြင့် တစ်ကြိမ်နှိပ်ပြီးပြန်ထွက်လျှင်ရပါပီရှင့်။
ငွေထုတ်မှတ်တမ်းကိုနှိပ်ပါ ငွေထုတ်ကုဒ်နေရာတွင် ABC နှင့် ဂဏာန်း 6 လုံးပါပါမည်။
ငွေထုတ်ကုဒ်မှာ A ပါရင် https://innwa.link/withdraw1
ငွေထုတ်ကုဒ်မှာ B ပါရင် https://innwa.link/w2 မှာပြောလိုက်ပါ
ငွေထုတ်ကုဒ်မှာ C ပါရင် https://cutt.ly/viberinnwawd3 မှာပြောလိုက်ပါ
telegram အသုံးပြုတယ်ဆိုရင် ဒီလင့်ကနေသွားလိုရပါတယ်
ငွေထုတ်ကုဒ်မှာ A ပါရင် https://innwa.link/telegram/w1
ငွေထုတ်ကုဒ်မှာ B ပါရင် https://innwa.link/telegram/w2
ငွေထုတ်ကုဒ်မှာ C ပါရင် https://cutt.ly/telegraminnwawd3
အသေးစိတ်အားပုံလေးနှင့်တကွရှင်းပြပေးထားလို့ သေချာစွာဖတ်ကြည့်ပေးပါအုံးရှင့်…
<img src="../../static/deepseek/test/q3-1.jpg"><br/>
အနည်းဆုံးထုတ်ငွေ ၁၀၀၀၀ကျပ်မှ စတင်ထုတ်ယူနိုင်ပြီးငွေထုတ်ပမာဏ ထည့်ပြီးပါက OK ကိုနှိပ်ပါ။ ငွေထုတ်မှတ်တမ်းတွင်ရှိသော ငွေထုတ်ကုဒ်များအား မှတ်သားထားပါ၊ ထို့နောက် ကိုယ်ရေးအချက်အလက်အောက်ရှိ ဆက်သွယ်ရန် ကိုနှိပ်ပါ။
<img src="../../static/deepseek/test/q3-2.jpg"><br/>
(ဆက်ရန် Page 11 တွင်) ငွေထုတ်လင့်နေရာတွင် ငွေထုတ်ကုတ်ရှိ စာလုံးများအလိုက်လင့်အားရွေးချယ်နှိပ်ပါ။ မိမိ၏ငွေထုတ်ကုဒ်ရှေ့တွင်ပါဝင်သော စာလုံးများအားငွေထုတ်မှတ်တမ်းတွင် ပြန်လည်စစ်ဆေးနိုင်ပါသည်။
<img src="../../static/deepseek/test/q3-3.jpg"><br/>`,
						},
						{
							value: 'ငွေသွင်းရမည့်ဘဏ်အကောင့်နံပါတ်လေးပို့ပေးပါ ',
							answer: 'အင်းဝဆော့ဝဲထဲမှ ကိုယ်ရေး အချက်လက်ထဲဝင်ပါ ဆက်သွယ်ရန်ကိုနှိပ်ပါပေးထားသော ငွေသွင်းရန်လင့်များမှ တဆင့် ငွေသွင်းနံပါတ်အားတောင်းခံနိုင်ပါသည်။<br/>',
						},
					]
				},
				submitLoading: false,
				answerKeyword: undefined,
				// answerKeyword: 'ငွေဘယ်လိုသွင်းရပါသလဲ',
				conversation_id: uni.getStorageSync('c_id') || '',
				ai_user: uni.getStorageSync('ai_user') || '',
				answerList: uni.getStorageSync('answerList') || [
					// {
					// 	role:'assistant',
					// 	content:'testtest![测试图片](https://samplelib.com/lib/preview/jpeg/sample-clouds-400x300.jpg "测试图片")',
					// }
				],
				// 会话记录
				chatHistory: {
					list: [],
					questionId: undefined,
				}
			}
		},
		mounted() {
			this.getChatList()
			// 检查最后一条消息是否为加载状态
			if (this.answerList.length > 0) {
				const lastMessage = this.answerList[this.answerList.length - 1]
				if (lastMessage.role === 'assistant' && lastMessage.content === 'ဖတ်ရှုနေပါသည်…') {
					// 找到对应的用户问题
					let userQuestion = ''
					if (this.answerList.length >= 2) {
						const secondLastMessage = this.answerList[this.answerList.length - 2]
						if (secondLastMessage.role === 'user') {
							userQuestion = secondLastMessage.content
						}
					}
					// 删除最后两条消息（用户问题和加载回答）
					this.answerList.splice(-2, 2)
					// 将问题填入输入框
					if (userQuestion) {
						this.answerKeyword = userQuestion
					}
					// 保存更新后的消息列表
					this.save_answer_list()
				}
			}
			// 延迟滚动，等待DOM更新完成
			this.$nextTick(() => {
				setTimeout(() => {
					this.scroll_to_bottom()
				}, 500)
			})
		},
		beforeDestroy() {
			this.stopLoadingAnimation()
		},

		methods: {
			navigateToHome() {
				// Open baidu.com in current window
				// #ifdef H5
				window.location.href = 'https://innwasport.com/';
				// #endif

				// #ifdef APP-PLUS
				plus.runtime.openURL('https://innwasport.com/');
				// #endif

				// #ifdef MP
				// uni.showToast({
				// 	title: '请在浏览器中打开',
				// 	icon: 'none'
				// });
				// #endif
			},
			toggleMoreMenu() {
				this.showMoreMenu = !this.showMoreMenu;
			},
			closeMoreMenu() {
				this.showMoreMenu = false;
			},
			toggleNotification() {
				this.notificationEnabled = !this.notificationEnabled;
				uni.setStorageSync('notificationEnabled', this.notificationEnabled);
				this.showMoreMenu = false;

				uni.showToast({
					title: this.notificationEnabled ? 'Notification sounds have been turned on.' :
						'Notification sounds have been turned off.',
					icon: 'none',
					duration: 1500
				});
			},
			showServiceNotAvailable() {
				this.showMoreMenu = false;
				uni.showModal({
					title: 'Notice',
					content: 'Service is not available now',
					showCancel: false,
					confirmText: 'OK',
					success: function(res) {}
				});
			},
			playNotificationSound() {
				if (!this.notificationEnabled) return;

				// #ifdef APP-PLUS
				const audio = uni.createInnerAudioContext();
				audio.src = '/static/image/ai/notification.mp3';
				audio.play();
				audio.onError((res) => {
					console.error('音频播放失败:', res);
				});
				// #endif

				// #ifdef H5
				try {
					const audio = new Audio('/static/image/ai/notification.mp3');
					audio.play().catch(e => {
						console.error('音频播放失败:', e);
					});
				} catch (e) {
					console.error('音频创建失败:', e);
				}
				// #endif
			},
			startLoadingAnimation() {
				let dotCount = 0;
				this.loadingInterval = setInterval(() => {
					dotCount = (dotCount + 1) % 4;
					this.loadingDots = '.'.repeat(dotCount);
				}, 500);
			},
			stopLoadingAnimation() {
				if (this.loadingInterval) {
					clearInterval(this.loadingInterval);
					this.loadingInterval = null;
					this.loadingDots = '';
				}
			},
			async getSuggestedReplies(messageId) {
				if (!messageId || !this.request_url || !this.request_token) {
					return;
				}

				try {
					const url =
						`${this.request_url}/v1/messages/${messageId}/suggested?user=${this.ai_user || 'abc-123'}`;
					const auth = `Bearer ${this.request_token}`;

					this.$http.get(url, {
						'Authorization': auth,
						'Content-Type': 'application/json'
					}, (res) => {
						console.log('建议回复API响应:', res);
						if (res.statusCode === 200 && res.data.result === 'success') {
							this.suggestedReplies = res.data.data || [];
							// 获取到建议回复后重新滚动到底部
							if (this.suggestedReplies.length > 0) {
								this.$nextTick(() => {
									setTimeout(() => {
										this.scroll_to_bottom();
									}, 200);
								});
							}
						} else {
							console.log('建议回复API错误:', res.data);
							this.suggestedReplies = [];
						}
					}, (err) => {
						console.error('获取建议回复失败:', err);
						this.suggestedReplies = [];
					});
				} catch (error) {
					console.error('获取建议回复异常:', error);
					this.suggestedReplies = [];
				}
			},
			selectSuggestedReply(reply) {
				this.answerKeyword = reply;
				this.suggestedReplies = [];
				// 延迟滚动到底部，等待DOM更新
				this.$nextTick(() => {
					setTimeout(() => {
						this.scroll_to_bottom();
					}, 150);
				});
			},
			formatMessageTime(timestamp) {
				if (!timestamp) return '';
				const date = new Date(timestamp);
				const day = date.getDate();
				const month = date.getMonth() + 1;
				const year = date.getFullYear();
				const hours = date.getHours();
				const minutes = date.getMinutes();
				const ampm = hours >= 12 ? 'PM' : 'AM';
				const displayHours = hours % 12 || 12;
				const formattedMinutes = minutes.toString().padStart(2, '0');

				return `${day}.${month}.${year} ${displayHours}:${formattedMinutes} ${ampm}`;
			},
			shouldShowTimeHeader(index) {
				// 不在answerList的第一条消息显示时间，因为时间应该显示在欢迎消息上方
				if (index === 0) return false;

				const current = this.answerList[index];
				const previous = this.answerList[index - 1];

				if (!current.timestamp || !previous.timestamp) return false;

				const currentTime = new Date(current.timestamp);
				const previousTime = new Date(previous.timestamp);
				const diffInMinutes = (currentTime - previousTime) / (1000 * 60);

				return diffInMinutes >= 5; // 间隔5分钟以上显示时间
			},
			isLastMessage(index) {
				return index === this.answerList.length - 1;
			},
			// navigate_dafult_option(e, item) {
			// 	this.show_navigate = false
			// 	let qa = JSON.parse(JSON.stringify(item))
			// 	console.log(qa)
			// 	// this.answerKeyword = answer.value
			// 	this.answerList.push({
			// 		role: 'user',
			// 		content: qa.value,
			// 	})
			// 	this.answerList.push({
			// 		role: 'assistant',
			// 		content: qa.answer,
			// 	})
			// 	// this.scroll_to_bottom()
			// 	return
			// 	this.onSubmit(event)
			// },
			load_config() {
				if (!this.config.ai_helper_token) {
					let config = this.$store.state.configs;
					this.config = config
					this.request_token = config.ai_helper_token
					this.request_url = config.ai_helper_host
				}
			},
			input_request_conf(e, attr) {
				let value = e.detail.value
				uni.setStorageSync(attr, value)
			},
			onClickCreateChat() {
				if (this.chatHistory.list.length >= 10) {
					return uni.showToast({
						title: '您最多可同时建立10个对话，如需新建对话，请先删除会话！',
						icon: 'none'
					})
				}
				this.chatHistory.questionId = undefined
				this.answerList = []
				this.answerKeyword = undefined
			},
			onClickEditTitle(item) {
				this.chatHistory.list.map(item => item._edit = false)
				item._edit = true
				this.$nextTick(() => {

				})
			},

			saveChatTitle(item) {
				uni.showToast({
					title: '触发修改',
					icon: 'none'
				})
				this.getChatList()
			},
			confirmDeletion(item) {
				uni.showModal({
					title: '提示',
					content: '确定删除吗'
				})
			},
			onClickDefaultQuestion(event, item) {
				let qa = JSON.parse(JSON.stringify(item))
				console.log(qa)
				// this.answerKeyword = answer.value
				this.answerList.push({
					role: 'user',
					content: qa.value,
				})
				this.answerList.push({
					role: 'assistant',
					content: qa.answer,
				})
				this.scroll_to_bottom()
				return
				this.onSubmit(event)
			},

			getChatList() {
				setTimeout(() => {
					this.chatHistory.list = [{
						"id": 31,
						"title": "统计学专业就业好不好？",
						"createDate": "2024-07-31 15:13:49",
						"updateDate": null,
						"itemList": [{
								"id": 136,
								"questionId": 30,
								"role": "user",
								"content": "统计学专业就业好不好？",
								"createDate": "2024-07-31 15:13:49",
								"updateDate": null
							},
							{
								"id": 137,
								"questionId": 30,
								"role": "assistant",
								"content": "#### 统计学专业的就业前景相对较好，具有广阔的发展空间。",
								"reasoning_content": "统计学专业的就业前景相对较好，具有广阔的发展空间。",
								"createDate": "2024-07-31 15:13:49",
								"updateDate": null
							}
						]
					}]
				}, 1000);
				this.chatHistory.list.map(item => {
					item._edit = false
					item._editTitle = item.title
					return item
				})
			},

			onClickChatItem(item) {
				this.chatHistory.questionId = item.id
				this.answerList = item.itemList
				this.$nextTick(() => {
					let elem = document.querySelector('.answerMain-bd')
					elem.scrollTop = elem.scrollHeight
				})
			},
			clear_message() {
				if (this.submitLoading) return
				let _this = this
				_this.showMoreMenu = false
				uni.showModal({
					title: 'Tips',
					content: 'Click OK to clear history!',
					confirmText: 'OK',
					cancelText: 'Cancel',
					complete: function(res) {
						if (res.confirm) {
							uni.removeStorageSync('c_id')
							uni.removeStorageSync('answerList')
							uni.removeStorageSync('ai_user')
							_this.conversation_id = ''
							_this.ai_user = ''
							_this.answerList = []
						}
					}
				})
			},
			save_answer_list(data) {
				uni.setStorageSync('answerList', this.answerList)
				uni.setStorageSync('ai_user', this.ai_user)
				if (data && data.conversation_id) {
					let c_id = data.conversation_id
					this.conversation_id = c_id
					uni.setStorageSync('c_id', c_id)
				}
			},
			async onSubmit(event) {
				this.load_config()
				if (event.keyCode === 13 || event.key === "Enter") {
					event.preventDefault(); // 阻止默认行为，即回车换行
					if (event.shiftKey) {
						this.answerKeyword += "\n";
					}
				}
				if (!this.answerKeyword) {
					return uni.showToast({
						title: 'Please Enter',
						icon: 'none'
					})
				}
				if (this.submitLoading) return
				this.submitLoading = true
				this.suggestedReplies = []
				this.answerList.push({
					role: 'user',
					content: this.answerKeyword,
					timestamp: new Date()
				})
				this.scroll_to_bottom()
				let auth = `Bearer ${this.request_token}`
				let url = this.request_url + '/v1/chat-messages'
				let user = this.ai_user || this.$toolbox.generate_uid()
				this.ai_user = user
				const _this = this
				let para = {
					"inputs": {},
					// "query": "回复我好的",
					"query": _this.answerKeyword,
					// "response_mode": "streaming",
					"response_mode": "blocking",
					"conversation_id": _this.conversation_id,
					"user": `${user}`,
					"files": []
				}
				let answer = {
					role: 'assistant',
					content: 'ဖတ်ရှုနေပါသည်…',
					timestamp: new Date()
				}
				_this.answerList.push(answer)
				_this.save_answer_list()
				_this.startLoadingAnimation()
				// _this.answerKeyword = undefined
				setTimeout(() => {
					_this.$set(_this, 'answerKeyword', undefined)
				}, 0)
				_this.$http.post(url, para, {
					'Authorization': auth,
					'timeout': 300 * 1000,
				}, (res) => {
					// console.log(res)
					_this.submitLoading = false
					_this.stopLoadingAnimation()
					if (res.statusCode === 200) {
						let regex = /<think>([\s\S]*?)<\/think>([\s\S]*)/;
						let answer_list = res.data.answer.match(regex)
						answer.content = answer_list ? answer_list[2] : res.data.answer;

						// 播放通知音效
						_this.playNotificationSound();

						// 获取建议回复
						if (res.data.id) {
							_this.currentMessageId = res.data.id;
							_this.getSuggestedReplies(res.data.id);
						}

						// answer.content = res.data.answer
					} else {
						answer.content = 'error'
					}
					_this.save_answer_list(res.data)
					setTimeout(() => {
						_this.scroll_to_bottom()
					}, 500)

				})
			},
			// async onSubmit2(event) {
			// 	this.load_config()
			// 	console.log('event', event);
			// 	if (event.keyCode === 13 || event.key === "Enter") {
			// 		event.preventDefault(); // 阻止默认行为，即回车换行
			// 		if (event.shiftKey) {
			// 			this.answerKeyword += "\n";
			// 		}
			// 	}
			// 	if (!this.answerKeyword) {
			// 		return uni.showToast({
			// 			title: 'Please Enter',
			// 			icon: 'none'
			// 		})
			// 	}
			// 	if (this.submitLoading) return
			// 	this.submitLoading = true
			// 	this.answerList.push({
			// 		role: 'user',
			// 		content: this.answerKeyword,
			// 	})
			// 	this.scroll_to_bottom()
			// 	let auth = `Bearer ${this.request_token}`
			// 	let url = this.request_url + '/v1/chat-messages'
			// 	// let auth = `Bearer app-4Qf4UO276qOFXqLiUefEluZN` //简单问答
			// 	// let auth = `Bearer app-ztWVq6vx9DeOersg0U9pMJDs`
			// 	// let url = 'http://192.168.99.10/v1/chat-messages'

			// 	const _this = this
			// 	let answer = {
			// 		role: 'assistant',
			// 		content: 'ဖတ်ရှုနေပါသည်…',
			// 		// reasoning_content: answer_list[1] || '',
			// 	}
			// 	_this.answerList.push(answer)
			// 	_this.startLoadingAnimation()

			// 	function errorOccur() {
			// 		_this.submitLoading = false
			// 		_this.stopLoadingAnimation()
			// 		_this.answerKeyword = undefined
			// 		answer.content = 'error'
			// 	}
			// 	let regex = /<think>([\s\S]*?)<\/think>([\s\S]*)/;
			// 	let user = new Date().getTime()
			// 	let _answer = ''
			// 	let para = {
			// 		"inputs": {},
			// 		// "query": "回复我好的",
			// 		"query": _this.answerKeyword,
			// 		// "response_mode": "streaming",
			// 		"response_mode": "blocking",
			// 		"conversation_id": _this.conversation_id,
			// 		"user": `${user}`,
			// 		"files": []
			// 	}
			// 	_this.$http.post(url, para, {
			// 		Authorization: auth
			// 	}, (res) => {
			// 		_this.stopLoadingAnimation()
			// 		if (res.data.code == 20000) {
			// 			let answer_list = _answer.match(regex)
			// 			_answer = answer_list ? answer_list[2] : res.answer;
			// 			answer.content = _answer
			// 			_this.answerKeyword = undefined
			// 			_this.scroll_to_bottom()

			// 		} else {
			// 			errorOccur()
			// 		}
			// 	})
			// 	return
			// 	let response = await fetch(url, {
			// 		method: "POST",
			// 		headers: {
			// 			// satoken: sessionStorage.getItem("satoken"),
			// 			// userId: sessionStorage.getItem("userId"),
			// 			'Authorization': auth,
			// 			'Content-Type': 'application/json',
			// 			// 'Content-Type': 'application/json; charset=utf-8',
			// 			// 'Content-Type': 'text/event-stream',
			// 			// 'Access-Control-Allow-Origin': '*',
			// 			// 'Access-Control-Allow-Origin': '*',
			// 		},
			// 		// body: JSON.stringify({
			// 		// 	questionId: this.chatHistory.questionId,
			// 		// 	list: this.answerList.slice(-30),
			// 		// }),
			// 		body: JSON.stringify({
			// 			"inputs": {},
			// 			// "query": "回复我好的",
			// 			"query": _this.answerKeyword,
			// 			// "response_mode": "streaming",
			// 			"response_mode": "blocking",
			// 			"conversation_id": "",
			// 			"user": `${user}`,
			// 			"files": []
			// 		})
			// 	}).catch(error => {
			// 		errorOccur()
			// 	})
			// 	if (!response.ok) {
			// 		errorOccur()
			// 		throw new Error('Network response was not ok');
			// 	}
			// 	const reader = response.body.getReader();
			// 	// 定义一个函数来读取流数据
			// 	// this.answerList.push({
			// 	// 	role: 'assistant',
			// 	// 	content: '',
			// 	// 	reasoning_content: '',
			// 	// })
			// 	console.log(response)

			// 	function readStream() {
			// 		reader.read().then(({
			// 			done,
			// 			value
			// 		}) => {
			// 			// 如果流已经读取完毕
			// 			if (done) {
			// 				_this.submitLoading = false
			// 				console.log('_this', _this.answerList);
			// 				return;
			// 			}
			// 			// 处理当前读取到的数据块
			// 			let itemText = new TextDecoder().decode(value, {
			// 				stream: true
			// 			})
			// 			console.log(itemText)
			// 			// const itemText2 = itemText.replace(/\\u([\da-fA-F]{1,3})/g, (match, group) => {
			// 			//   return group.length === 4 ? match : `\\u${'0'.repeat(4 - group.length)}${group}`;
			// 			// });

			// 			// _this.processSSEChunk(itemText)
			// 			if (itemText.answer) {
			// 				_answer = itemText.answer
			// 			} else {
			// 				let res = JSON.parse(encodeURI(itemText))
			// 				// let res = eval("("+itemText+")");
			// 				_answer = res.answer
			// 			}
			// 			let answer_list = _answer.match(regex)
			// 			_answer = answer_list ? answer_list[2] : res.answer;
			// 			answer.content = _answer
			// 			_this.answerKeyword = undefined
			// 			// console.log('res',res)
			// 			// console.log('answer_list',answer_list)
			// 			// 继续读取下一个数据块
			// 			readStream();
			// 			_this.scroll_to_bottom()
			// 		}).catch(error => {
			// 			console.error('Error reading stream:', error);
			// 			errorOccur()
			// 		});
			// 	}

			// 	// 开始读取流
			// 	readStream();
			// },
			scroll_to_bottom() {
				let _this = this
				// 先设置scroll_top为一个很大的值
				_this.$set(_this, 'scroll_top', 999999)
				// 同时使用scroll_into_view确保滚动到底部
				_this.$set(_this, 'scroll_into_view', null)
				_this.$nextTick(() => {
					setTimeout(() => {
						_this.$set(_this, 'scroll_into_view', 'scroll-bottom')
						_this.$forceUpdate()
					}, 50)
				})
			},
			processSSEChunk(chunk) {
				// 按行拆分数据块
				this.buffer += chunk
				const lines = this.buffer.split('data:')
				// 检查最后一行是否完整
				if (!chunk.endsWith('\n')) {
					// 如果最后一行不完整，保留在缓冲区中
					this.buffer = lines.pop();
				} else {
					// 如果最后一行完整，清空缓冲区
					this.buffer = '';
				}
				lines.forEach((line, index) => {
					// 检查是否是SSE格式的数据行
					// 提取JSON部分
					const jsonString = line;
					// 如果JSON部分不为空，则解析
					if (jsonString === '[DONE]') {
						this.answerList[this.answerList.length - 1].content += ''
					} else if (jsonString !== '') {
						try {
							const jsonData = JSON.parse(jsonString);
							if (jsonData.questionId && !this.chatHistory.questionId) {
								this.getAIChatList()
								this.chatHistory.questionId = jsonData.questionId
							}
							if (jsonData.reasoning_content) {
								this.answerList[this.answerList.length - 1].reasoning_content += jsonData
									.reasoning_content
							} else if (jsonData.content) {
								this.answerList[this.answerList.length - 1].content += jsonData.content
							}
						} catch (error) {
							console.log('parsing JSON错误', jsonString, index);
							console.log('parsing JSON错误', error);
						}
					}
					// this.$nextTick(() => {
					// let elem = document.querySelector('.answerMain-bd')
					// elem.scrollTop = elem.scrollHeight
					// window.scrollTo(0, document.body.scrollHeight)
					// })
				});
			},
		},
	}
</script>

<style lang="scss" scoped>
	uni-page-body,
	html,
	body {
		height: 100%;
	}

	.page {
		// background: #f9f9f9;
		background-image: url('/static/background.png');
		background-size: cover;
		background-position: center;
		background-repeat: no-repeat;
		height: 100%;
	}

	/* Custom header styles */
	.custom-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		height: 44px;
		// padding: 0 15px;
		background: transparent;
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		z-index: 1000;
		width: 100%;
		box-sizing: border-box;
	}

	.header-left {
		width: 44px;
		height: 44px;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.header-center {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		position: absolute;
		left: 50%;
		transform: translateX(-50%);
	}

	.header-title {
		color: #6A0003;
		font-family: Poppins;
		font-weight: bold;
		font-style: italic;
		font-size: 16px;
		text-align: center;
	}

	.header-right {
		width: 44px;
		height: 44px;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.more-icon {
		width: 20px;
		height: 20px;
	}

	.flex {
		display: flex;
	}

	.align-center {
		align-items: center;
	}

	::v-deep .cu-custom {
		background: transparent !important;
		background-color: transparent !important;
	}

	::v-deep .cu-custom .cu-bar {
		background: transparent !important;
		background-color: transparent !important;
	}

	::v-deep .cu-custom .cu-bar.fixed {
		background: transparent !important;
		background-color: transparent !important;
	}

	::v-deep .cu-custom .content {
		color: #6A0003 !important;
		font-family: Poppins;
		font-weight: bold;
		font-style: Italic;
		font-size: 16px;
		leading-trim: NONE;
		letter-spacing: 0%;
		text-align: center;
		vertical-align: middle;

	}

	::v-deep .cu-custom .cu-bar .content {
		color: #6A0003 !important;
	}

	.modify-icon {
		display: inline-block;
		font-size: 14px;
		padding: 5px;
		cursor: pointer;

		&:hover {
			background: #e1e5fa;
			border-radius: 4px;
			color: PrimaryColor;
		}
	}

	.createChat-button {
		font-size: 14px;
	}

	.defaultQuestion-title {
		color: #05073b;
		font-size: 20px;
		font-weight: 600;
		line-height: 36px;
		margin-bottom: 8px;
	}

	.defaultQuestion {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		column-gap: 10px;
	}

	.defaultQuestion-item {
		padding: 6px;
		background: #E2E2E2;
		border-radius: 6px;
		margin-top: 10px;
		cursor: pointer;
		font-size: 13px;
		font-weight: 600;

		.modify-icon {
			font-size: 16px;

			&:hover {
				background: unset;
			}
		}

		&:hover {
			background: #e9ecfb;
			color: PrimaryColor;
		}
	}

	.answer {
		display: flex;
		justify-content: center;
		// height: 100%;
		// padding: 10px;
		box-sizing: border-box;
	}

	.answerLeft {
		width: 280px;
		margin-right: 10px;
		background: linear-gradient(180deg, #f5f4f6, #e6ebf7);
		border-radius: 8px;
		padding: 15px 10px 0 10px;
	}

	.answerLeft-deleteConfirm {
		padding: 12px 0;
		text-align: center;
	}

	.answerLeft-deleteConfirm__btn {
		width: 92px;
		height: 32px;
		line-height: 32px;
		padding: 0 4px;
	}

	.modify-title {
		border: 1px solid #dcdfe6;
		height: 32px;
		line-height: 32px;
		border-radius: 8px;
		width: 100%;
		padding: 0 12px;
	}

	.answerMain {
		// padding-top: 9px;
		padding-bottom: 120px;
		font-size: 12px;
		display: flex;
		flex-direction: column;
		// background: linear-gradient(180deg, #f5f4f6, #e6ebf7);
		width: 100vw;
		border-radius: 8px;
	}

	.answerMain-bd {
		// flex-grow: 1;
		// height: 0;
		// overflow-y: auto;
		flex-direction: column;
		display: flex;
		background: unset;
		box-sizing: border-box;

		&::-webkit-scrollbar-thumb {
			border-radius: 4px;
			background: rgba(108, 119, 143, 0.3);
		}

		&::-webkit-scrollbar {
			height: 20px;
			width: 4px;
		}
	}

	.answerMain-ft {
		flex-shrink: 0;
		min-height: 50px;
		// padding: 12px 32px 10px 32px;
		box-sizing: border-box;
		// background: rgb(238, 240, 247);
	}

	.chatHistory-item {
		display: flex;
		align-items: center;
		padding: 0 10px 0 0;
		margin-top: 10px;

		&:hover {
			.chatHistory-item__handle {
				display: block;
			}
		}
	}

	.chatHistory-item:hover,
	.chatHistory-item.is-active {
		background: rgba(255, 255, 255, 0.9);
		border-radius: 8px;
		box-shadow: 0 16px 20px 0 rgba(173, 167, 224, 0.06);
		color: initial;
	}

	.chatHistory-item__hd {
		flex-shrink: 0;
	}

	.chatHistory-item__bd {
		flex: 1;
		color: #000c3f;
		cursor: pointer;
		display: flex;
		align-items: center;
		font-size: 14px;
		font-weight: 400;
		height: 50px;
		line-height: 50px;
		overflow: hidden;
		padding: 0 10px 0 10px;
		position: relative;
		text-align: justify;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.chatHistory-item__handle {
		flex-shrink: 0;
		display: none;
	}

	.answerMain-item {
		padding: 6px 24px;
		color: #05073b;
		position: relative;
		display: flex;

		&.roleUser {
			justify-content: end;

			.answerMain-item__avatar {
				left: unset;
				right: 40px;
			}
		}

		&:last-child {
			margin-bottom: 10px;
		}
	}

	.answerMain-item__avatar {
		width: 26px;
		height: 26px;
		border-radius: 50%;
		position: absolute;
		bottom: 6px;
		left: 2px;
	}

	.answerMain-item__content {
		background: #fdfdfe;
		border-radius: 12px 12px 12px 0;
		box-shadow: 0 16px 20px 0 rgba(174, 167, 223, 0.06);
		display: flex;
		flex-direction: column;
		padding: 12px 20px;
		position: relative;
		font-size: 12px;
		line-height: 1.5;
		// min-height: 50px;
		box-sizing: border-box;
		flex: 1;
	}

	/* 等待状态时隐藏对话框背景 */
	.answerMain-item__content.loading {
		background: transparent !important;
		box-shadow: none !important;
		border-radius: 0 !important;
		padding: 0 !important;
		margin-left: 10px;
	}

	/* 等待状态时调整头像位置 */
	.answerMain-item:has(.answerMain-item__content.loading) .answerMain-item__avatar {
		bottom: 6px !important;
	}

	.answerMain-item.roleUser .answerMain-item__content {
		background: #6A0003;
		color: white;
		border-radius: 12px 12px 0 12px;
	}

	.answerMain-item__outputReasonContent {
		color: #666;
		border-left: 3px solid #ddd;
		padding-left: 13px;
		// margin: 5px 0;
		line-height: 1.25;
	}

	.answerMain-input {
		background: #fff;
		padding: 12px 16px;
		box-shadow: 0 16px 20px 0 rgba(174, 167, 223, 0.2);
		min-height: 50px;
	}

	.answerMain-input__textarea {
		height: 50px;
		width: 100%;

		::v-deep {
			.el-textarea__inner {
				border: none;
				resize: none;
				color: #05073b;
			}
		}
	}

	.answerMain-input__button {
		font-size: 12px;
		align-self: end;
		margin: 0;
		width: 53px;
		height: 24px;
		border-radius: 12px;
		background-color: #890006;
		color: white;
		line-height: 24px;
	}

	/* More菜单弹框样式 */
	.more-menu-dropdown {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		z-index: 1000;
		// background: rgba(0, 0, 0, 0.3);
		display: flex;
		justify-content: flex-end;
		align-items: flex-start;
		padding-top: 50px;
		padding-right: 10px;
	}

	.more-menu-content {
		background: white;
		border-radius: 8px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
		min-width: 150px;
		overflow: hidden;
		animation: slideInDown 0.2s ease-out;
	}

	@keyframes slideInDown {
		from {
			opacity: 0;
			transform: translateY(-10px);
		}

		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.more-menu-item {
		display: flex;
		align-items: center;
		padding: 12px 16px;
		border-bottom: 1px solid #f0f0f0;
		cursor: pointer;
		transition: background-color 0.2s;
	}

	.more-menu-item:last-child {
		border-bottom: none;
	}

	.more-menu-item:hover {
		background-color: #f5f5f5;
	}

	.more-menu-item:active {
		background-color: #e8e8e8;
	}

	.more-menu-icon {
		width: 16px;
		height: 16px;
		margin-right: 8px;
		flex-shrink: 0;
	}

	.more-menu-text {
		font-size: 14px;
		color: #333;
		flex: 1;
		line-height: 1.2;
	}

	/* 建议回复样式 */
	.suggested-replies {
		padding: 8px 0 0 0;
		// background: #fff;
		animation: slideInUp 0.3s ease-out;
	}

	@keyframes slideInUp {
		from {
			transform: translateY(50px);
			opacity: 0;
		}

		to {
			transform: translateY(0);
			opacity: 1;
		}
	}

	.suggested-replies-scroll {
		width: 100%;
		height: 50px;
		white-space: nowrap;
	}

	.suggested-replies-container {
		display: flex;
		align-items: center;
		height: 100%;
		gap: 8px;
	}

	.suggested-reply-item {
		flex-shrink: 0;
		padding: 8px 16px;
		background: #fff;
		border-radius: 12px;
		font-size: 12px;
		color: #333;
		box-shadow: 0px 1px 1px 0px #00000040;
		cursor: pointer;
		transition: all 0.2s ease;
		white-space: nowrap;
		min-width: fit-content;
		animation: slideInUpItem 0.4s ease-out both;
	}

	@keyframes slideInUpItem {
		from {
			transform: translateY(30px);
			opacity: 0;
			scale: 0.9;
		}

		to {
			transform: translateY(0);
			opacity: 1;
			scale: 1;
		}
	}

	.suggested-reply-item:first-child {
		margin-left: 10px;
	}

	.suggested-reply-item:hover {
		background: #e8e8e8;
		border-color: #d0d0d0;
	}

	.suggested-reply-item:active {
		margin-left: 5px;
		background: #ddd;
		transform: scale(0.98);
	}

	/* 时间显示样式 */
	.time-divider {
		margin: 10px 0;
	}

	.time-header-first {
		text-align: center;
		font-family: Myanmar Text, sans-serif;
		font-weight: 700;
		font-style: normal;
		font-size: 10px;
		line-height: 150%;
		color: #9C9C9C;
		padding: 5px 0;
	}

	.time-header-with-line {
		display: flex;
		align-items: center;
		margin: 10px 20px;
	}

	.time-line {
		flex: 1;
		height: 1px;
		background-color: #9C9C9C;
	}

	.time-text {
		font-family: Myanmar Text, sans-serif;
		font-weight: 700;
		font-style: normal;
		font-size: 10px;
		line-height: 150%;
		color: #9C9C9C;
		margin: 0 15px;
		white-space: nowrap;
	}

	.last-message-time {
		font-family: Myanmar Text, sans-serif;
		font-weight: 700;
		font-style: normal;
		font-size: 10px;
		line-height: 150%;
		color: #9C9C9C;
		text-align: right;
		margin: 5px 24px 10px 24px;
	}

	.last-message-time.ai-message-time {
		text-align: left;
	}

	/* AI加载动画样式 */
	.ai-loading-wrapper {
		display: flex;
		flex-direction: column;
		gap: 8px;
		align-items: flex-start;
	}

	.ai-loading-text {
		font-size: 12px;
		color: #666;
		animation: pulse 1.5s ease-in-out infinite alternate;
	}

	.ai-loading-animation {
		display: flex;
		gap: 4px;
		align-items: center;
	}

	.dot {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background-color: #6A0003;
		animation: bounce 1.4s ease-in-out infinite both;
	}

	.dot1 {
		animation-delay: -0.32s;
	}

	.dot2 {
		animation-delay: -0.16s;
	}

	.dot3 {
		animation-delay: 0s;
	}

	@keyframes pulse {
		0% {
			opacity: 0.6;
		}

		100% {
			opacity: 1;
		}
	}

	@keyframes bounce {

		0%,
		80%,
		100% {
			transform: scale(0);
			opacity: 0.5;
		}

		40% {
			transform: scale(1);
			opacity: 1;
		}
	}

	/* AI回答完成的过渡动画 */
	.ai-response-enter-active {
		transition: all 0.6s ease-out;
		transform-origin: top left;
	}

	.ai-response-leave-active {
		transition: all 0.3s ease-in;
	}

	.ai-response-enter-from {
		opacity: 0;
		transform: translateY(20px) scale(0.95);
	}

	.ai-response-enter-to {
		opacity: 1;
		transform: translateY(0) scale(1);
	}

	.ai-response-leave-from {
		opacity: 1;
		transform: scale(1);
	}

	.ai-response-leave-to {
		opacity: 0;
		transform: scale(0.95);
	}

	.ai-response-content {
		animation: typewriter 0.8s ease-out;
	}

	@keyframes typewriter {
		0% {
			max-height: 0;
			overflow: hidden;
		}

		100% {
			max-height: 1000px;
		}
	}

	/* 消息项入场动画 */
	.message-item-animate {
		animation: slideInFromBottom 0.5s ease-out both;
	}

	.user-message-animate {
		animation: slideInFromRight 0.4s ease-out;
	}

	@keyframes slideInFromBottom {
		0% {
			opacity: 0;
			transform: translateY(30px);
		}

		100% {
			opacity: 1;
			transform: translateY(0);
		}
	}

	@keyframes slideInFromRight {
		0% {
			opacity: 0;
			transform: translateX(20px);
		}

		100% {
			opacity: 1;
			transform: translateX(0);
		}
	}
</style>