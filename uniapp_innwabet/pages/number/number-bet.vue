<template>
	<view class="mybg-grey">
		<cu-custom isBack backUrl="/pages/index/index">
			<block slot="content">2D</block>
			<block slot="right">
				<view>
					<button class="cu-btn bg-blue margin-right-sm" @click="goto()">3D</button>
				</view>
			</block>
		</cu-custom>
		<form class="mybg-grey full-page">
			<view class="myrect flex-column text-bold" style="width: 96vw;margin: 5px 2vw;padding: 4px 0 4px 0;">
				<view class="flex-row" style="width: 96vw;justify-content: space-around;">
					<view class="myrect box-shadow bg-white rec2 flex-column mycolor-red">
						<text>{{language.close_time}}</text>
						<text style="height: 6vw;">{{Info.CLOSE_TIME}}</text>
					</view>
					<view class="myrect box-shadow bg-white rec2 flex-column mycolor-red" @click="to_total">
						<text>{{language.digit_total}}</text>
						<!-- <view class="flex-row" style="justify-content: space-around;height: 6vw;">
							<text class="mycolor-orange">{{Info.bet_sum_total ?Info.bet_sum_total : '0'}}</text>
						</view> -->
					</view>
					<view class="myrect box-shadow bg-white rec2 flex-column mycolor-red" @click="to_record">
						<text>{{language.digit_record}}</text>
						<!-- <view class="flex-row" style="justify-content: space-around;height: 6vw;">
						</view> -->
					</view>
				</view>
			</view>

			<view class="myrect box-shadow bg-white flex-column text-bold"
				style="width: 96vw;margin: 5px 2vw;padding: 2px 0 2px 0;">
				<view style="margin-top: 2px;">{{language.history_result}}</view>
				<view class="mybg-grey" style="width: 96vw;height: 2px;margin: 2px 0 2px 0"></view>
				<view class="flex-row" style="width: 96vw;margin: 1px;justify-content: space-around;">

					<view class="myrect mybg-dgrey flex-column"
						style="width: 17%;height: 17vw;margin: 1px;line-height: 6vw;" v-for="(day,index) in days"
						:key="index">
						<text>{{day}}</text>
						<view class="flex-row" style="justify-content: space-around;height: 6vw;">
							<text class="mycolor-red">{{Results[index + 1].am}}</text>
							<text class="mycolor-orange">{{Results[index + 1].pm}}</text>
						</view>
					</view>
				</view>
			</view>

			<view class="myrect box-shadow bg-white flex-column text-bold text-right"
				style="width: 96vw;margin: 10px 2vw;margin-top: 10px;">
				<view class="flex-row" style="justify-content: space-between;padding: 7px 12px 7px 12px;">
					<!-- <view class="title">{{language.pleaseInput}}</view> -->
					<button class='cu-btn shadow mybg-red' @click="modalName = 'play_info'">{{language.fast}}</button>

					<input style="width: 50%;" @input='onInput($event,2,1)' type="number" v-model="amount"></input>
				</view>
				<view class="mybg-grey" style="width: 96vw;height: 2px;margin: 5px 0 5px 0"></view>

				<view class="flex-row" style="justify-content: space-between;">
					<button class='cu-btn shadow margin-sm mybg-red'
						@tap="toPage('order')">{{language.digitorder}}</button>
					<view>
						<!-- <button class='cu-btn shadow margin-sm mybg-orange'
							@tap='resetAmount'>{{language.reset}}</button> -->

						<button class='cu-btn shadow mybg-orange'
							@click="clear_select">{{language.cancel_fast}}</button>
						<button class='cu-btn shadow margin-sm mybg-red' @tap="showModal">OK</button>
					</view>
				</view>

			</view>
			<scroll-view scroll-y class="myrect text-bold text-center" enable-flex
				style="margin-left: 0px;height: calc(100vh - 270px - 25vw);justify-content: space-around;width: 100vw;flex-direction: row;">
				<view class="cu-btn" :class="item.baned?'bg-black':item.selected ?'mybg-orange':'mybg-light-yellow'"
					@click="select_number(item,index)"
					style="width: 11.25vw;height: 11.25vw; border: rgb(235,227,223) solid 1rpx;margin: 1.25vw;flex-direction: column;border-radius: 1vw;justify-content: space-around;"
					v-for="(item,index) in number_2d_items" :key="index">
					<view>
						{{item.label}}
					</view>
					<view class="cu-progress round xs" style="width: 10vw" :class="item.baned?'hidden':''">
						<view :class="calc_num_percent(item) > 99? 'bg-red':calc_num_percent(item) > 60?'bg-yellow':'bg-blue'
						" :style="[{ width: calc_num_percent(item) + '%'}]"></view>
					</view>

				</view>
				<view style="width: 100%;height: calc((90vw )/16);"></view>
			</scroll-view>



			<view class="cu-modal" :class="modalName=='list_popup'?'show':''">
				<view class="cu-dialog">
					<view class="cu-bar bg-white justify-end">
						<view class="action" @tap="hideModal">
							<text class="cuIcon-close text-red"></text>
						</view>
					</view>
					<view class="padding-sm">
						<scroll-view scroll-y style="height:55vh">

							<view class="cu-form-group">
								<view style="width: 10%;" class="title text-bold">No.</view>
								<view style="width: 20%;" class="title text-bold">{{language.number}}</view>
								<view style="width: 35%;" class="title text-bold text-center">{{language.amount}}</view>
								<view class="title text-bold ">{{language.delete}}</view>
							</view>

							<view class="cu-form-group" v-for="(item,index) in betList" :key='index'>
								<view style="width: 10%;" class="title">{{index + 1}}</view>
								<view style="width: 20%;" class="title text-center">{{item.BET_TYPE}}</view>
								<view style="width: 35%;" class="title"><input :placeholder="language.betcontent"
										@input='onInput($event,1,index)' name="input" type="number"
										v-model="item.BET_MONEY"></input></view>
								<button class="cu-btn cuIcon-delete round mybg-red" @tap='delRow(index)'></button>
							</view>

						</scroll-view>
					</view>
					<form>
						<view class="cu-form-group">
							<view class="title">{{language.odds}}</view>
							<view
								style="border: 1px solid red; color:red;font-weight: bold;padding:8px;border-radius: 3px;">
								{{Info.ODDS?'1X' + Info.ODDS :''}}
							</view>
						</view>
						<view class="cu-form-group">
							<view class="title">{{language.amount}}</view>
							<view style=" color:red;font-weight: bold;padding:8px;border-radius: 3px;">
								{{cal_total_amount()}}
							</view>
						</view>
					</form>
					<view class="flex">
						<view class="basis-df ">
							<view class="cu-btn margin-sm shadow mybg-orange radius" @tap='resetRowAmount'>
								{{language.reset}}
							</view>
						</view>
						<view class="basis-df ">
							<view class="cu-btn margin-sm shadow radius" :class="saved ?'bg-grey':'mybg-red' "
								@tap="submit">OK</view>
						</view>
					</view>
				</view>
			</view>


			<view class="cu-modal" :class="modalName=='play_info'?'show':''">
				<form class="cu-dialog">
					<scroll-view scroll-y style="height: 65vh; width: 91vw;" class="mybg-dgrey">
						<view class="myrect" style="margin-bottom: 5px;width: 96%;margin-left: 2%;">
							<view class="cu-form-group text-bold">
								<view>{{language.double_and_size}}</view>
							</view>
							<view class="cu-form-group flex-column">
								<view class="flex-row">
									<button class="margin-bottom-sm margin-top-sm text-sm cu-btn"
										style="width: 18%;margin-right: 2%;padding: 0 0 0 0;"
										@click="get_numbers(item.value,'',language[item.lang_text])" v-if="index < 5"
										v-for="(item,index) in sod_items.button"
										:key="index">{{language[item.lang_text]}}</button>
								</view>
								<view class="flex-row">
									<button class="cu-btn margin-bottom-sm"
										style="width: 18%;margin-right: 2%;padding: 0 0 0 0;"
										@click="get_numbers(item.value,'',language[item.lang_text])" v-if="index > 4"
										v-for="(item,index) in sod_items.button"
										:key="index">{{language[item.lang_text]}}</button>
								</view>
							</view>
						</view>
						<view class="myrect" style="margin-bottom: 5px;width: 96%;margin-left: 2%;">
							<view class="cu-form-group text-bold">
								<view>{{language.brake}}</view>
							</view>
							<view class="cu-form-group flex-column">
								<view class="flex-row">
									<button class="cu-btn margin-bottom-sm"
										style="width: 5vw;margin-right: 2%;padding: 0 25upx;"
										@click="get_numbers('get_sum_number',item,`${language.brake} ${item}`)"
										v-for="(item,index) in number_0_9" :key="index">{{item}}</button>
								</view>
							</view>
						</view>


						<view class="myrect" style="margin-bottom: 5px;width: 96%;margin-left: 2%;">
							<view class="cu-form-group text-bold">
								<view>{{language.include}}</view>
							</view>
							<view class="cu-form-group flex-column">
								<view class="flex-row">
									<button class="cu-btn margin-bottom-sm"
										style="width: 5vw;margin-right: 2%;padding: 0 25upx;"
										@click="get_numbers('get_include_number',item,`${language.include} ${item}`)"
										v-for="(item,index) in number_0_9" :key="index">{{item}}</button>
								</view>
							</view>
						</view>

						<view class="myrect" style="margin-bottom: 5px;width: 96%;margin-left: 2%;">
							<view class="cu-form-group text-bold">
								<view>{{language.head}}</view>
							</view>
							<view class="cu-form-group flex-column">
								<view class="flex-row">
									<button class="cu-btn margin-bottom-sm"
										style="width: 5vw;margin-right: 2%;padding: 0 25upx;"
										@click="get_numbers('get_first_number',item,`${language.head} ${item}`)"
										v-for="(item,index) in number_0_9" :key="index">{{item}}</button>
								</view>
							</view>
						</view>
						<view class="myrect" style="margin-bottom: 5px;width: 96%;margin-left: 2%;">
							<view class="cu-form-group text-bold">
								<view>{{language.tail}}</view>
							</view>
							<view class="cu-form-group flex-column">
								<view class="flex-row">
									<button class="cu-btn margin-bottom-sm"
										style="width: 5vw;margin-right: 2%;padding: 0 25upx;"
										@click="get_numbers('get_second_number',item,`${language.tail} ${item}`)"
										v-for="(item,index) in number_0_9" :key="index">{{item}}</button>
								</view>
							</view>
						</view>

						<view class="myrect" style="margin-bottom: 5px;width: 96%;margin-left: 2%;">
							<view class="cu-form-group text-bold">
								<view>{{language.Constellation_Power}}</view>
							</view>
							<view class="cu-form-group flex-column">
								<view class="flex-row">
									<view class="flex-column">
										<button class="cu-btn margin-bottom-sm margin-top-sm"
											style="width: 100%;text-align: left;"
											@click="get_numbers(item.value,'',language[item.lang_text])"
											v-for="(item,index) in constellation_power_items.button"
											:key="index">{{language[item.lang_text] + item.sub_lang_text}}</button>
									</view>
								</view>
							</view>
						</view>
						<view class="myrect" style="margin-bottom: 5px;width: 96%;margin-left: 2%;">
							<view class="cu-form-group text-bold">
								<view>{{language.select_20}}</view>
							</view>
							<view class="cu-form-group flex-column">
								<view class="flex-row">
									<button class="cu-btn margin-bottom-sm"
										style="width: 20%;margin-right: 2%;padding: 0 20upx;font-size: 12px;"
										@click="get_numbers('get_20_number',item.value,item.label)"
										v-for="(item,index) in select_20_list" :key="index">{{item.label}}</button>
								</view>
							</view>
						</view>
					</scroll-view>
					<view class="flex flex-wrap justify-center">
						<view style="width: 100%;">
							<button class="mybg-orange" @tap='showInfoPopup()'>close</button>
						</view>
						<!-- <view class="basis-df">
						<button > 重置</button>
					</view> -->
					</view>
				</form>
			</view>


			<view class="cu-modal" :class="modalName=='info_popup'?'show':''">
				<form class="cu-dialog">
					<view class="cu-form-group text-bold" style="border-bottom:2px solid #f69e57;">
						<view style="width: 50%;text-wrap: wrap;">Name</view>
						<view style="width: 30%;">Key</view>
						<view style="width: 20%;">Example</view>
					</view>
					<scroll-view scroll-y style="height: 65vh; width: 90vw;" class="mybg-dgrey">
						<view class=" myrect" v-for="(item,key) in rule_info" :key='key'
							style="margin-bottom: 5px;width: 96%;margin-left: 2%;">
							<view class="cu-form-group text-bold">
								<view style="width: 50%;text-wrap: wrap;">{{item.name}}</view>
								<view style="width: 30%;">{{key}}</view>
								<view style="width: 20%;">{{item.example}}</view>
							</view>
							<view class="cu-form-group">
								<textarea style="height: 40px;" disabled v-model="item.result"></textarea>
							</view>
						</view>
					</scroll-view>
					<view class="flex flex-wrap justify-center">
						<view style="width: 100%;">
							<button class="mybg-orange" @tap='showInfoPopup()'>OK</button>
						</view>
						<!-- <view class="basis-df">
						<button > 重置</button>
					</view> -->
					</view>
				</form>
			</view>


		</form>
	</view>
</template>

<script>
	import numberrule from '../../utils/number-rule.js'
	import dateFormatUtils from '../../utils/utils.js'
	import config from '../../utils/config.js';
	import Vue from 'vue'
	export default {
		data() {
			return {
				update_cd:config.update_time_cd_2d,
				days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', ],
				index: -1,
				number_2d_items: numberrule.number_play_info.get_2d_items(),
				sod_items: numberrule.number_play_info.SOD,
				constellation_power_items: numberrule.number_play_info.constellation,
				select_20_list: numberrule.number_play_info.select_20,
				modalName: null,
				quick_select: false,
				number_list: [],
				intervalId: null,
				amount: '100',
				number_0_9: (Array.from(Array(10).keys())),
				betList: [],
				rule: '',
				Info: {},
				language: config.language,
				Results: [{}, {}, {}, {}, {}, {}, {}, ],
				rule_info: numberrule.number_rule_info,
				userconfig: this.$store.state.configs,
				betContent: '',
				saved: false,
			}
		},
		watch: {},
		methods: {
			get_numbers(func, val, betContent) {
				let _this = this
				_this.clear_select()
				console.log(betContent)
				let numbers = numberrule.number_play_info[func](val)
				_this.number_2d_items.forEach((ele, index) => {
					if (numbers.indexOf(ele.label) > -1 && !ele.baned) {
						_this.$set(_this.number_2d_items[index], 'selected', true)
					}
				})
				_this.betContent = betContent ?? ''
				_this.quick_select = true
				_this.showInfoPopup()
			},
			clear_select() {
				let _this = this
				_this.betContent = ''
				_this.number_2d_items.forEach((ele, index) => {
					_this.$set(_this.number_2d_items[index], 'selected', false)
				})
				_this.quick_select = false
			},
			select_number(item, index) {
				if(!item.baned){
					this.$set(this.number_2d_items[index], 'selected', !item.selected)
				}
			},
			showInfoPopup(ty) {
				if (ty === 1) {
					this.modalName = 'info_popup'
				} else {
					this.modalName = ''
				}
			},

			toPage(name) {
				// this.music.play_dede()
				uni.navigateTo({
					url: name,
					animationType: 'slide-in-right',
					animationDuration: 100
				})
			},
			showModal() {
				let _this = this
				if (!_this.Info.ODDS) {
					return
				}
				if(parseInt(_this.Info.SINGLE_MIN) > parseInt(_this.amount)){
					uni.showModal({
						title: 'Tips',
						content: _this.language.single_min + " (" + _this.Info.SINGLE_MIN + ")",
						showCancel: false,
						confirmText: 'ok',
						success: function(res) {}
					});
					return
				}
				let select_numbers = _this.number_2d_items.filter(ele => {
					return ele.selected
				})
				select_numbers = select_numbers.map(ele => {
					return ele.label
				})
				if (select_numbers.length == 0) {
					return
				}

				_this.betList = _this.parseList(select_numbers)
				_this.saved = false
				_this.modalName = 'list_popup'
			},
			parseList(arr) {
				// let reg3 = /(^\d{1,2}$)/;
				// let reg4 = /(^\d{1}$)/;
				// let list = []
				// arr.forEach(ele => {
				// 	if (reg3.test(ele)) {
				// 		let obj = {
				// 			BET_MONEY: this.amount,
				// 			BET_TYPE: reg4.test(ele) ? '0' + ele : ele
				// 		};
				// 		list.push(obj);
				// 	} else {
				// 		return []
				// 	}
				// })

				let list = arr.map(ele => {
					return {
						BET_MONEY: this.amount,
						BET_TYPE: ele
					}
				})
				return list
			},
			calc_num_percent(item) {
				let percent = String(item.money / item.num_limit * 100)
				return percent
			},
			cal_total_amount() {
				let total_amount = 0
				for (let i in this.betList) {
					total_amount += parseFloat(this.betList[i].BET_MONEY)
				}
				return total_amount
			},
			get_match_detail(item) {
				let _this = this
				let reg = /(^\d{1}$)/
				let para = {
					match_id: item.ID
				}
				_this.$http.get('/digital/get_detail', {
					data: para
				}, (res) => {
					if (res.data.code == 20000) {
						// _this.number_2d_items = []
						let bet_sum = 0
						res.data.items.forEach((ele) => {
							bet_sum += parseInt(ele.BET_MONEY)
							let temp = {
								label: ele.BET_TYPE,
								money: parseInt(ele.BET_MONEY),
								selected: false,
								num_limit: ele.LIMIT_NUM
							}
							_this.$set(_this.number_2d_items, parseInt(ele.BET_TYPE), temp)
						});
						_this.Info.bet_sum_total = bet_sum
					}
				})
			},
			getResult() {
				var _this = this;
				let reg4 = /(^\d{1}$)/;
				uni.showLoading({
					title: 'loading'
				})
				_this.$http.get('/digital/get_actvie_nper', {
					data: this.listQuery
				}, (res) => {
					uni.hideLoading();
					if (res.data.code == 20000) {
						// console.log(res.data)
						_this.Info = res.data.item
						_this.get_match_detail(res.data.item)
						_this.clear_select()
						_this.amount = String(res.data.item.SINGLE_MIN)
						Vue.set(_this.Info, 'am', !(res.data.item.STAGE.slice(-2) == 'am' || res.data.item.STAGE
							.slice(-2) == 'AM'))
						_this.Info.STAGE = _this.Info.STAGE.slice(-7)
						_this.Info.CLOSE_TIME = dateFormatUtils.formatTime(new Date(new Date(_this.Info.CLOSE_TIME)
							.valueOf() - 5400 * 1000))
						_this.Info.CLOSE_TIME = _this.Info.CLOSE_TIME.slice(-14, -3)
						_this.Info.bet_sum_total = 0
						uni.setStorageSync('digit_info', _this.Info)
						if (_this.Info.BAN_NUMS) {
							let ban_nums = _this.Info.BAN_NUMS.split(',')
							ban_nums.forEach(ele => {
								_this.number_2d_items[parseInt(ele)].baned = true
							})
						}
					} else {
						_this.Info = {}
						let title = ''
						switch (res.data.code) {
							case 50001:
								title = 'no match opened'
								break;
							default:
								title = 'unknown error'
								break;
						}
						uni.showToast({
							title: title,
							icon: 'none',
						})

					}

					var result = []
					//根据每日进行分组
					res.data.results.forEach(ele => {

						var openDate = dateFormatUtils.stringToDate(ele.OPEN_TIME + ":00");
						var openDay = openDate.getDay();
						var am = ele.STAGE.slice(-2)
						var apm = am == 'am' || am == 'AM' ? 0 : 1

						var tmp = result[openDay] ? result[openDay] : [];
						tmp[apm] = ele;
						result[openDay] = tmp;
					})

					//将每天的开奖结果拼接起来

					var resultStr = [{}, {}, {}, {}, {}, {}, {}, ];
					result.forEach((ele, index) => {
						var temp = {};
						if (ele[0]) {
							let amRes = ele[0].RESULT.toString()
							temp.am = reg4.test(amRes) ? '0' + amRes : amRes
						}
						if (ele[1]) {
							let pmRes = ele[1].RESULT.toString()
							temp.pm = reg4.test(pmRes) ? '0' + pmRes : pmRes
						}
						resultStr[index] = temp;
					})
					_this.Results = resultStr
					// console.log(resultStr)
					// console.log(result)
				})
			},
			hideModal(e) {
				// this.$refs.list_popup.close()
				this.modalName = null
			},

			submit() {
				let _this = this

				if (_this.saved || !_this.Info.ODDS) {
					return
				}
				let para = []
				let list = JSON.parse(JSON.stringify(_this.betList))
				let remark = ''
				if (list.length > 1) {
					remark = _this.betContent ?? _this.rule
				}
				list.forEach(ele => {
					// ele.BET_TYPE = parseInt(ele.BET_TYPE)
					ele.REMARK = remark
					ele.BET_MONEY ? para.push(ele) : ''
				})
				// if (para.length === 0 || !_this.Info.ID || under || over) {
				// 	return
				// }
				_this.saved = true
				_this.$http.post('/digital/digit_bet', {
					match_id: _this.Info.ID,
					bets: para,
				}, (res) => {
					_this.modalName = ''
					uni.hideLoading();
					if (res.data.code == 20000) {
						_this.get_match_detail(_this.Info)
						_this.clear_select()
						// uni.setStorageSync('2D_amount',_this.amount)
						_this.amount = String(_this.Info.SINGLE_MIN)
						_this.rule = _this.language.combination
						uni.showModal({
							title: 'tips',
							// content: _this.language.bettingSuccess,
							content: 'bet success',
							showCancel: false,
							confirmText: 'ok',
							success: function() {
								// var userInfo = _this.$store.state.userInfo

								// userInfo.TOTAL_MONEY = parseInt(userInfo.TOTAL_MONEY) - parseInt(_this.amount);
								// _this.$store.dispatch('saveUserInfo', userInfo);
							}
						});
					} else {
						var tips = '';
						// if (_this.language[res.data.message]) {
						// 	tips = _this.language[res.data.message] + "(" + _this.$store.state.configs[res.data.message] + ")"
						// } else {
						// 	tips = res.data.message;
						// }
						uni.showToast({
							title: res.data.message,
							icon: 'none'
						})
					}
				})
			},
			delRow(index) {
				this.betList.splice(index, 1)
			},
			resetRowAmount() {
				this.betList.forEach(ele => {
					Vue.set(ele, 'BET_MONEY', this.amount)
				})
			},
			resetAmount() {
				this.amount = String(this.Info.SINGLE_MIN)
			},
			onInput(evt, typ, index) {
				// let _this = this
				// console.log(evt,index)
				// console.log(evt.detail.value.replace(/\b(0+)/gi,''))
				// let amount = evt.detail.value.replace(/\b(0+)/gi, '').replace('^(0|[1-9][0-9]*)$', '')
				// let over = parseInt(amount) > this.Info.SINGLE_MAX
				// let under = parseInt(amount) < this.Info.SINGLE_MIN
				// let result = over ? String(this.Info.SINGLE_MAX) : under ? String(this.Info.SINGLE_MIN) : amount

				// // console.log(amount,over,under)
				// setTimeout(() => {
				// 	switch (typ) {
				// 		case 1:
				// 			Vue.set(this.betList[index], 'BET_MONEY', result)
				// 			break
				// 		case 2:
				// 			// Vue.set(this, 'amount', result)
				// 			Vue.set(this, 'amount', amount)
				// 			break
				// 	}
				// }, 0)


			},
			goto(name) {
				uni.setStorageSync('navi2D3D', '3D')
				uni.navigateTo({
					url: '/pages/number/3d-number-bet',
					animationType: 'slide-in-right',
					animationDuration: 100
				})
			},
			to_record(name) {
				uni.navigateTo({
					url: '/pages/number/record',
					animationType: 'slide-in-right',
					animationDuration: 100
				})
			},
			to_total(name) {
				if (!this.Info.ID) {
					return
				}
				uni.navigateTo({
					url: '/pages/number/total',
					animationType: 'slide-in-right',
					animationDuration: 100
				})
			},
			update_progress_bar() {
				let _this = this
				if(_this.intervalId){
					
				}else{
					_this.intervalId = setInterval(function() {
						let page_list = getCurrentPages()
						if (page_list[page_list.length - 1].route.indexOf('pages/number/number-bet') < 0) {
							clearInterval(_this.intervalId);
							_this.intervalId = null
						// } else if (_this.Info.ID) {
						} else {
							_this.getResult()
							// _this.get_match_detail(_this.Info)
						}
					}, _this.update_cd * 1000);
				}
			},
		},
		onShow() {
			this.rule = this.language.combination;
			uni.setStorageSync('navi2D3D', '2D')
			this.getResult()
			this.update_progress_bar()

		},
	}
</script>

<style>
	.rec1 {
		width: 40vw;
		height: 16vw;
		border: #d34647 solid 1px;
		margin: 1px;
	}

	.rec2 {
		border: #d34647 solid 1px;
		width: 30%;
		height: 17vw;
		margin: 0px;
		line-height: 6vw;
	}

	.content-row view {
		height: 30px;
		width: 20%;
		line-height: 30px;
	}

	.day-text {
		font-size: 18px;
		border: 1px solid #F2F2F2;
	}

	.day-text2 {
		border: 0px;
		font-size: 16px;
	}
</style>
