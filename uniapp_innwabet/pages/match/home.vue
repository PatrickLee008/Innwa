<template name="match">
	<view>
		<cu-custom isBack backUrl="/pages/index/index">
			<block slot="content">InnwaBet</block>
		</cu-custom>
		
		<advertisement/>
		
		<uni-notice-bar showIcon="true" :speed="speed" scrollable="true"  :text="notice"></uni-notice-bar>
		
		<scroll-view scroll-y class="page">
			<view class="nav-list">
				<navigator hover-class='none' :url="'/pages/match/' + item.name" class="nav-li" navigateTo :class="'bg-'+item.color"
				 :style="[{animation: 'show ' + ((index+1)*0.2+1) + 's 1'}]" v-for="(item,index) in elements" :key="index">
					<view class="nav-title">{{item.title}}</view>
					<text :class="'cuIcon-' + item.cuIcon"></text>
				</navigator>
			</view>
			<view class="cu-tabbar-height"></view>
		</scroll-view>
	</view>
</template>

<script>
	import uniNoticeBar from '@/components/uni-notice-bar/uni-notice-bar.vue'
	import advertisement from '../plugin/advertisement.vue'
	import config from '../../utils/config.js'
	export default {
		name: "match",
		components: {uniNoticeBar,advertisement},
		data() {
			return {
				speed:10,
				language:config.language,
				elements: [{
						title: '',
						color: 'purple',
						name:'mixed',
						cuIcon: 'vipcard'
					},
					{
						title: '',
						color: 'mauve',
						name:'single',
						cuIcon: 'formfill'
					},
					{
						title: '',
						color: 'mauve',
						name:'score',
						cuIcon: 'formfill'
					}
				],
				notice:''
			};
		},
		methods:{
			getNotice(){
				var _this = this;
				_this.$http.get('/notice/get',{},(res)=>{
					if(res.data.code==20000){
						_this.notice = '';
						res.data.items.forEach(element=>{
							_this.notice += '['+element.TITLE+']'+element.CONTENT+'           ';
						})
					}
				})
			}
		},
		created() {
			this.getNotice();
			this.elements[0].title = this.language.mixed;
			this.elements[1].title = this.language.single;
			this.elements[2].title = this.language.score;
			
		}
	}
</script>

<style>
	.page {
		height: 100vh;
	}
</style>
