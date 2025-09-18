<template>
	<view class="mybg-grey">
		<cu-custom isBack backUrl="/pages/number/number-bet">
			<!-- <block slot="content">{{'total'}}:{{Info.bet_sum_total}}</block> -->
			<block slot="content">{{Info.bet_sum_total}}</block>
		</cu-custom>
		<form class="mybg-grey full-page">
			<view class="myrect box-shadow bg-white flex-column text-bold"
				style="width: 96vw;margin: 5px 2vw;padding: 2px 0 2px 0;">
				<view class="flex-row" style="width: 96vw;margin: 1px;justify-content: flex-start;flex-wrap: wrap;">
					<view class="myrect mybg-dgrey flex-row padding-xs"
						style="width: 45vw;height: 8vw;margin: 1px 0 5px calc(25vw / 10);line-height: 8vw;justify-content: space-between;"
						v-for="(item,index) in number_2d_items" :key="index">
						<view class="flex-row" >
							<text>{{item.label}}</text>
							<view class="col-line bg-red"></view>
						</view>
						<text style="font-size: 13px;color: #666666;">{{item.money}}</text>/<text style="font-size: 14px;color:rgb(184,0,0);font-weight: bold;">{{number_limit}}</text>
					</view>
				</view>
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
				days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', ],
				index: -1,
				Info: uni.getStorageSync('digit_info'),
				language: config.language,
				results_of_day: [],
				userconfig: this.$store.state.configs,
				number_2d_items: numberrule.number_play_info.get_2d_items(),
				month: '',
				current:true,
				number_limit:10000,
				listQuery: {
					start_time: '',
					end_time: '',
				},
			}
		},
		watch: {},
		methods: {
			get_match_detail(item) {
				let _this = this
				let para = {
					match_id: _this.Info.ID
				}
				_this.$http.get('/digital/get_detail', {
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
								money: dateFormatUtils.numFormat( parseInt(ele.BET_MONEY)),
								selected: false,
								num_limit: dateFormatUtils.numFormat(ele.LIMIT_NUM)
							}
							_this.$set(_this.number_2d_items, parseInt(ele.BET_TYPE), temp)
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
			this.get_match_detail()
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
