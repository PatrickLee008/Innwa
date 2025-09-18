export function dateToString(dateTime) {
  const date = new Date(dateTime) // 时间戳为10位需*1000，时间戳为13位的话不需乘1000
  const Y = date.getFullYear() + '-'
  const M =
        (date.getMonth() + 1 < 10
          ? '0' + (date.getMonth() + 1)
          : date.getMonth() + 1) + '-'
  const D =
        date.getDate() < 10 ? '0' + date.getDate() + ' ' : date.getDate() + ' '
  const H = date.getHours() < 10 ? '0' + date.getHours() : date.getHours()
  const MI =
        date.getMinutes() < 10 ? '0' + date.getMinutes() : date.getMinutes()
  const S =
        date.getSeconds() < 10 ? '0' + date.getSeconds() : date.getSeconds()

  return Y + M + D +H + ':' + MI + ':' + S
}

export function dateToString2(dateTime) {
      const date = new Date(dateTime) // 时间戳为10位需*1000，时间戳为13位的话不需乘1000
      const Y = date.getFullYear() + '-'
      const M =
            (date.getMonth() + 1 < 10
              ? '0' + (date.getMonth() + 1)
              : date.getMonth() + 1) + '-'
      const D =
            date.getDate() < 10 ? '0' + date.getDate() + ' ' : date.getDate() + ' '    
      return Y + M + D
}

export function stringToDate(dateString) {
  var val = Date.parse(dateString)
  var newDate = new Date(val)
  return newDate
}

