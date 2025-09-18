import my from './my.js'

export const tab_pages = [
]

let last_operate = null

export const toolbox = {
	/** 操作频繁警告，time_gap:操作间隔,提示信息:message
	 * @param {String} message 
	 * @param {Number} time_gap //列表索引
	 * @returns {Boolean}
	 */
	click_too_fast(time_gap = .1, message = 'click too fast') {
		var result = false;
		var now = new Date().getTime();
		if (last_operate !== null) {
			var second = (now - last_operate) / 1000;
			result = second < time_gap;
			if (message && result) {
				uni.showToast({
					title: message,
					icon: 'error',
				})
			}
		}
		last_operate = now
		return result;
	},
	generate_uid() {
	    return `${Date.now()}-${Math.floor(Math.random() * 100000)}`;
	}
}

export default toolbox;