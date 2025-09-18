import http from './http'
//const AUTH_TOKEN = "Authorization";

http.setBaseUrl("https://api.innwabet.net");
// http.setBaseUrl("http://192.168.99.9:9190");
// http.setBaseUrl("http://8.218.24.233:8181");

http.beforeResponseFilter = function (res) {
    //X-Auth-Token
	/*
    if (res.header) {
        var respXAuthToken = res.header[AUTH_TOKEN.toLocaleLowerCase()];
        if (respXAuthToken) {
            uni.setStorageSync(AUTH_TOKEN, respXAuthToken);
            http.header[AUTH_TOKEN] = respXAuthToken;
        }
    }*/
	if (res.statusCode == 401) {
		uni.showToast({
			title: 'Timeout',
			image: '../../static/icon/error.png',
			duration: 2000
		})
		uni.removeStorageSync("Authorization");
		setTimeout(function() {
			uni.redirectTo({
				url: '../login/login'
			})
		}, 2000)

	} 
    return res;
}

 
let my = {
    'http': http
}

export default my
