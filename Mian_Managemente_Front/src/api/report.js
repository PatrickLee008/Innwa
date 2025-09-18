import request from '@/utils/request'

export function getPlayerCount() {
  return request({
    url: '/report/user_count',
    method: 'get'
  })
}

export function getToTalReport(data) {
  return request({
    url: '/report/total_report',
    method: 'get',
    params: data
  })
}

export function getAgentChargeReport(data) {
  return request({
    url: '/charge/get_charge_report',
    method: 'get',
    params: data
  })
}

export function getUserBenefitReport(data) {
  return request({
    url: '/report/user_benefit_report',
    method: 'get',
    params: data
  })
}
