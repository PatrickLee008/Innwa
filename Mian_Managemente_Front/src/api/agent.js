import request from '@/utils/request'

export function getAgentList(data) {
  return request({
    url: '/agent/get',
    method: 'get',
    params: data
  })
}
export function editAgent(data) {
  return request({
    url: '/agent/edit',
    method: 'post',
    data
  })
}
export function delAgent(data) {
  return request({
    url: '/agent/remove',
    method: 'post',
    data
  })
}
export function addAgent(data) {
  return request({
    url: '/agent/add',
    method: 'post',
    data
  })
}

export function getAgent(data) {
  return request({
    url: '/agent/get_one',
    method: 'get',
    params:data
  })
}

export function addAgentRecharge(data) {
  return request({
    url: '/charge/add_to_agent',
    method: 'post',
    data
  })
}


export function getAgentReportApi() {
  return request({
    url: '/agent/get_report',
    method: 'get'
  })
}
