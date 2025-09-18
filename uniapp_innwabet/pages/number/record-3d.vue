<template>
	<view class="mybg-grey">
		<cu-custom isBack backUrl="/pages/number/3d-number-bet">
			<block slot="content">{{language.history_result}}</block>
			<block slot="right">
				<button class="cu-btn bg-blue margin-right-xs" @click="show_popup">{{language.month}}</button>
				<!-- <button class="cu-btn bg-blue" @click="set_day(true)" v-else>this month</button> -->
			</block>
		</cu-custom>
		<form class="mybg-grey full-page">
			<view class="myrect box-shadow bg-white flex-column"
				style="width: 96vw;margin: 5px 2vw;padding: 2px 0 2px 0;">
				<view style="margin-top: 2px;line-height: 35px;">{{month}}</view>
				<view class="mybg-grey" style="width: 96vw;height: 2px;margin: 2px 0 2px 0"></view>
				<view class="flex-row text-bold" style="width: 96vw;margin: 1px;justify-content: space-around;">
					<view class="myrect mybg-dgrey flex-column"
						style="width: 17%;height: 10vw;margin: 1px;line-height: 5vw;" v-for="(day,index) in days" :key="index">
						<text>{{day}}</text>
					</view>
				</view>
				<view class="mybg-grey" style="width: 96vw;height: 2px;margin: 5px 0 5px 0"></view>
				<view class="flex-row" style="width: 96vw;margin: 1px;justify-content: flex-start;flex-wrap: wrap;">
					<view class="myrect mybg-dgrey flex-column"
						style="width: 13%;height: 12vw;margin: 0px 0 5px calc(9% / 8);line-height: 4vw;"
						v-for="(day,index) in results_of_day" :key="index">
						<text>{{day.label}}</text>
						<view class="flex-row text-bold" style="justify-content: space-around;height: 4vw;">
							<text class="mycolor-orange">{{day.result}}</text>
						</view>
					</view>
				</view>
			</view>
		</form>


		<uni-popup ref="popup" type="bottom">
			<view style="width: 100vw;background-color: white;">
				<view style="width: 100vw;height: 30px;line-height: 30px;" class="text-center border-bottom margin">
					{{language.month}}
				</view>
				<view class="flex flex-wrap" style="justify-content: space-around;">
					<button class="cu-btn margin-bottom" :class="btn.selected?'mybg-red':''"
						v-for="(btn,index) in button_list" style="width: 30%;"
						@click="set_day(btn)" :key="index">{{btn.label}}</button>
					<!-- <button class="cu-btn" :class="listQuery.time==1?'mybg-red':''"
						@click="buttonPress(1,1)">{{language.one_week}}</button>
					<button class="cu-btn" :class="listQuery.time==2?'mybg-red':''"
						@click="buttonPress(1,2)">{{language.one_month}}</button> -->
				</view>
			</view>
		</uni-popup>
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
				days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', ],
				index: -1,
				Info: uni.getStorageSync('digit_info'),
				language: config.language,
				results_of_day: [],
				userconfig: this.$store.state.configs,
				month: '',
				current: true,
				button_list: [],
				listQuery: {
					start_time: '',
					end_time: '',
				},
			}
		},
		watch: {},
		methods: {
			show_popup() {
				this.$refs.popup.open()
			},
			close_popup() {
				this.$refs.popup.close()
			},
			get_month_result() {
				var _this = this;
				let reg4 = /(^\d{1}$)/;
				uni.showLoading({
					title: 'loading'
				})
				let para = {
					start_time: _this.listQuery.start_time,
					end_time: _this.listQuery.end_time,
					status: 3,
				}
				_this.$http.get('/digital_3d', {
					data: para
				}, (res) => {
					uni.hideLoading();
					if (res.data.code == 20000) {
						_this.parse_date(res.data.items)
					} else {

					}
				})
			},
			goto(name) {
				uni.setStorageSync('navi2D3D', '3D')
				uni.navigateTo({
					url: '/pages/number/3d-number-bet',
					animationType: 'slide-in-right',
					animationDuration: 100
				})
			},
			parse_date(items) {
				let reg = /(^\d{1}$)/;
				let start = new Date(dateFormatUtils.stringToDate2(this.listQuery.start_time))
				let last = new Date(dateFormatUtils.stringToDate2(this.listQuery.end_time))
				let all_day = new Array();
				let year = start.getFullYear()
				let month = start.getMonth() + 1
				for (var i = start.getDate(); i <= last.getDate(); i++) {
					let label = i < 10 ? '0' + i : i
					let new_date = year + "-" + (month < 10 ? '0' + month : month) + "-" + label
					let new_day = new Date(new_date)
					all_day[i - 1] = {
						day: new_day.getDay(),
						date: new_date,
						label: label,
						am: '',
						pm: '',
					}
				}
				let add_day = []
				let start_day = 7
				// if (start.getDay() != 0 && start.getDay() != 6) {
				if(start.getDay() != 0){
					start_day = start.getDay()
				}
				for (let i = 1; i < start_day; i++) {
					let label = i < 10 ? '0' + i : i
					add_day.push({
						day: 1,
						date: '',
						label: '',
						am: '',
						pm: '',
					})
				}
				// }
				items.forEach((ele, index) => {
					all_day.forEach((_ele, _index) => {
						if (_ele.date == ele.OPEN_TIME.slice(0, 10) && ele.STATUS == 3) {
							let res = ele.RESULT.toString()
							_ele.result = reg.test(res) ? '00' + res : res < 100 ? '0' + res : res
						}
					})
				})

				this.results_of_day = add_day.concat(all_day)
				this.month = start.getFullYear() + "-" + (month < 10 ? '0' + month : month)
			},
			set_day(btn) {
				let date_btn = Object.assign({}, btn)
				let _this = this
				_this.button_list.forEach(ele => {
					ele.selected = false
				})
				btn.selected = true
				_this.listQuery.end_time = _this.getLastDay(date_btn.date)
				_this.listQuery.start_time = date_btn.date
				_this.get_month_result()
				_this.$nextTick(() => {
					_this.close_popup()
				});
			},
			padZero(value) {
				return value < 10 ? '0' + value : value;
			},
			getLastDay(date) {
				var date = new Date(dateFormatUtils.stringToDate2(date));
				var new_month = date.getMonth() + 1;
				//取当前的年份
				var new_year = date.getFullYear();
				//取当年当月中的第一天
				var new_date = new Date(new_year, new_month, 1);
				var currentdate =
					`${new_year}-${new_month}-${new Date(new_date.getTime() - 1000 * 60 * 60 * 24).getDate()}`;
				return currentdate;
			},
			createDateDate(monthNum) {
				let datelist = []
				let date = new Date()
				let M = date.getMonth() + 1
				if (M - monthNum < 0) {
					let begin = 12 + (M - monthNum)
					for (let i = begin + 1; i <= begin + monthNum; i++) {
						if (i > 12) {
							datelist.push(`${date.getFullYear()}-${this.padZero(i%12)}`)
						} else {
							datelist.push(`${date.getFullYear() - 1}-${this.padZero(i)}`)
						}
					}
				} else {
					let begin = M - monthNum
					for (let i = begin + 1; i <= begin + monthNum; i++) {
						datelist.push(`${date.getFullYear()}-${this.padZero(i)}`)
					}
				}
				let list = datelist.map((ele, index) => {
					return {
						label: ele,
						date: ele + '-01',
						selected: index === datelist.length - 1,
					}
				})
				list.reverse()
				// console.log(datelist)
				this.button_list = list
				this.set_day(list[0])
				// console.log(this.getLastDay(list[0].date))
				// return list
			},

		},
		onShow() {
			this.rule = this.language.combination;
			this.createDateDate(6)
			// console.log(this.createDateDate(10))
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
