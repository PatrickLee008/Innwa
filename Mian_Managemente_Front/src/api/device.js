import request from '@/utils/request'

export function getDeviceApi(data) {
  return request({
    url: '/device/get',
    method: 'get',
    params: data
  })
}

export function addDeviceApi(data) {
  return request({
    url: '/device/add',
    method: 'post',
    data
  })
}

export function editDeviceApi(data) {
  return request({
    url: '/device/edit',
    method: 'post',
    data
  })
}

export function removeDeviceApi(data) {
  return request({
    url: '/device/remove',
    method: 'get',
    params: data
  })
}

