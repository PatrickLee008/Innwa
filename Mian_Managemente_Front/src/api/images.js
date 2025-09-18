import request from '@/utils/request'

export function getImageList() {
    return request({
        url: '/up_image/get',
        method: 'get'
    })
}


export function addImage(data) {
  return request({
    url: '/up_image/add',
    method: 'post',
    data
  })
}


export function editImage(data) {
  return request({
    url: '/up_image/edit',
    method: 'post',
    data
  })
}


export function removeImage(data) {
  return request({
    url: '/up_image/remove',
    method: 'post',
    data
  })
}

