<template>
	<view class=" text-center">
		<view class="flex  p-xs mb-sm" style="height: 32px;line-height: 32px;">
			<view class="flex-twice bg-lightgrey radius" @click="handleDateBtn('left')">{{leftBtn}}</view>
			<view class="flex-twice bg-lightgrey radius text-bold">{{centerBtn}}</view>
			<view class="flex-twice bg-lightgrey radius" @click="handleDateBtn('right')">{{rightBtn}}</view>
		</view>
	</view>
</template>

<script>
	import dateFormatUtils from '../../utils/utils.js'
	export default {
		name:'DatePicker',
		data() {
			return {
				queryDate: new Date(),
				leftBtn: '',
				centerBtn: '',
				rightBtn: ''
			}
		},
		methods: {
			getFilterTime(){
				var listQuery={start_time:'',end_time:''};
				
				listQuery.start_time = dateFormatUtils.formatTime(this.queryDate);
				
				var tomorrow = new Date(this.queryDate.getTime() + 3600 * 1000 * 24);
				listQuery.end_time = dateFormatUtils.formatTime(tomorrow);
				return listQuery;
			},
			handleDateBtn(type) {

				switch (type) {
					case 'left':

						//右边按钮变成今天
						this.rightBtn = dateFormatUtils.formatDate(this.queryDate.getTime(), 'Y-M-D');
						this.rightBtn = this.rightBtn.substring(5, this.rightBtn.length);

						//今年减去24小时
						this.queryDate = new Date(this.queryDate.getTime() - 3600 * 1000 * 24);
						var queryDateStr = dateFormatUtils.formatDate(this.queryDate.getTime(), 'Y-M-D');

						this.centerBtn = queryDateStr.substring(5, queryDateStr.length);

						//左边按钮是今天减去48小时
						this.leftBtn = dateFormatUtils.formatDate(this.queryDate.getTime() - 3600 * 1000 * 24, 'Y-M-D');
						this.leftBtn = this.leftBtn.substring(5, this.leftBtn.length);

						//this.getMatchResult()
						this.$emit('fatherMethod',this.getFilterTime());
						break;
					case 'right':
						this.leftBtn = dateFormatUtils.formatDate(this.queryDate.getTime(), 'Y-M-D');
						this.leftBtn = this.leftBtn.substring(5, this.leftBtn.length);

						this.queryDate = new Date(this.queryDate.getTime() + 3600 * 1000 * 24);
						var queryDateStr = dateFormatUtils.formatDate(this.queryDate.getTime(), 'Y-M-D');

						this.centerBtn = queryDateStr.substring(5, queryDateStr.length);

						this.rightBtn = dateFormatUtils.formatDate(this.queryDate.getTime() + 3600 * 1000 * 24, 'Y-M-D');
						this.rightBtn = this.rightBtn.substring(5, this.rightBtn.length);

						//this.getMatchResult()
						this.$emit('fatherMethod',this.getFilterTime());
						break;
				}
				var today = dateFormatUtils.formatDate(new Date().getTime(), 'Y-M-D');
				var todayStr = dateFormatUtils.formatDate(this.queryDate.getTime(), 'Y-M-D');
				if (todayStr == today) {
					this.centerBtn = 'Today'
				}
			}
		},
		created() {
			//获取今日
			this.queryDate = new Date().getTime();
			var queryDateStr = dateFormatUtils.formatDate(this.queryDate, 'Y-M-D');
			queryDateStr += ' 12:00:00';
			this.queryDate = dateFormatUtils.stringToDate(queryDateStr);
			
			this.centerBtn = 'Today';
			
			this.leftBtn = dateFormatUtils.formatDate(this.queryDate.getTime() - 3600 * 1000 * 24, 'Y-M-D');
			this.leftBtn = this.leftBtn.substring(5, this.leftBtn.length);
			
			this.rightBtn = dateFormatUtils.formatDate(this.queryDate.getTime() + 3600 * 1000 * 24, 'Y-M-D');
			this.rightBtn = this.rightBtn.substring(5, this.rightBtn.length);
		}
	}
</script>

<style>

</style>
