import request from '@/utils/request'

export function getCashList(data) {
  return request({
    url: '/withdraw/get',
    method: 'get',
    params: data
  })
}

export function getSettlementList(data) {
  return request({
    url: '/settlement/get',
    method: 'get',
    params: data
  })
}

export function settleCash(data) {
  return request({
    url: '/withdraw/app_user_deal',
    method: 'post',
    data
  })
}
export function settleAgentCash(data) {
  return request({
    url: '/withdraw/agent_deal',
    method: 'post',
    data
  })
}

export function addWithdraw(data) {
  return request({
    url: '/withdraw/agent_withdraw',
    method: 'post',
    data
  })
}
export function getLatestWithDrawList(data) {
  return request({
    url: '/withdraw/latest_list',
    method: 'get',
    params: data
  })
}

export function removeAgentWithdrawApi(data) {
  return request({
    url: '/withdraw/remove',
    method: 'post',
    data
  })
}

export function getLatestChargeList(data) {
  return request({
    url: '/charge/latest_list',
    method: 'get',
    params: data
  })
}


export function getGroupApi(data) {
  return request({
    url: '/withdraw_group/get',
    method: 'get',
    params: data
  })
}

export function addGroupApi(data) {
  return request({
    url: '/withdraw_group/add',
    method: 'post',
    data
  })
}

export function editGroupApi(data) {
  return request({
    url: '/withdraw_group/edit',
    method: 'post',
    data
  })
}

export function removeGroupApi(data) {
  return request({
    url: '/withdraw_group/remove',
    method: 'post',
    data
  })
}



export function getBankcardApi(data) {
  return request({
    url: '/sys_bankcard',
    method: 'get',
    params: data
  })
}

export function addBankcardApi(data) {
  return request({
    url: '/sys_bankcard',
    method: 'post',
    data
  })
}

export function editBankcardApi(data) {
  return request({
    url: '/sys_bankcard/' + data.ID,
    method: 'put',
    data
  })
}

export function removeBankcardApi(data) {
  return request({
    url: '/sys_bankcard/' + data.ID,
    method: 'delete',
    data
  })
}


export function activeBankcardApi(data) {
  return request({
    url: '/sys_bankcard/' + data.ID + '/active',
    method: 'put',
    data
  })
}

export function ankcardVisibleApi(data) {
  return request({
    url: '/sys_bankcard/' + data.ID + '/visible',
    method: 'put',
    data
  })
}


export function getRechargeCallBack(data) {
  return request({
    url: '/charge_callback/get',
    method: 'get',
    params: data
  })
}


export function editRechargeCallBack(data) {
  return request({
    url: '/charge_callback/edit',
    method: 'put',
    data
  })
}

export function getDailyReport(data) {
  return request({
    url: '/sys_bankcard/' + data.id + '/daily_reports',
    method: 'get',
    params: data
  })
}

export function bankCardCashOut(id, data) {
  return request({
    url: '/sys_bankcard/' + id + '/reduce_income',
    method: 'put',
    data
  })
}

