import request from '@/utils/request'

export function getAuthMenu(data) {
  return request({
    url: '/menu/get',
    method: 'get',
    params: data
  })
}

export function getMenuList(data) {
  return request({
    url: '/menu/get_list',
    method: 'get',
    params: data
  })
}

