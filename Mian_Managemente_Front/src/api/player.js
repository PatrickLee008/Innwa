import request from '@/utils/request'

export function getRechargeList(data) {
  return request({
    url: '/charge/get',
    method: 'get',
    params: data
  })
}
export function addRecharge(data) {
  return request({
    url: '/charge/add',
    method: 'post',
    data
  })
}

export function getPlayer(data) {
  return request({
    url: '/charge/user_info',
    method: 'get',
    params: data
  })
}

export function getPlayerList(data) {
  return request({
    url: '/app_user/get',
    method: 'get',
    params: data
  })
}
export function getUnAgentPlayerList(data) {
  return request({
    url: '/app_user/get_unset_agent_users',
    method: 'get',
    params: data
  })
}
export function delPlayer(data) {
  return request({
    url: '/app_user/remove',
    method: 'get',
    params: data
  })
}
export function addPlayer(data) {
  return request({
    url: '/app_user/add',
    method: 'post',
    headers: {
      'Content-Type': 'application/json'
    },
    data

  })
}
export function editPlayer(data) {
  return request({
    url: '/app_user/edit',
    method: 'post',
    headers: {
      'Content-Type': 'application/json'
    },
    data
  })
}
export function getAdmin() {
  return request({
    url: '/admin/get',
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  })
}
export function addAdmin(data) {
  return request({
    url: '/admin/add',
    method: 'post',
    headers: {
      'Content-Type': 'application/json'
    },
    data
  })
}
export function editAdmin(data) {
  return request({
    url: '/admin/edit',
    method: 'post',
    headers: {
      'Content-Type': 'application/json'
    },
    data
  })
}
export function delAdmin(data) {
  return request({
    url: '/admin/remove',
    method: 'post',
    headers: {
      'Content-Type': 'application/json'
    },
    data
  })
}
