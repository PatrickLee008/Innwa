import request from '@/utils/request'

export function getCoinLogs(data) {
  return request({
    url: '/app_operation/get',
    method: 'get',
    params: data
  })
}
