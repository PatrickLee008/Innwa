import request from '@/utils/request'

export function getUpdateConfigApI(data) {
  return request({
    url: '/config/get_update',
    method: 'get',
    params: data
  })
}


export function refreshHistoryOrder(data) {
  return request({
    url: '/order/refresh_sphinx_order',
    method: 'post',
    data
  })
}
