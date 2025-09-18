var reverseReg = /^[0-9][0-9]\//; //反选
var beforeByOrderReg = /^[0-9]\*/; //前顺序
var afterByOrderReg = /\*[0-9]/; //后顺序
var containtReg = /^[0-9]\+/ //包含
var addReg = /^[0-9]\-/ //相加组合
var brotherReg = /B|b/ //兄弟组合
var afterEvenRex = /^[0-9][S,s]/ //后双
var beforeEvenRex = /^[S,s][0-9]/ //前双

var beforeOddRex = /^[M,m][0-9]/ //前单
var afterOddRex = /^[0-9][M,m]/ //后单

var powerReg = /P|p/ //power组合
var nakatReg = /N|n/

var arr100 = (Array.from(Array(100).keys()));
var arr1000 = (Array.from(Array(1000).keys()));
var number_2d = arr100.map(ele => {
	return ele.toString().padStart(2, '0')
});
var number_3d = arr1000.map(ele => {
	return ele.toString().padStart(3, '0')
});
var number_2d_items = arr100.map(ele => {
	return {
		label: ele.toString().padStart(2, '0'),
		selected: false
	}
});
var number_3d_items = arr1000.map(ele => {
	return {
		label: ele.toString().padStart(3, '0'),
		selected: false
	}
});



var number_rule = {
	//玩法解析
	analysis: function(betContent) {
		//拆分字母
		var rule = '';
		var resultList = []
		//反向组合,例如  01/  = 01 , 10 
		if (reverseReg.test(betContent)) {
			resultList = this.reverseFunc(betContent);
			rule = 'R';
		}

		if (brotherReg.test(betContent)) {
			resultList = this.brotherFunc(betContent);
			rule = 'B'
		}

		//前后顺序,例如 7* = 70，71,72 ...
		if (beforeByOrderReg.test(betContent) || afterByOrderReg.test(betContent)) {
			resultList = this.byOrderFunc(betContent);

			if (beforeByOrderReg.test(betContent)) {
				rule = 'N*'
			} else if (afterByOrderReg.test(betContent)) {
				rule = '*N'
			}
		}

		//包含关系，例如 7+ = 07,17,27... ，70,71,72***; 实际上就是 7* 和 *7 的并集；
		if (containtReg.test(betContent)) {
			resultList = this.contaitsFunc(betContent);
			rule = 'N+'
		}

		if (addReg.test(betContent)) {
			resultList = this.addFunc(betContent);
			rule = 'N-'
		}

		if (afterEvenRex.test(betContent) || beforeEvenRex.test(betContent)) {
			resultList = this.beforeAndAfterEven(betContent);
			if (afterEvenRex.test(betContent)) {
				rule = 'NS'
			} else if (beforeEvenRex.test(betContent)) {
				rule = 'SN'
			}
		}

		if (beforeOddRex.test(betContent) || afterOddRex.test(betContent)) {
			resultList = this.beforeAndAfterOdd(betContent);
			if (afterOddRex.test(betContent)) {
				rule = 'NM'
			} else if (beforeOddRex.test(betContent)) {
				rule = 'MN'
			}
		}

		//双双和单单
		if (betContent == '++') {
			resultList = this.evenOddFunc(4);
			rule = '++'
		}
		if (betContent == '--') {
			resultList = this.evenOddFunc(3);
			rule = '--'
		}

		//双单和单双组合
		if (betContent == '+-') {
			resultList = this.evenOddFunc(2);
			rule = '+-'
		}
		if (betContent == '-+') {
			resultList = this.evenOddFunc(1);
			rule = '-+'
		}

		if (betContent == '**') {
			resultList = this.pairsFunc();
			rule = '**'
		}

		//偶数对子
		if (betContent == '+*') {
			resultList = this.evenPairsFunc();
			rule = '+*'
		}

		//奇数对子
		if (betContent == '-*') {
			resultList = this.oddPairsFunc();
			rule = '-*'
		}

		if (betContent.indexOf('..') > -1) {
			resultList = this.numberCombination(betContent, 1);
			rule = 'N1N2N3..'
		} else if (betContent.indexOf('.') > -1) {
			resultList = this.numberCombination(betContent, 0);
			rule = 'N1N2N3.'
		}

		if (powerReg.test(betContent)) {
			resultList = this.powerFunc();
			rule = 'power'
		}

		if (nakatReg.test(betContent)) {
			resultList = this.nakatFunc();
			rule = 'nakat'
		}

		var resultObj = {
			// 'rule': rule,
			'rule': number_rule_info[rule] ? (number_rule_info[rule]).name : 'အကွက်တွဲများ',
			'resultList': resultList
		};
		return resultObj;

	},
	reverseFunc: function(betContent) {
		var resultList = [];
		var numberonly = /(^[0-9]*$)/;
		var loc = betContent.indexOf('/')
		var str = betContent.substring(0, loc);
		if (!numberonly.test(str)) {
			return []
		}
		var equal = str === (str[1, 1] + str[0, 0])
		return equal ? [str] : [str, (str[1, 1] + str[0, 0])]

	},
	//前后顺序玩法
	byOrderFunc: function(betContent) {
		var resultList = [];
		for (var i = 0; i < 10; i++) {
			//第一位是*号
			var content = '';
			if (betContent.indexOf('*') == 0) {
				content = i.toString() + betContent.substring(1, 2);
			} else {
				content = betContent.substring(0, 1) + i.toString();
			}
			resultList.push(content);
		}
		return resultList;
	},
	//包含玩法
	contaitsFunc: function(betContent) {
		var resultList = [];
		var para1 = betContent.substring(0, 1) + '*';
		var para2 = '*' + betContent.substring(0, 1);
		var list1 = this.byOrderFunc(para1);
		var list2 = this.byOrderFunc(para2);

		resultList = list1.concat(list2.filter(function(val) {
			return !(list1.indexOf(val) > -1)
		}))

		return resultList;
	},
	//兄弟玩法
	brotherFunc: function() {
		return ['01', '12', '23', '34', '45', '56', '67', '78', '89', '90', '09', '98', '87', '76', '65', '54',
			'43', '32',
			'21', '10'
		];
	},
	pairsFunc: function() {
		return ['00', '11', '22', '33', '44', '55', '66', '77', '88', '99'];
	},
	//偶数对子
	evenPairsFunc: function() {
		return ['00', '22', '44', '66', '88'];
	},
	//奇数对子
	oddPairsFunc: function() {
		return ['11', '33', '55', '77', '99']
	},
	//相加
	addFunc: function(betContent) {
		var resultList = [];
		var num = betContent.substring(0, 1);
		for (var i = 0; i <= num; i++) {
			var j = num - i;
			var ele = i.toString() + j.toString();
			resultList.push(ele);
		}
		return resultList;
	},
	//双单组合
	evenOddFunc: function(type) {
		var resultList = [];
		for (var i = 0; i < 10; i++) {
			for (var j = 0; j < 10; j++) {

				//单单组合
				if (i % 2 != 0 && j % 2 != 0 && type == 3) {
					var ele = i.toString() + j.toString();
					resultList.push(ele);
				}
				//双双组合
				if (i % 2 == 0 && j % 2 == 0 && type == 4) {
					var ele = i.toString() + j.toString();
					resultList.push(ele);
				}

				//单双组合
				if (i % 2 != 0 && j % 2 == 0 && type == 1) {
					var ele = i.toString() + j.toString();
					resultList.push(ele);
				}
				//双单组合
				if (i % 2 == 0 && j % 2 != 0 && type == 2) {
					var ele = i.toString() + j.toString();
					resultList.push(ele);
				}
			}
		}
		return resultList;
	},

	//前双、后双
	beforeAndAfterEven: function(betContent) {
		//前双
		var resultList = [];
		if (betContent.indexOf('s') == 0 || betContent.indexOf('S') == 0) {
			var num = betContent.substring(1, 2);
			for (var i = 0; i < 10; i++) {
				if (i % 2 == 0) {
					var ele = i.toString() + num;
					resultList.push(ele);
				}
			}
		} else if (betContent.indexOf('s') == 1 || betContent.indexOf('S') == 1) {
			var num = betContent.substring(0, 1);
			for (var i = 0; i < 10; i++) {
				if (i % 2 == 0) {
					var ele = num + i.toString();
					resultList.push(ele);
				}
			}
		}
		return resultList;
	},
	//前单，后单
	beforeAndAfterOdd: function(betContent) {
		//前双
		var resultList = [];
		if (betContent.indexOf('m') == 0 || betContent.indexOf('M') == 0) {
			var num = betContent.substring(1, 2);
			for (var i = 0; i < 10; i++) {
				if (i % 2 != 0) {
					var ele = i.toString() + num;
					resultList.push(ele);
				}
			}
		} else if (betContent.indexOf('m') == 1 || betContent.indexOf('M') == 1) {
			var num = betContent.substring(0, 1);
			for (var i = 0; i < 10; i++) {
				if (i % 2 != 0) {
					var ele = num + i.toString();
					resultList.push(ele);
				}
			}
		}
		return resultList;
	},
	powerFunc: function() {
		return ['05', '16', '27', '38', '49', '50', '61', '72', '83', '94']
	},
	nakatFunc: function() {
		return ['07', '18', '24', '35', '42', '53', '69', '70', '81', '96']
	},
	numberCombination: function(betContent, type) {
		var resultList = [];
		var numberonly = /(^[0-9]*$)/;
		var loc = betContent.indexOf('.')
		var str = betContent.substring(0, loc);
		if (!numberonly.test(str)) {
			return []
		}
		var arr = str.split("")
		// console.log(arr)
		for (var i = 0; i < arr.length; i++) {
			for (var j = 0; j < arr.length; j++) {
				if (type == 0) {
					if (arr[i] != arr[j]) {
						var result = arr[i].toString() + arr[j].toString();
						resultList.push(result);
					}
				} else {
					var result = arr[i].toString() + arr[j].toString();
					resultList.push(result);
				}
			}
		}
		return resultList;
	},
};

let number_play_info = {

	get_2d_items: function() {
		var items = arr100.map(ele => {
			return {
				label: ele.toString().padStart(2, '0'),
				selected: false,
				money: 0,
			}
		});
		return items
	},
	get_3d_items: function() {
		var items = arr1000.map(ele => {
			return {
				label: ele.toString().padStart(3, '0'),
				selected: false,
				money: 0,
			}
		});
		return items
	},
	'SOD': {
		button: [{
				lang_text: 'big',
				value: 'get_big',
			},
			{
				lang_text: 'small',
				value: 'get_small',
			},
			{
				lang_text: 'odd',
				value: 'get_odd',
			},
			{
				lang_text: 'even',
				value: 'get_even',
			},
			{
				lang_text: 'brother',
				value: 'get_bro',
			},


			// 第二行
			{
				lang_text: 'eveneven',
				value: 'get_eveneven',
			},
			{
				lang_text: 'evenodd',
				value: 'get_evenodd',
			},
			{
				lang_text: 'oddeven',
				value: 'get_oddeven',
			},
			{
				lang_text: 'oddodd',
				value: 'get_oddodd',
			},
			{
				lang_text: 'same',
				value: 'get_same',
			},
		],
		button2: [{
				lang_text: 'big',
				value: 'get_big_3d',
			},
			{
				lang_text: 'small',
				value: 'get_small_3d',
			},
			{
				lang_text: 'odd',
				value: 'get_odd_3d',
			},
			{
				lang_text: 'even',
				value: 'get_even_3d',
			},
			{
				lang_text: 'same',
				value: 'get_same_3d',
			},
		],
	},
	'constellation': {
		button: [{
			lang_text: 'Constellation',
			sub_lang_text: ' 07,18,24,35,69',
			value: 'get_constellation',
		}, {
			lang_text: 'Constellation',
			sub_lang_text: ' R 70,81,42,53,96',
			value: 'get_constellation_r',
		}, {
			lang_text: 'Power',
			sub_lang_text: ' 05,16,27,38,49',
			value: 'get_power',
		}, {
			lang_text: 'Power',
			sub_lang_text: ' R 50,61,72,83,94',
			value: 'get_power_r',
		}, ],
	},
	select_20: [{
		label: '00-19',
		value: 0,
	}, {
		label: '20-39',
		value: 20,
	}, {
		label: '40-59',
		value: 40,
	}, {
		label: '60-79',
		value: 60,
	}, {
		label: '80-99',
		value: 80,
	}],
	select_200: [{
		label: '000-199',
		value: 0,
	}, {
		label: '200-399',
		value: 200,
	}, {
		label: '400-599',
		value: 400,
	}, {
		label: '600-799',
		value: 600,
	}, {
		label: '800-999',
		value: 800,
	}],



	get_small: function() {
		return number_2d.slice(0, 50)
	},

	get_big: function() {
		return number_2d.slice(50)
	},
	get_odd: function() {
		var numbers = number_2d.filter(ele => {
			return ele % 2 == 1
		});
		return numbers
	},
	get_even: function() {
		var numbers = number_2d.filter(ele => {
			return ele % 2 == 0
		});
		return numbers
	},
	get_eveneven: function() {
		var numbers = number_2d.filter(ele => {
			return ele.slice(0, 1) % 2 == 0 && ele.slice(1) % 2 == 0
		});
		return numbers
	},
	get_evenodd: function() {
		var numbers = number_2d.filter(ele => {
			return ele.slice(0, 1) % 2 == 0 && ele.slice(1) % 2 == 1
		});
		return numbers
	},
	get_oddeven: function() {
		var numbers = number_2d.filter(ele => {
			return ele.slice(0, 1) % 2 == 1 && ele.slice(1) % 2 == 0
		});
		return numbers
	},
	get_oddodd: function() {
		var numbers = number_2d.filter(ele => {
			return ele.slice(0, 1) % 2 == 1 && ele.slice(1) % 2 == 1
		});
		return numbers
	},
	get_same: function() {
		var numbers = number_2d.filter(ele => {
			return ele.slice(0, 1) == ele.slice(1)
		});
		return numbers
	},
	get_include_number: function(num) {
		var numbers = number_2d.filter(ele => {
			return ele.slice(0, 1) == num || ele.slice(1) == num
		});
		return numbers
	},
	get_first_number: function(num) {
		var numbers = number_2d.filter(ele => {
			return ele.slice(0, 1) == num
		});
		return numbers
	},
	get_sum_number: function(num) {
		var numbers = number_2d.filter(ele => {
			return String(parseInt(ele.slice(0, 1)) + parseInt(ele.slice(1))).slice(-1) == num
		});
		return numbers
	},
	get_second_number: function(num) {
		var numbers = number_2d.filter(ele => {
			return ele.slice(1) == num
		});
		return numbers
	},
	get_first_number_3d: function(num) {
		var numbers = number_3d.filter(ele => {
			return ele.slice(0, 1) == num
		});
		return numbers
	},
	get_second_number_3d: function(num) {
		var numbers = number_3d.filter(ele => {
			return ele.slice(2) == num
		});
		return numbers
	},
	get_bro: function(num) {
		return '01,09,10,12,21,23,32,34,43,45,54,56,65,67,76,78,87,89,90,98'.split(',')
	},
	get_constellation: function(num) {
		return '07,18,24,35,69'.split(',')
	},
	get_constellation_r: function(num) {
		return '70,81,42,53,96'.split(',')
	},
	get_power: function(num) {
		return '05,16,27,38,49'.split(',')
	},
	get_power_r: function(num) {
		return '50,61,72,83,94'.split(',')
	},
	get_20_number: function(num) {
		let a = num == 0 ? 0 : num - 1
		return number_2d.slice(num, num + 20)
	},

	get_small_3d: function() {
		return number_3d.slice(0, 500)
	},
	get_big_3d: function() {
		return number_3d.slice(500)
	},
	get_odd_3d: function() {
		var numbers = number_3d.filter(ele => {
			return ele % 2 == 1
		});
		return numbers
	},
	get_even_3d: function() {
		var numbers = number_3d.filter(ele => {
			return ele % 2 == 0
		});
		return numbers
	},
	get_include_number_3d: function(num) {
		var numbers = number_3d.filter(ele => {
			return ele.slice(0, 1) == num || ele.slice(1, 2) == num || ele.slice(2) == num
		});
		return numbers
	},
	get_first_number_3d: function(num) {
		var numbers = number_3d.filter(ele => {
			return ele.slice(0, 1) == num
		});
		return numbers
	},
	get_second_number_3d: function(num) {
		var numbers = number_3d.filter(ele => {
			return ele.slice(2) == num
		});
		return numbers
	},
	get_200_number: function(num) {
		let a = num == 0 ? 0 : num - 1
		return number_3d.slice(num, num + 200)
	},
	get_same_3d: function() {
		var numbers = number_3d.filter(ele => {
			return ele.slice(0, 1) == ele.slice(1, 2) && ele.slice(0, 1) == ele.slice(2)
		});
		return numbers
	},
};
var number_rule_info = {
	'R': {
		name: 'R',
		number: '2-ကွက်',
		example: '01/',
		result: '01/ = 01,10'
	},
	'B': {
		name: 'ညီကို',
		number: '20-ကွက်',
		example: 'B',
		result: 'B = 01,09,10,12,21,23,32,34,43,45,54,56,65,67,76,78,87,89,90,98',
	},
	'*N': {
		name: 'ရှေ့စီးရီး',
		number: '10-ကွက်',
		example: '*7',
		result: '*7 = 07,17,27,37,47,57,67,77,78,79',
	},
	'N*': {
		name: 'နောက်စီးရီး',
		number: '10-ကွက်',
		example: '7*',
		result: '7* = 70,71,72,73,74,75,76,77,78,79',
	},
	'++': {
		name: 'စုံစုံ',
		number: '25-ကွက်',
		example: '++',
		result: '++ = 00,02,04,06,08,20,22,24,26,28,40,42,44,46,48,60,62,64,66,68,80,82,84,86,88',
	},
	'--': {
		name: 'မမ',
		number: '25-ကွက်',
		example: '--',
		result: '-- = 11,13,15,17,19,31,33,35,37,39,51,53,55,57,59,71,73,75,77,79,91,93,95,97,99',
	},
	'+-': {
		name: 'စုံမ',
		number: '25-ကွက်',
		example: '+-',
		result: '+- = 01,03,05,07,09,21,23,25,27,29,41,43,45,47,49,61,63,65,67,69,81,83,85,87,89',
	},
	'-+': {
		name: 'မစုံ',
		number: '25-ကွက်',
		example: '-+',
		result: '-+ = 10,12,14,16,18,30,32,34,36,38,50,52,54,56,58,70,72,74,76,78,90,92,94,96,98',
	},
	'N+': {
		name: 'တစ်လုံးပါ',
		number: '19-ကွက်',
		example: '7+',
		result: '7+ = 07,17,27,37,47,57,67,70,71,72,73,74,75,76,77,78,79,87,97',
	},
	'**': {
		name: 'အပူး',
		number: '10-ကွက်',
		example: '**',
		result: '** = 00,11,22,33,44,55,66,77,88,99',
	},
	'+*': {
		name: 'စုံအပူး',
		number: '5-ကွက်',
		example: '+*',
		result: '+* = 00,22,44,66,88',
	},
	'-*': {
		name: 'မအပူး',
		number: '5-ကွက်',
		example: '-*',
		result: '-* = 11,33,55,77,99',
	},
	'N-': {
		name: 'ဘရိတ်',
		number: '10-ကွက်',
		example: '7-',
		result: '7- = 07,16,25,34,43,52,61,70,89,98',
	},
	'P': {
		name: 'ပါဝါ',
		number: '10-ကွက်',
		example: 'P',
		result: 'P = 05,16,27,38,49,50,61,72,83,94',
	},
	'N': {
		name: 'နက္ခတ်',
		number: '10-ကွက်',
		example: 'N',
		result: 'N = 07,18,24,35,42,53,69,70,81,96',
	},
	'SN': {
		name: 'ရှေ့စုံ',
		number: '5-ကွက်',
		example: 'S7',
		result: 'S7 = 07,27,47,67,87',
	},
	'NS': {
		name: 'နောက်စုံ',
		number: '5-ကွက်',
		example: '7S',
		result: '7S = 70,72,74,76,78',
	},
	'MN': {
		name: 'ရှေ့မ',
		number: '5-ကွက်',
		example: 'M7',
		result: 'M7 = 17,37,57,77,97',
	},
	'NM': {
		name: 'နောက်မ',
		number: '5-ကွက်',
		example: '7M',
		result: '7M = 17,37,57,77,97',
	},
	'N1N2N3.': {
		name: 'အပြီးပေါက်အပူးပါ',
		number: '-ကွက်',
		example: '123',
		result: '123. = 11,12,13,21,22,23,31,32,33',
	},
	'N1N2N3..': {
		name: 'အပြီးပေါက်အပူးမပါ',
		number: '-ကွက်',
		example: '123..',
		result: '123.. = 12,13,21,23,31,32',
	}
};

export default {
	number_rule,
	number_rule_info,
	number_play_info,
}
