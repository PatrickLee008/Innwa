<template>
	<view>
		<cu-custom bgColor="bg-purple" isBack="true">
			<block slot="content">{{language.bank}}</block>
		</cu-custom>
		<view class="cu-list menu-avatar">
			<view class="cu-item" v-for="(item,index) in list" :key="index">
				<view class="content">
					<view>
						<text class="margin-right-sm">{{item.BANK_TYPE}}</text>
						<text class="cu-tag sm bg-green" v-if="item.PRIMARY_CARD">default</text>
					</view>
					<view class="text-gray text-sm flex">
						<view class="text-cut">
							<text class="margin-right-xs">{{item.CARD_NUM}}</text>
						</view>
					</view>
				</view>
				<view class="action">
					<button class="cu-btn sm bg-green margin-right-sm cuIcon-check shadow" @click="setDefault(item.ID)"></button>
					<button class="cu-btn sm bg-red cuIcon-delete shadow" @click="removeBank(item.ID)"></button>
				</view>
			</view>

		</view>
		<image @click="add" src="../../static/icon/add.png" class="add"></image>

		<uni-popup ref="popup" type="center">
			<view class="bg-white">
				<form>
					<view class="cu-form-group border-bottom">
						<view class="title">{{language.bank}}</view>
						<picker @change="PickerChange" :value="index" :range="type_list">
							<view class="picker">
								{{card_conf.card_type}}
							</view>
						</picker>
					</view>

					<view class="cu-form-group border-bottom">
						<view class="title">{{language.cartNumber}}</view>
						<input type="number" placeholder="please select" v-model="card_conf.card_num"></input>
					</view>

					<button @click="submit" class="bg-purple margin-top-sm submit">Yes</button>
				</form>
			</view>
		</uni-popup>
	</view>
</template>

<script>
	import uniPopup from "@/components/uni-popup/uni-popup.vue";
	import config from '../../utils/config.js'

	export default {
		components: {
			uniPopup
		},
		data() {
			return {
				language: config.language,
				index: -1,
				status: 'more',
				page: 1,
				limit: 15,
				list: [],
				type_list: ['KBZ','WaveMoney'],
				card_conf:{
					card_type:'KBZ',
					card_num:'',
				},
				contentText: {
					contentdown: 'more',
					contentrefresh: 'loading',
					contentnomore: 'no more'
				}
			}
		},
		methods: {
			removeBank(bankId) {
				var _this = this;
				if(_this.$toolbox.click_too_fast(.5)) return
				var para = {
					ID: bankId,
				}
				this.$http.post('/bank_card/delete',para, (res) => {
					if (res.data.code == 20000) {
						uni.showToast({
							title: 'delete success',
							icon: 'success',
							duration: 2000
						})
						_this.getList();
					}
				})
			},
			setDefault(bankId) {
				var _this = this;
				if(_this.$toolbox.click_too_fast(.5)) return
				var para = {
					ID: bankId,
				}
				this.$http.post('/bank_card/set_default',para, (res) => {
					if (res.data.code == 20000) {
						uni.showToast({
							title: 'set primary card success',
							icon: 'success',
							duration: 2000
						})
						_this.getList();
					}
				})
			},
			getList() {
				var _this = this;
				var para = {
					page: _this.page,
					limit: _this.limit
				}
				_this.list.length = 0;
				_this.$http.get('/bank_card/get', {
					data: para
				}, (res) => {
					if (res.data.code == 20000) {
						var results = res.data.bank_cards;
						results.forEach(element => {
							_this.list.push(element);
						})
						if (results.length == 0) {
							_this.status = 'noMore'
						} else {
							_this.status = 'more'
						}
					}
				})
			},
			add() {
				this.$refs.popup.open()
			},
			PickerChange(e) {
				let index = e.detail.value
				this.index = index
				this.card_conf.card_type = this.type_list[index]
			},
			submit() {
				var _this = this;
				var para = {
					CARD_NUM: _this.card_conf.card_num,
					BANK_TYPE: _this.card_conf.card_type,
				}

				_this.$http.post('/bank_card/add', para, (res) => {
					if (res.data.code == 20000) {
						uni.showToast({
							title: 'add success',
							icon: 'success',
							duration: 2000
						})
						_this.getList();
					}
					_this.$refs.popup.close()
				})
			}
		},
		onLoad() {
			this.getList();
		}
	}
</script>

<style>
	.action {
		width: 100px !important;
	}

	.submit {
		border-radius: 0;
	}

	input {
		background-color: lightgrey;
		height: 30px;
		border-radius: 4px;
		padding-left: 5px;
	}

	.add {
		position: fixed;
		height: 20vw;
		width: 20vw;
		bottom: 2px;
		left: 40vw;
	}

	.content {
		left: 12px !important;
	}

	.border-bottom {
		border: 1px solid lightgrey;
	}
</style>
