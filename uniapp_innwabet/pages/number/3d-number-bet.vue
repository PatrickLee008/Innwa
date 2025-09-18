<template>
	<view class="mybg-grey">
		<cu-custom isBack backUrl="/pages/index/index">
			<block slot="content">3D</block>
			<!-- 	<block slot="right">
				<view>
					<button class="cu-btn bg-blue margin-right-sm" @click="goto()">2D</button>
				</view>
			</block> -->
		</cu-custom>
		<form class="mybg-grey full-page">
			<view class="flex-row text-bold" style="justify-content: space-around;line-height: 6vw;">
				<view class="myrect box-shadow bg-white rec1 flex-column mycolor-green">
					<text>{{language.stage}}</text>
					<text style="height: 6vw;">{{Info.STAGE}}</text>
				</view>
				<view class="myrect box-shadow bg-white rec1 flex-column mycolor-green">
					<text>{{language.close_time}}</text>
					<text style="height: 6vw;">{{Info.CLOSE_TIME}}</text>
				</view>
			</view>

			<view class="myrect flex-column text-bold" style="padding: 4px 0 4px 0;margin-left: 0;">
				<view class="flex-row" style="justify-content: space-around;">
					<view class="myrect box-shadow bg-white rec2 flex-column mycolor-green" @click="to_total()">
						<text>{{language.digit_total}}</text>
					</view>
					<view class="myrect box-shadow bg-white rec2 flex-column mycolor-green" @click="to_record()">
						<text>{{language.digit_record}}</text>
					</view>

				</view>
			</view>

			<view class="myrect box-shadow bg-white flex-column text-bold text-right"
				style="width: 96vw;margin: 15px 2vw;margin-top: 15px;">
				<view class="flex-row" style="justify-content: space-between;padding: 7px 12px 7px 12px;">
					<button class='cu-btn shadow mybg-green' @click="modalName = 'play_info'">{{language.fast}}</button>
					<button class='cu-btn shadow mybg-green' @click="play_R">R</button>
					<input style="width: 50%;" @input='onInput($event,2,1)' type="number" v-model="amount"></input>
				</view>
				<view class="mybg-grey" style="width: 96vw;height: 2px;margin: 5px 0 5px 0"></view>

				<view class="flex-row" style="justify-content: space-between;">
					<button class='cu-btn shadow margin-sm mybg-green'
						@tap="toPage('order')">{{language.digitorder}}</button>
					<view>
						<button class='cu-btn shadow mybg-orange'
							@click="clear_select">{{language.cancel_fast}}</button>
						<button class='cu-btn shadow margin-sm mybg-green' @tap="showModal">OK</button>
					</view>
				</view>
			</view>

			<view v-if="!show_picture" class="ir-nav-con" style="width: 100vw;" :style="{ background: navBgColor}">
				<view v-for="(nav, index) in number_0_9_str" :key="index"
					:class="['ir-nav', {'ir-active': currNav === index, 'ir-over-hide': navEqual}]"
					:style="{backgroundColor: currNav === index && navType === 'card' ? activeColor : ''}"
					@click="changeNav(index)">
					<text class="ir-nav-text"
						:style="{color: textColor(index),fontSize: fontSize}">{{nav.name || nav}}</text>
					<view v-if="navType === 'border'" class="ir-line"
						:style="{backgroundColor: currNav === index ? activeColor : ''}" />
				</view>
			</view>
			<scroll-view scroll-y class="myrect text-bold text-center" enable-flex v-if="!show_picture"
				style="margin-left: 0px;height: calc(100vh - 300px - 25vw);justify-content: space-around;width: 100vw;flex-direction: row;">
				<view class="cu-btn" :class="_item.baned?'bg-black':_item.selected ?'mybg-orange':'mybg-light-yellow'"
					@click="select_number(_item,index)"
					style="width: 11.25vw;height: 11.25vw; border: rgb(235,227,223) solid 1rpx;margin: 1.25vw;flex-direction: column;border-radius: 1vw;justify-content: space-around;"
					v-for="(_item,_index) in number_3d_items"
					v-if="_index >= currNav * 100 && _index <= (currNav * 100 + 99)" :key="_index">
					<view>
						{{_item.label}}
					</view>
					<view class="cu-progress round xs" style="width: 10vw" :class="_item.baned?'hidden':''">
						<view :class="calc_num_percent(_item) > 90? 'bg-red':calc_num_percent(_item) > 40?'bg-yellow':'bg-blue'
						" :style="[{ width: calc_num_percent(_item) + '%'}]"></view>
					</view>
				</view>
				<view style="width: 100%;height: 4vw;"></view>
			</scroll-view>

			<scroll-view scroll-y class="myrec3" v-if="show_picture" style="height: calc(100vh - 245px - 25vw);"
				@scrolltolower="clickLoadMore()">
				<view class="flex-column2 margin-tb-sm" style="width: 30.5vw;height: border: rgb(235,227,223) solid 1rpx;margin: 1.25vw;
					border-radius: 1vw;justify-content: space-around;" v-for="(pic,__index) in picture_list" :key="__index">
					<text class="bg-white pic-text">
						{{pic.name}}
					</text>
					<view style="width: 30.5vw;height: 37vw;" @click="select_pic(pic)">
						<image style="width: 30.5vw;height: 37vw;" :src="pic.img"></image>
					</view>
					<view class="pic-button" style="">
						<button class="cu-btn" :class="cal_3d_item(pic,0).selected ?'mybg-orange':''"
							@click="select_pic_number(pic,0)" style="width: 14vw;">{{cal_3d_item(pic,0).label}}</button>
						<button class="cu-btn" :class="cal_3d_item(pic,1).selected ?'mybg-orange':''"
							@click="select_pic_number(pic,1)" style="width: 14vw;">{{cal_3d_item(pic,1).label}}</button>
					</view>
				</view>
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
								<button class="cu-btn cuIcon-delete round mybg-green" @tap='delRow(index)'></button>
							</view>
						</scroll-view>
					</view>
					<form>
						<view class="cu-form-group">
							<view class="title">{{language.odds}}</view>
							<view
								style="border: 1px solid rgb(0, 140, 103); color:rgb(0, 140, 103);font-weight: bold;padding:8px;border-radius: 3px;">
								{{Info.ODDS?'1X' + Info.ODDS :''}}
							</view>
						</view>
						<view class="cu-form-group">
							<view class="title">{{language.amount}}</view>
							<view style=" color:rgb(0, 140, 103);font-weight: bold;padding:8px;border-radius: 3px;">
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
							<view class="cu-btn margin-sm shadow radius" :class="saved ?'bg-grey':'mybg-green' "
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
									<button class="cu-btn margin-bottom-sm margin-top-sm"
										style="width: 18%;margin-right: 2%;padding: 0 0 0 0;"
										@click="get_numbers(item.value,'',language[item.lang_text])"
										v-for="(item,index) in sod_items.button2"
										:key="index">{{language[item.lang_text]}}</button>
								</view>
								<!-- <view class="flex-row">
									<button class="cu-btn margin-bottom-sm"
										style="width: 5vw;margin-right: 2%;padding: 0 25upx;"
										@click="get_numbers('get_include_number_3d',item,language.double_and_size)"
										v-for="(item,index) in number_0_9" :key="index">{{item}}</button>
								</view> -->
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
										@click="get_numbers('get_include_number_3d',item,`${language.include} ${item}`)"
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
										@click="get_numbers('get_first_number_3d',item,`${language.head} ${item}`)"
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
										@click="get_numbers('get_second_number_3d',item,`${language.tail} ${item}`)"
										v-for="(item,index) in number_0_9" :key="index">{{item}}</button>
								</view>
							</view>
						</view>
						<view class="myrect" style="margin-bottom: 5px;width: 96%;margin-left: 2%;">
							<view class="cu-form-group text-bold">
								<view>{{language.select_200}}</view>
							</view>
							<view class="cu-form-group flex-column">
								<view class="flex-row">
									<button class="cu-btn margin-bottom-sm"
										style="width: 30%;margin-right: 2%;padding: 0 20upx;font-size: 12px;"
										@click="get_numbers('get_200_number',item.value,item.label)" v-if="index < 3"
										v-for="(item,index) in select_200_list" :key="index">{{item.label}}</button>
								</view>
								<view class="flex-row">
									<button class="cu-btn margin-bottom-sm"
										style="width: 30%;margin-right: 2%;padding: 0 20upx;font-size: 12px;"
										@click="get_numbers('get_200_number',item.value,item.label)" v-if="index > 2"
										v-for="(item,index) in select_200_list" :key="index">{{item.label}}</button>
								</view>
							</view>
						</view>
					</scroll-view>
					<view class="flex flex-wrap justify-center">
						<view style="width: 100%;">
							<button class="mybg-orange" @tap='showInfoPopup()'>close</button>
						</view>
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
	import number_pic_list from '../../utils/number-pic.js'
	import Vue from 'vue'
	import IrTabs from '@/components/ir-tabs/ir-tabs.vue';
	export default {
		components: {
			IrTabs
		},
		data() {
			return {
				update_cd: config.update_time_cd_3d,
				noNavi: false,
				days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', ],
				index: -1,
				number_3d_items: numberrule.number_play_info.get_3d_items(),
				sod_items: numberrule.number_play_info.SOD,
				constellation_power_items: numberrule.number_play_info.constellation,
				select_20_list: numberrule.number_play_info.select_20,
				select_200_list: numberrule.number_play_info.select_200,
				modalName: null,
				quick_select: false,
				number_list: [],
				amount: '100',
				number_0_9: (Array.from(Array(10).keys())),
				number_0_9_str: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ],
				betList: [],
				rule: '',
				Info: {},
				language: config.language,
				intervalId: null,
				Results: [{}, {}, {}, {}, {}, {}, {}, ],
				rule_info: numberrule.number_rule_info,
				userconfig: this.$store.state.configs,
				betContent: '',
				saved: false,
				currentPage: 0,
				show_picture: false,
				picture_list: number_pic_list.slice(0, 10),
				// navibar相关
				navType: 'border',
				currNav: 0,
				navEqual: true,
				fontSize: '30rpx',
				activeColor: '#007AFF',
				navBgColor: '#fff',
				the_end: false,
			}
		},
		watch: {},
		methods: {
			select_pic(pic) {
				let _this = this
				// this.$set(item, 'selected', !item.selected)
				let item = _this.number_3d_items[parseInt(pic.children[0].number)]
				let item2 = _this.number_3d_items[parseInt(pic.children[1].number)]
				// console.log(item)
				if (!item.selected || !item2.selected) {
					_this.$set(item, 'selected', true)
					_this.$set(item2, 'selected', true)
				} else {
					_this.$set(item, 'selected', false)
					_this.$set(item2, 'selected', false)
				}
			},
			select_pic_number(pic, index) {
				let _this = this
				let item = _this.number_3d_items[parseInt(pic.children[index].number)]
				_this.$set(item, 'selected', !item.selected)
				// let item2 = _this.number_3d_items[parseInt(pic.children[1].number)]
				// if(item.selected && item.selected){
				// 	_this.$set(item, 'selected', false)
				// 	_this.$set(item2, 'selected', false)
				// }else{
				// 	_this.$set(item, 'selected', true)
				// 	_this.$set(item2, 'selected', true)
				// }
			},
			cal_3d_item(pic, index) {
				let item = this.number_3d_items[parseInt(pic.children[index].number)]
				return item
			},
			calc_num_percent(item) {
				let percent = String(item.money / item.num_limit * 100)
				return percent
			},
			changeNav(index) {
				this.currNav = index
			},
			// 设置菜单字体颜色
			textColor(index) {
				let color = ''
				if (this.navType === 'border' && this.currNav === index) {
					color = this.activeTextColor || this.activeColor
				} else if (this.navType === 'card' && this.currNav === index) {
					color = this.activeTextColor
				} else {
					color = this.navTextColor
				}
				return color
			},
			play_R() {
				let _this = this
				const selectedLabels = _this.number_3d_items
					.filter(item => item.selected)
					.map(item => item.label);
				if (selectedLabels.length === 0) {
					return
				}

				const generatePermutations = (str, current = '', used = []) => {
					if (current.length === str.length) {
						return [current];
					}
					let permutations = [];
					for (let i = 0; i < str.length; i++) {
						if (!used[i]) {
							used[i] = true;
							const newCurrent = current + str[i];
							const newPermutations = generatePermutations(str, newCurrent, used);
							permutations = permutations.concat(newPermutations);
							used[i] = false;
						}
					}
					return permutations;
				};
				let res = []
				selectedLabels.forEach(ele => {
					res = res.concat(generatePermutations(ele))
				})
				const uniqueLabelStr = [...new Set(res)];
				_this.clear_select()
				_this.number_3d_items.forEach((ele, index) => {
					if (uniqueLabelStr.includes(ele.label) && !ele.baned) {
						_this.$set(_this.number_3d_items[index], 'selected', true)
					}
				})
			},
			get_numbers(func, val, betContent) {
				let _this = this
				_this.clear_select()
				console.log(betContent)
				let numbers = numberrule.number_play_info[func](val)
				_this.number_3d_items.forEach((ele, index) => {
					if (numbers.includes(ele.label) && !ele.baned) {
						_this.$set(_this.number_3d_items[index], 'selected', true)
					}
				})
				_this.betContent = betContent ?? ''
				_this.quick_select = true
				_this.showInfoPopup()
			},
			clear_select() {
				let _this = this
				_this.number_3d_items.forEach((ele, index) => {
					_this.$set(_this.number_3d_items[index], 'selected', false)
				})
				_this.betContent = ''
				_this.quick_select = false
			},
			select_number(item, index) {
				if (!item.baned) {
					this.$set(item, 'selected', !item.selected)
				}
				// this.$set(item, 'selected', !item.selected)
				// this.$set(this.number_3d_items[index], 'selected', !item.selected)
				// this.$nextTick(() => {
				// 	setTimeout(() => {
				// 		this.$set(item, 'selected', !item.selected)
				// 	}, 30)
				// })
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
			cal_total_amount() {
				let total_amount = 0
				for (let i in this.betList) {
					total_amount += parseFloat(this.betList[i].BET_MONEY)
				}
				return total_amount
			},
			showModal() {
				let _this = this
				if (!_this.Info.ODDS) {
					return
				}
				if (parseInt(_this.Info.SINGLE_MIN) > parseInt(_this.amount)) {
					uni.showModal({
						title: 'Tips',
						content: _this.language.single_min + " (" + _this.Info.SINGLE_MIN + ")",
						showCancel: false,
						confirmText: 'ok',
						success: function(res) {}
					});
					return
				}
				let select_numbers = _this.number_3d_items.filter(ele => {
					return ele.selected
				})
				if (select_numbers.length == 0) {
					return
				}
				select_numbers = select_numbers.map(ele => {
					return ele.label
				})
				_this.betList = _this.parseList(select_numbers)
				_this.saved = false
				_this.modalName = 'list_popup'
			},
			parseList(arr) {
				// let reg3 = /(^\d{3}$)/;
				// let reg4 = /(^\d{2}$)/;
				let list = arr.map(ele => {
					return {
						BET_MONEY: this.amount,
						BET_TYPE: ele
					}
				})
				return list
			},
			getResult() {
				var _this = this;
				let reg4 = /(^\d{1}$)/;
				uni.showLoading({
					title: 'loading'
				})
				_this.$http.get('/digital_3d/get_actvie_nper', {
					data: this.listQuery
				}, (res) => {
					uni.hideLoading();
					if (res.data.code == 20000) {
						// console.log(res.data)
						_this.Info = res.data.item
						_this.get_match_detail(res.data.item)
						_this.amount = String(res.data.item.SINGLE_MIN)
						// _this.Info.STAGE = _this.Info.STAGE.slice(-7)

						// _this.Info.CLOSE_TIME = dateFormatUtils.formatTime(new Date(new Date(_this.Info.CLOSE_TIME)
						// 	.valueOf() - 5400 * 1000))
						// _this.Info.CLOSE_TIME = _this.Info.CLOSE_TIME.slice(-14, -3)
						
						let closeTime = dateFormatUtils.stringToDate(_this.Info.CLOSE_TIME+":00")
						closeTime.setHours(closeTime.getHours() - 1);
						_this.Info.CLOSE_TIME = dateFormatUtils.formatTime(closeTime)
						_this.Info.CLOSE_TIME = _this.Info.CLOSE_TIME.substring(5,16)
						
						
						uni.setStorageSync('digit_info', _this.Info)

						if (_this.Info.BAN_NUMS) {
							let ban_nums = _this.Info.BAN_NUMS.split(',')
							ban_nums.forEach(ele => {
								_this.number_3d_items[parseInt(ele)].baned = true
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
				})
			},
			get_match_detail(item) {
				let _this = this
				let reg = /(^\d{1}$)/
				let para = {
					match_id: item.ID
				}
				_this.$http.get('/digital_3d/get_detail', {
					data: para
				}, (res) => {
					if (res.data.code == 20000) {
						let bet_sum = 0
						res.data.items.forEach((ele) => {
							bet_sum += parseInt(ele.BET_MONEY)
							let temp = {
								label: ele.BET_TYPE.length < 3 ? '0' + ele.BET_TYPE : ele.BET_TYPE,
								money: parseInt(ele.BET_MONEY),
								selected: false,
								num_limit: ele.LIMIT_NUM
							}
							_this.$set(_this.number_3d_items, parseInt(ele.BET_TYPE), temp)
						});
						_this.Info.bet_sum_total = bet_sum
					}
				})
			},
			hideModal(e) {
				// this.$refs.list_popup.close()
				this.modalName = null
			},

			submit() {
				let _this = this;
				if (_this.saved || !_this.Info.ODDS) {
					return
				}
				let list = JSON.parse(JSON.stringify(_this.betList))
				let remark = ''
				if (list.length > 1) {
					remark = _this.betContent ?? _this.rule
				}
				let over = false
				let under = false
				let para = [];
				list.forEach(ele => {
					// ele.BET_TYPE = parseInt(ele.BET_TYPE)
					over = parseInt(ele.BET_MONEY) > _this.Info.SINGLE_MAX
					under = parseInt(ele.BET_MONEY) < _this.Info.SINGLE_MIN
					if (over || under) {
						uni.showToast({
							icon: 'none',
							title: 'Amount ' + (over ? 'over maximun!! （' + _this.Info.SINGLE_MAX : '') +
								(under ? 'under minimun!!（' + _this.Info.SINGLE_MIN : '') + ')',
						})
						return
					}
					ele.REMARK = remark
					ele.BET_MONEY ? para.push(ele) : ''
				})
				if (para.length == 0 || !_this.Info.ID || under || over) {
					return
				}
				_this.saved = true
				uni.showLoading({
					title: 'loading'
				})
				_this.$http.post('/digital_3d/bet', {
					match_id: _this.Info.ID,
					bets: para,
				}, (res) => {
					_this.modalName = ''
					uni.hideLoading();
					if (res.data.code == 20000) {
						_this.amount = String(_this.Info.SINGLE_MIN)
						// uni.setStorageSync('3D_amount',_this.amount)
						_this.rule = _this.language.combination
						_this.clear_select()
						_this.get_match_detail(_this.Info)
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
			goto(name) {
				uni.setStorageSync('navi2D3D', '2D')
				uni.navigateTo({
					url: '/pages/number/number-bet',
					animationType: 'slide-in-right',
					animationDuration: 100
				})
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
			get_picture() {
				var _this = this;
				let data = number_pic_list.slice(_this.currentPage * 10, _this.currentPage * 10 + 10)
				_this.picture_list = _this.picture_list.concat(data)
				if (_this.currentPage === 10) {
					_this.the_end = true
				}
			},
			get_picture2() {
				var _this = this;
				uni.request({
					url: 'https://backend.pttgaming.com/api/v2/v1/threed/book',
					data: {
						page: _this.currentPage,
					},
					method: 'GET',
					header: {
						'content-type': 'application/json',
					},
					complete: (res) => {
						if (res.statusCode == 200) {
							let data = res.data
							_this.picture_list = _this.picture_list.concat(data.data)
							uni.setStorageSync('picture_list', _this.picture_list)
							// console.log(_this.picture_list)
							// if(data.current_page === 10){
							// 	_this.the_end = true
							// }
							if (data.length == 0) {
								_this.the_end = true
							} else {}
						}
					},
				});
			},
			clickLoadMore(type) {
				if (this.the_end) {
					return
				}
				this.currentPage++;
				this.get_picture();
			},
			to_record(name) {
				uni.navigateTo({
					url: '/pages/number/record-3d',
					animationType: 'slide-in-right',
					animationDuration: 100
				})
			},
			to_total(name) {
				if (!this.Info.ID) {
					return
				}
				uni.navigateTo({
					url: '/pages/number/total-3d',
					animationType: 'slide-in-right',
					animationDuration: 100
				})
			},
			update_progress_bar() {
				let _this = this
				if (_this.intervalId) {

				} else {
					_this.intervalId = setInterval(function() {
						let page_list = getCurrentPages()
						if (page_list[page_list.length - 1].route.indexOf('pages/number/3d-number-bet') < 0) {
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
			this.getResult()
			this.update_progress_bar()
			this.clear_select()
			uni.setStorageSync('navi2D3D', '3D')
			// this.get_picture()
		},
	}
</script>

<style>
	.myrec3 {
		width: 100vw;
		display: flex;
		flex-direction: row;
		flex-wrap: wrap;
		align-content: center;
	}

	.rec1 {
		width: 43vw;
		height: 20vw;
		border: rgb(9, 134, 147) solid 1px;
		margin: 1px;
	}

	.rec2 {
		border: rgb(9, 134, 147) solid 1px;
		width: 43vw;
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

	.ir-nav-con {
		display: flex;
		flex-direction: row;
		box-shadow: 0 0 16rpx 0 rgba(0, 0, 0, .3);
		justify-content: space-between;
		height: 84rpx;
		box-sizing: border-box;
		overflow: hidden;
		z-index: 1;
	}

	.ir-nav-con .ir-nav {
		display: flex;
		flex-direction: row;
		padding: 18rpx 10rpx 22rpx 10rpx;
		flex: 1;
		text-align: center;
		justify-content: center;
		align-items: center;
		white-space: nowrap;
	}

	.ir-over-hide {
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.ir-nav-con .ir-nav .ir-nav-text {
		text-align: center;
	}

	.ir-nav-con .ir-nav .ir-nav-icon {
		width: 30rpx;
		height: 30rpx;
		margin-right: 10rpx;
	}

	.ir-nav-con .ir-nav.ir-active {
		position: relative;
	}

	.ir-nav-con .ir-nav.ir-active .ir-line {
		content: '';
		width: 64rpx;
		height: 4rpx;
		position: absolute;
		bottom: 0;
		left: 50%;
		transform: translateX(-50%);
	}

	.flex-column2 {
		flex-direction: column;
		justify-content: center;
		align-content: center;
		align-items: center;
		display: inline-flex;
	}

	.pic-button {
		width: 30.5vw;
		display: inline-flex;
		position: relative;
		flex-directionX: row;
		justify-content: space-between;
		background-color: white;
	}

	.pic-text {
		font-size: 10upx;
		font-weight: 700;
		padding-top: 3px;
		display: block;
		word-break: keep-all;
		line-height: 15px;
		width: 30.5vw;
		/* height: 15px; */
	}

	.ir-page-con {
		margin-top: 84rpx;
	}
</style>