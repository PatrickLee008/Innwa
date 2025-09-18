import request from '@/utils/request'

export function getOrderCopyList(data) {
  return request({
    url: '/order_copy/get',
    method: 'get',
    params: data
  })
}
export function getOrderList(data) {
  return request({
    url: '/order/get',
    method: 'get',
    params: data
  })
}
export function getOrderHistoryList(data) {
  return request({
    url: '/order/get_history',
    method: 'get',
    params: data
  })
}
export function cancelOrder(data) {
  return request({
    url: '/order/cancel',
    method: 'post',
    data
  })
}
export function settleCash(data) {
  return request({
    url: '/withdraw/settle',
    method: 'get',
    params: data
  })
}
export function getNotice(data) {
  return request({
    url: '/notice/get',
    method: 'get',
    params: data
  })
}
export function addNotice(data) {
  return request({
    url: '/notice/add',
    method: 'post',
    data
  })
}
export function editNotice(data) {
  return request({
    url: '/notice/edit',
    method: 'post',
    data
  })
}
export function delNotice(data) {
  return request({
    url: '/notice/remove',
    method: 'post',
    data
  })
}
export function editSettings(data) {
  return request({
    url: '/config/edit',
    method: 'post',
    data
  })
}
export function getcommission(data) {
  return request({
    url: '/config/get_commissions',
    method: 'get',
    params: data
  })
}
export function getBetLimit(data) {
  return request({
    url: '/config/get_limits',
    method: 'get',
    params: data
  })
}
export function getPick(data) {
  return request({
    url: '/config/get_scraps',
    method: 'get',
    params: data
  })
}
export function getOtherSetting(data) {
  return request({
    url: '/config/get_other_setting',
    method: 'get',
    params: data
  })
}
export function getLatestOrders(data) {
  return request({
    url: '/order/latest_list',
    method: 'get',
    params: data
  })
}

