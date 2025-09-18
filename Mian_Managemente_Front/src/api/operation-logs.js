import request from '@/utils/request'

export function getOperationLogs(data) {
  return request({
    url: '/operation/get',
    method: 'get',
    params: data
  })
}

export function getLoginLogs(data) {
  return request({
    url: '/login_record/get',
    method: 'get',
    params: data
  })
}

