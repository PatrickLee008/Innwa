<template name="matchList">
	<view>
		<view class="bg-white padding" v-for="(league,index) in list">
			<view class="bg-purple radius">
				{{league.name}}
			</view>
			<view v-for="(match,_index) in league.matchList" class="team" :class="{'bg-lightgrey':_index%2==0}">

				<view class="grid text-center col-4">
					<view>{{language.team}}</view>
					<view class="topic_cont_text" :class="{'text-red':match.ATTR[0].LOSE_TEAM=='1'}">{{match.HOST_TEAM}}</view>
					<view>VS</view>
					<view class="topic_cont_text" :class="{'text-red':match.ATTR[0].LOSE_TEAM=='2'}">{{match.GUEST_TEAM}}</view>
				</view>

				<view v-for="(attr,__index) in match.ATTR" v-if="type=='mixed'">
					<view v-if="attr.MATCH_ATTR_TYPE=='4'" class="grid margin-top text-center col-4">
						<view>{{language.body}}</view>
						<view class="border" @click="betClick(1,index,_index,__index)" :class="{'bg-cyan':attr.host_selected}">{{attr.ODDS}}</view>
						<view class="border">{{attr.REAL_ODDS}}</view>
						<view class="border" @click="betClick(2,index,_index,__index)" :class="{'bg-cyan':attr.guest_selected}">{{attr.ODDS_GUEST}}</view>
					</view>

					<view v-if="attr.MATCH_ATTR_TYPE=='5'" class="grid margin-top text-center col-4">
						<view>{{language.goal}}</view>
						<view class="border" @click="betClick(1,index,_index,__index)" :class="{'bg-cyan':attr.host_selected}">{{language.over}}</view>
						<view class="border">{{attr.REAL_ODDS}}</view>
						<view class="border" @click="betClick(2,index,_index,__index)" :class="{'bg-cyan':attr.guest_selected}">{{language.under}}</view>
					</view>

					<view v-if="attr.MATCH_ATTR_TYPE=='7'" class="grid margin-top text-center col-4">
						<view>{{language.odd_even}}</view>
						<view class="border" @click="betClick(1,index,_index,__index)" :class="{'bg-cyan':attr.host_selected}">{{language.odd}}</view>
						<view class="border">{{attr.REAL_ODDS}}</view>
						<view class="border" @click="betClick(2,index,_index,__index)" :class="{'bg-cyan':attr.guest_selected}">{{language.even}}</view>
					</view>
				</view>

				<view v-for="(attr,__index) in match.ATTR" v-if="type=='single'">
					<view v-if="attr.MATCH_ATTR_TYPE=='1'" class="grid margin-top text-center col-4">
						<view>{{language.body}}</view>
						<view class="border" @click="betClick(1,index,_index,__index)" :class="{'bg-cyan':attr.host_selected}">{{attr.ODDS}}</view>
						<view class="border" :class="{'bg-red light':attr.change==true}">{{attr.REAL_ODDS}}</view>
						<view class="border" @click="betClick(2,index,_index,__index)" :class="{'bg-cyan':attr.guest_selected}">{{attr.ODDS_GUEST}}</view>
					</view>

					<view v-if="attr.MATCH_ATTR_TYPE=='2'" class="grid margin-top text-center col-4">
						<view>{{language.goal}}</view>
						<view class="border" @click="betClick(1,index,_index,__index)" :class="{'bg-cyan':attr.host_selected}">{{language.over}}</view>
						<view class="border" :class="{'bg-red light':attr.change==true}">{{attr.REAL_ODDS}}</view>
						<view class="border" @click="betClick(2,index,_index,__index)" :class="{'bg-cyan':attr.guest_selected}">{{language.under}}</view>
					</view>

					<view v-if="attr.MATCH_ATTR_TYPE=='6'" class="grid margin-top text-center col-4">
						<view>{{language.odd_even}}</view>
						<view class="border" @click="betClick(1,index,_index,__index)" :class="{'bg-cyan':attr.host_selected}">{{language.odd}}</view>
						<view class="border">{{attr.REAL_ODDS}}</view>
						<view class="border" @click="betClick(2,index,_index,__index)" :class="{'bg-cyan':attr.guest_selected}">{{language.even}}</view>
					</view>
				</view>

				<view class="grid margin-top text-center col-2">
					<view class="grid col-2">
						<view>{{language.time}}</view>
					</view>
					<view>{{match.MATCH_TIME}}</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	import config from '../../utils/config.js'
	import Vue from "vue";
	export default {
		name: "matchList",
		props: [
			"list", "type"
		],
		data() {
			return {
				language: config.language,
				num: 0
			};
		},
		methods: {
			betClick(type, index, _index, __index) {
				var _this = this;
				var match = _this.list[index].matchList[_index];
				_this.num = 0;
				match.ATTR.forEach((attr, i) => {
					if (i == __index) {
						if (type == '1') {
							attr.host_selected = true;
							attr.guest_selected = false;
						} else {
							attr.host_selected = false;
							attr.guest_selected = true;
						}
						_this.num++;  
					} else {
						attr.host_selected = false;
						attr.guest_selected = false;
					}
				})
				console.log(JSON.stringify(_this.list[index].matchList[_index].ATTR[__index]))
				Vue.set(_this.list[index].matchList, match, _index);
			},
		}
	}
</script>

<style>
	.bg-lightgrey {
		background-color: #F2F2F2;
	}

	.team {
		border-bottom: 1px solid #E2E2E2;
		margin-bottom: 8px;
	}

	.border {
		border: 1px solid #E2E2E2;
	}

	.border-bottom {
		border-bottom: 1px solid #E2E2E2;
	}

	.text-center {
		height: 32px;
		line-height: 32px;
	}

	.margin-top {
		margin-top: 8px;
	}

	.center {
		text-align: center;
	}

	.grey {
		background-color: #F2F2F2;
		color: #666666;
	}

	.row {
		width: 350px;
		text-align: center;
		padding: 8px 0 8px 0;
	}
</style>
