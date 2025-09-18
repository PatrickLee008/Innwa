import request from '@/utils/request'

export function getMatchList(data) {
  return request({
    url: '/match/get_match_list',
    method: 'get',
    params: data
  })
}
export function getMatchDetail(data) {
  return request({
    url: '/match/' + data.id,
    method: 'get',
    params: data
  })
}
export function getMatchHideWarning(data) {
  return request({
    url: '/match/get_match_hide_warning',
    method: 'get',
    params: data
  })
}
export function setMatchHideState(data) {
  return request({
    url: '/match/set_match_hide_state',
    method: 'post',
    data
  })
}
export function addMatch(data) {
  return request({
    url: '/match/add',
    method: 'post',
    data
  })
}
export function delMatch(data) {
  return request({
    url: '/match/remove',
    method: 'get',
    params: data
  })
}
export function editMatch(data) {
  return request({
    url: '/match/edit',
    method: 'post',
    data
  })
}
export function settlementMatch(data) {
  return request({
    url: '/match/settle',
    method: 'post',
    data
  })
}

export function addMatchByList(data) {
  return request({
    url: '/match/add_by_list',
    method: 'post',
    data
  })
}

export function cancelMatch(data) {
  return request({
    url: '/match/cancel',
    method: 'post',
    data
  })
}

export function getMatchSettleList(data) {
  return request({
    url: '/match_settle/get_match_settle_list',
    method: 'get',
    params: data
  })
}
export function reverseMatchSettle(data) {
  return request({
    url: '/match/reverse',
    method: 'post',
    data
  })
}
export function addMatchSettle(data) {
  return request({
    url: '/match_settle/add',
    method: 'post',
    data
  })
}
export function removeMatchSettle(data) {
  return request({
    url: '/match_settle/remove',
    method: 'get',
    params: data
  })
}
export function startMatchSettle(data) {
  return request({
    url: '/match_settle/start',
    method: 'post',
    data
  })
}
export function startAllMatchSettle(data) {
  return request({
    url: '/match_settle/start_all',
    method: 'post',
    data
  })
}
export function stopMatchSettle(data) {
  return request({
    url: '/match_settle/stop',
    method: 'post',
    data
  })
}
export function stopAllMatchSettle(data) {
  return request({
    url: '/match_settle/stop_all',
    method: 'post',
    data
  })
}

export function getSettleSwitch(data) {
  return request({
    url: '/match_settle/get_switch',
    method: 'get',
    params: data
  })
}
export function setSettleSwitch(data) {
  return request({
    url: '/match_settle/set_switch',
    method: 'post',
    data
  })
}
