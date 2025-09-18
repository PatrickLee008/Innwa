import request from '@/utils/request'

export function getDigitList(data) {
  return request({
    url: '/digit/get',
    method: 'get',
    params: data
  })
}
export function getDigitDetail(data) {
  return request({
    url: '/digit/get_detail',
    method: 'get',
    params: data
  })
}
export function getDigitHistoryDetail(data) {
  return request({
    url: '/digit/get_history_detail',
    method: 'get',
    params: data
  })
}
export function addDigit(data) {
  return request({
    url: '/digit/add',
    method: 'post',
    data
  })
}
export function delDigit(data) {
  return request({
    url: '/digit/remove',
    method: 'post',
    data
  })
}
export function editDigit(data) {
  return request({
    url: '/digit/edit',
    method: 'post',
    data
  })
}
export function settlementDigit(data) {
  return request({
    url: '/digit/settle',
    method: 'post',
    data
  })
}

export function addDigitByList(data) {
  return request({
    url: '/digit/add_by_list',
    method: 'post',
    data
  })
}

export function cancelDigit(data) {
  return request({
    url: '/digit/cancel',
    method: 'post',
    data
  })
}

export function getDigitSettleList(data) {
  return request({
    url: '/digit_settle/get_digit_settle_list',
    method: 'get',
    params: data
  })
}
export function reverseDigitSettle(data) {
  return request({
    url: '/digit/reverse',
    method: 'post',
    data
  })
}
export function addDigitSettle(data) {
  return request({
    url: '/digit_settle/add',
    method: 'post',
    data
  })
}
export function removeDigitSettle(data) {
  return request({
    url: '/digit_settle/remove',
    method: 'get',
    params: data
  })
}
export function startDigitSettle(data) {
  return request({
    url: '/digit_settle/start',
    method: 'post',
    data
  })
}
export function startAllDigitSettle(data) {
  return request({
    url: '/digit_settle/start_all',
    method: 'post',
    data
  })
}
export function stopDigitSettle(data) {
  return request({
    url: '/digit_settle/stop',
    method: 'post',
    data
  })
}
export function stopAllDigitSettle(data) {
  return request({
    url: '/digit_settle/stop_all',
    method: 'post',
    data
  })
}

export function getSettleSwitch(data) {
  return request({
    url: '/digit_settle/get_switch',
    method: 'get',
    params: data
  })
}
export function setSettleSwitch(data) {
  return request({
    url: '/digit_settle/set_switch',
    method: 'post',
    data
  })
}



export function get3DDigitList(data) {
  return request({
    url: '/digital_3d/get',
    method: 'get',
    params: data
  })
}
export function get3DDigitDetail(data) {
  return request({
    url: '/digital_3d/get_detail',
    method: 'get',
    params: data
  })
}
export function get3DDigitHistoryDetail(data) {
  return request({
    url: '/digital_3d/get_history_detail',
    method: 'get',
    params: data
  })
}
export function add3DDigit(data) {
  return request({
    url: '/digital_3d/add',
    method: 'post',
    data
  })
}
export function del3DDigit(data) {
  return request({
    url: '/digital_3d/remove',
    method: 'post',
    data
  })
}
export function edit3DDigit(data) {
  return request({
    url: '/digital_3d/edit',
    method: 'post',
    data
  })
}
export function settlement3DDigit(data) {
  return request({
    url: '/digital_3d/settle',
    method: 'post',
    data
  })
}


export function reverse3DDigitSettle(data) {
  return request({
    url: '/digital_3d/reverse',
    method: 'post',
    data
  })
}
export function cancel3DDigit(data) {
  return request({
    url: '/digital_3d/cancel',
    method: 'post',
    data
  })
}
