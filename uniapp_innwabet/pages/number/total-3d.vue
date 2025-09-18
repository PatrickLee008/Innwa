<template>
	<view class="mybg-grey">
		<cu-custom isBack backUrl="/pages/number/3d-number-bet">
			<!-- <block slot="content">{{'total'}}:{{Info.bet_sum_total}}</block> -->
			<block slot="content">{{Info.bet_sum_total}}</block>
		</cu-custom>
		<form class="mybg-grey full-page">
			<view class="ir-nav-con" style="width: 100vw;" :style="{ background: navBgColor}">
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
			<scroll-view scroll-y class="myrect box-shadow bg-white flex-column text-bold"
				style="width: 96vw;margin: 5px 2vw;padding: 2px 0 2px 0;height: calc(100vh - 95px);">
				<view class="flex-row" style="width: 96vw;margin: 1px;justify-content: flex-start;flex-wrap: wrap;">
					<view class="myrect mybg-dgrey flex-row padding-xs"
						style="width: 45vw;height: 8vw;margin: 1px 0 5px calc(25vw / 10);line-height: 8vw;justify-content: space-between;"
						v-for="(item,_index) in number_3d_items"
						v-if="_index >= currNav * 100 && _index <= (currNav * 100 + 99)" :key="_index">
						<view class="flex-row">
							<text>{{item.label}}</text>
							<view class="col-line bg-red"></view>
						</view>
						<text style="font-size: 13px;color:rgb(184,0,0)">{{item.money}}</text>/<text
							style="font-size: 14px;color: #666666;font-weight: bold;">{{number_limit}}</text>
					</view>
				</view>
			</scroll-view>


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
				days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', ],
				index: -1,
				number_0_9_str: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ],
				Info: uni.getStorageSync('digit_info'),
				language: config.language,
				results_of_day: [],
				userconfig: this.$store.state.configs,
				number_3d_items: numberrule.number_play_info.get_3d_items(),
				month: '',
				current: true,
				currNav: 0,
				navType: 'border',
				currNav: 0,
				navEqual: true,
				number_limit: 10000,
				fontSize: '30rpx',
				activeColor: '#007AFF',
				navBgColor: '#fff',
				listQuery: {
					start_time: '',
					end_time: '',
				},
			}
		},
		watch: {},
		methods: {
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
			changeNav(index) {
				this.currNav = index
			},
			get_match_detail(item) {
				let _this = this
				let para = {
					match_id: _this.Info.ID
				}
				_this.$http.get('/digital_3d/get_detail', {
					data: para
				}, (res) => {
					if (res.data.code == 20000) {
						let bet_sum = 0
						let num_limit = 10000
						res.data.items.forEach((ele) => {
							bet_sum += parseInt(ele.BET_MONEY)
							num_limit = dateFormatUtils.numFormat(ele.LIMIT_NUM)
							let temp = {
								label: ele.BET_TYPE,
								money: dateFormatUtils.numFormat(parseInt(ele.BET_MONEY)),
								selected: false,
								num_limit: dateFormatUtils.numFormat(parseInt(ele.LIMIT_NUM)),
							}
							_this.$set(_this.number_3d_items, parseInt(ele.BET_TYPE), temp)
						});
						_this.$set(_this, 'number_limit', num_limit)
						_this.Info.bet_sum_total = dateFormatUtils.numFormat(bet_sum)
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

		},
		onShow() {
			this.rule = this.language.combination;
			if(!this.Info.bet_sum_total){
				this.Info.bet_sum_total = '0'
			}
			this.get_match_detail()
		},
	}
</script>

<style>
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
</style>
