import Vue from 'vue'

import Cookies from 'js-cookie'

import 'normalize.css/normalize.css' // a modern alternative to CSS resets
import Element from 'element-ui'
import './styles/element-variables.scss'

import '@/styles/index.scss' // global css

import './assets/icon/iconfont.css'
import App from './App'
import store from './store'
import router from './router'

import './icons' // icon
import './permission' // permission control
import './utils/error-log' // error log

import * as filters from './filters' // global filters


import mavonEditor from 'mavon-editor'
import 'mavon-editor/dist/css/index.css'

Vue.use(mavonEditor)

import {toolbox} from './utils/toolbox';
Vue.prototype.$toolbox =toolbox;

import {to_myan_time,to_server_time,getCurrentDateWithTime} from "./utils";
Vue.prototype.$to_myan_time = to_myan_time;
Vue.prototype.$to_server_time = to_server_time;
Vue.prototype.$get_date_with_time = getCurrentDateWithTime;
/**
 * If you don't want to use mock-server
 * you want to use MockJs for mock api
 * you can execute: mockXHR()
 *
 * Currently MockJs will be used in the production environment,
 * please remove it before going online! ! !
 */

//import { mockXHR } from '../mock'
//if (process.env.NODE_ENV === 'production') {
  //mockXHR()
//}

Vue.use(Element, {
  size: Cookies.get('size') || 'medium' // set element-ui default size
})

// register global utility filters
Object.keys(filters).forEach(key => {
  Vue.filter(key, filters[key])
})

Vue.config.productionTip = false

new Vue({
  el: '#app',
  router,
  store,
  render: h => h(App)
})
