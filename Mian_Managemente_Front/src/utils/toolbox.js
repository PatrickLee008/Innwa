import {MessageBox} from 'element-ui'
// import {postData} from '@/api/system'

const day_to_str = ['周日', '周一', '周二', '周三', '周四', '周五', '周六',]
const prefix = process.env.VUE_APP_IMAGE_PREFIX
// const prefix = 'http://192.168.99.123:9092/static/'
export const toolbox = {
  string_to_json(str) {
    str = str || '{}'
    str = str.replaceAll('\'', '"')
    return JSON.parse(str)
  },
  /** 删除空字段或者为null的属性
   * @param {Object} obj
   * @returns {Object}
   */
  clean_obj(obj) {
    obj = this.deep_clone(obj)
    for (var ob in obj) {
      if (obj[ob] == null || obj[ob] === '') {
        delete obj[ob]
      } else if (typeof obj[ob] === 'object') {
        obj[ob] = this.clean_obj(obj[ob])
      }
    }
    return obj
  },
  upload_all_image(imageList, item, table_name, that = this, func = function () {
  }, index = 0) {
    let image_list = []
    imageList.map((ele, _index) => {
      // console.log(ele)
      // console.log(that.$refs[ele.field_name])
      that.$refs[ele.field_name][0].uploadFiles.forEach((images, __index) => {
        image_list.push({
          field_name: ele.field_name,
          file: images,
        })
      })
      // let file = that.$refs[ele.field_name][0].uploadFiles[0]
      // return file && !file.id && (_index >= index) ? this.upload_image(file, _index, table_name, ele.field_name, item.id) : Promise.resolve()
    })
    let promise_list = image_list.map((images, _index) => {
      return images && !images.file.id && (_index >= index) ? this.upload_image(images.file, _index, table_name, images.field_name, item.id) : Promise.resolve()
    })
    return new Promise((resolve, reject) => {
      Promise.all(promise_list)
        .then((values) => {
          that.after_upload_image(item)
          resolve()
        })
        .catch((error) => {
          MessageBox.confirm(`${imageList[error].name}图片上传失败,是否重试`, '上传错误', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }).then(() => {
            return this.upload_all_image(imageList, item, table_name, that, func, error)
          }).catch((err) => {
            resolve()
          })
        })
    })
  },
  upload_image(params, _index, table_name, field_name, id) {
    return new Promise((resolve, reject) => {
      const formData = new FormData()
      formData.append('table_name', table_name)
      formData.append('data_id', id)
      formData.append('field_name', field_name)
      const file = params.raw
      formData.append('file', file)
      postData('uploaded_image', formData).then((res) => {
        if (res.code === 20000) {
          reject(resolve())
          params.onSuccess() // 上传成功的图片会显示绿色的对勾
        } else {
          reject(_index)
          params.onError()
        }
      })
        .catch((res) => {
          reject(_index)
        })
    })
  },
  parse_form_imageList(imageList, form) {
    imageList.forEach(ele => {
      if (form.hasOwnProperty(ele.field_name)) {
        form[ele.field_name].forEach(_ele => {
          _ele.url = prefix + _ele.address
        })
      } else {
        form[ele.field_name] = []
      }
    })
  },
  /**
   * @param {String} str
   * @param {String} Num
   * @param {Number} len
   * @returns {String}
   */
  pad_number(str = '', Num = '0', len = 2) {
    return String(str).padStart(len, Num)
  },
  /**
   * @param {Object} obj
   * @param {Array}props_to_ajust
   * @returns {Object}
   */
  adjust_obj_prop(obj, props_to_ajust) {
    let newObj = {}
    let newObj2 = this.deep_clone(obj)
    props_to_ajust.forEach(prop => {
      if (newObj2.hasOwnProperty(prop)) {
        newObj[prop] = newObj2[prop]
      }
    })
    return newObj
  },
  /**
   * @param {Object} obj
   * @param {Array}prop_to_remove
   * @returns {Array}
   */
  remove_obj_prop(obj, prop_to_remove) {
    let newObj = this.deep_clone(obj)
    prop_to_remove.forEach(prop => {
      if (newObj.hasOwnProperty(prop)) {
        delete newObj[prop]
      }
    })
    return newObj
  },
  /**
   * 获取日期列表
   * @param {Number} len //长度
   * @param {Number} first_day
   * @param {String} today_label //当天不显示日期显示今天
   * @returns {Object}
   */
  get_day_list(len = 7, first_day = 0, today_label = '今天') {
    let days = []
    for (let i = 0; i < len; i++) {
      let dates = this.get_day(0 + i)
      dates.day_str = first_day + i == 0 && today_label ? today_label : dates.w,
        days.push(dates)
    }
    return days
  },
  /**
   * 获取多少天后的日期
   * @param {Object} day //0为当天
   * @returns {Object}
   */
  get_day: function(day = 0) {
    let today = new Date();
    let targetday_milliseconds = today.getTime() + 1000 * 60 * 60 * 24 * day;
    today.setTime(targetday_milliseconds);
    let tYear = today.getFullYear();
    let tMonth = today.getMonth();
    let tDate = today.getDate();
    let tWeek = today.getDay();
    let time = parseInt(today.getTime() / 1000);
    tMonth = this.pad_number(tMonth + 1);
    tDate = this.pad_number(tDate);

    return {
      't': time,
      'y': tYear,
      'm': tMonth,
      'd': tDate,
      'mdfs': `${tMonth}/${tDate}`,
      'md': `${tMonth}-${tDate}`,
      'ymdfs': `${tYear}/${tMonth}/${tDate}`,
      'ymd': `${tYear}-${tMonth}-${tDate}`,
      'cnymd': `${tYear}年${tMonth}月${tDate}日`,
      'w': day_to_str[tWeek]
    };
  },
  /**
   * 计算时间差
   * @param {String} time1 //格式2024-08-12 19:59:53
   * @param {String} time2 //
   * @returns {String}  //格式 19:59:53
   */
  time_gap(time1, time2) {
    // 将时间字符串转换为 Date 对象
    const date1 = new Date(time1);
    const date2 = new Date(time2);

    // 计算时间差（以毫秒为单位）
    const diff = Math.abs(date2 - date1);

    // 计算小时、分钟和秒数
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);

    // 格式化为 hh:mm:ss
    const formattedTime =
      `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

    return formattedTime;
  },
  format_date(date) {
    const year = date.getFullYear()
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const day = date.getDate().toString().padStart(2, '0')
    return `${year}-${month}-${day}`
  },
  /**
   * @param {Object} obj
   * @returns {Object}
   */
  fake_deep_clone(obj) {
    return JSON.parse(JSON.stringify(obj))
  },
  /**深克隆
   * @param {Object} source
   * @returns {Object}
   */
  deep_clone(source) {
    if (!source && typeof source !== 'object') {
      throw new Error('error arguments', ` source:`, source)
    }
    const targetObj = source.constructor === Array ? [] : {}
    Object.keys(source).forEach(keys => {
      if (source[keys] && typeof source[keys] === 'object') {
        targetObj[keys] = this.deep_clone(source[keys])
      } else {
        targetObj[keys] = source[keys]
      }
    })
    return targetObj
  },
  /**前端导出表格
   * @param {Array} headers //表头
   * @param {Array} _list //数据列表
   * @param {Array} attrs //数据参数
   * @param file_name //文件名称
   */
  export_excel(headers,_list,attrs,file_name){
    import('@/vendor/Export2Excel').then(excel => {
      const tHeader = headers || []
      const filter_attr = attrs || []
      const list = _list ||[]
      const name= file_name||'导出文件'
      const auto_width= true
      const book_type= 'xlsx'
      const format_json = function(filterVal, jsonData) {
        return jsonData.map(v => filterVal.map(j => {
          if (j === 'timestamp') {
            return parseTime(v[j])
          } else {
            return v[j] || ''
          }
        }))
      }
      const data = format_json(filter_attr, list)
      excel.export_json_to_excel({
        header: tHeader,
        data,
        filename: name,
        autoWidth: auto_width,
        bookType: book_type
      })
    })
  },
  getDateRangeFromString(type) {
    const now = moment()
    let startDate, endDate
    const weekOfday = moment().format('E')
    switch (type) {
      case '今天':
        startDate = now.startOf('day')
        endDate = now.endOf('day')
        break
      case '昨天':
        startDate = now.clone().subtract(1, 'days').startOf('day')
        endDate = now.clone().subtract(1, 'days').endOf('day')
        break
      case '本周':
        startDate = moment().subtract(weekOfday - 1, 'days')
        endDate = now.endOf('day')
        break
      case '上周':
        startDate = moment(now).clone().subtract(1, 'weeks').startOf('isoWeek')
        endDate = moment(now).clone().subtract(1, 'weeks').endOf('isoWeek')
        break
      case '本月':
        startDate = now.clone().startOf('month')
        endDate = now.endOf('day')
        break
      case '上月':
        startDate = now.clone().subtract(1, 'months').startOf('month')
        endDate = now.clone().subtract(1, 'months').endOf('month')
        break
      case '本年':
        startDate = now.clone().startOf('year')
        endDate = now.endOf('day')
        break
      case '上年':
        startDate = now.clone().subtract(1, 'years').startOf('year')
        endDate = now.clone().subtract(1, 'years').endOf('year')
        break
      default:
        throw new Error('Invalid type')
    }
    let res = {
      startDate: startDate.format('YYYY-MM-DD'),
      endDate: endDate.format('YYYY-MM-DD')
    }
    // console.log(res)
    return res
  }
}
