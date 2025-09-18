import request from '@/utils/request'

export function getRoles() {
  return request({
    url: '/role/get',
    method: 'get'
  })
}

export function addRole(data) {
  return request({
    url: '/role/add',
    method: 'post',
    data
  })
}

export function updateRole(data) {
  return request({
    url: '/role/edit',
    method: 'post',
    data
  })
}

export function deleteRole(data) {
  return request({
    url: '/role/remove',
    method: 'post',
    data
  })
}

