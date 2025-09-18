export default {
	data() {
		return {
			noticed: uni.getStorageSync('noticed')
		}
	},
	methods: {
		show_notice() {
			this.noticed = true
			uni.setStorageSync('noticed', true)
			let sub_title = 'လေးစားရပါသော အင်းဝမန်ဘာများရှင့်'
			let content = `ရာသီဥတုအခြေအနေကြောင့် လျှပ်စစ်မီး Wifi အင်တာနက် ပြတ်တောက်မှုများရှိနေပါသဖြင့် ငွေသွင်း/ ‌ငွေထုတ်များကို ခေတ္တရပ်နားထားမည် ဖြစ်ကြောင်း အသိပေးအပ်ပါတယ်ရှင်။

အစ်ကိုတိုရဲ့ အကောင့်လုံခြုံရေးနှင့် ငွေကြေးပျောက်ဆုံးပျောက်ရှမှုတို မရှိနိုင်ကြောင်းကိုလည်း အာမခံပါတယ်ရှင့် ယုံကြည်စိတ်ချစွာ စောင့်ဆိုင်းပေးကြပါရန် မေတ္တာရပ်ခံအပ်ပါသည်။`
			this.temp = {
				title: 'Notice',
				sub_title: sub_title,
				content: content
			}
			this.$refs.popup.open()
		},
	},
	mounted() {
			if (!this.noticed) {
				this.show_notice()
			}
	},
	onLoad(option) {
	}
}
