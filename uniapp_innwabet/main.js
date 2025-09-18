import Vue from 'vue'
import App from './App'

import common from 'utils/common.js'
Vue.prototype.$noMultipleClicks = common.noMultipleClicks;

import basics from './pages/basics/home.vue'
Vue.component('basics',basics)

import components from './pages/component/home.vue'
Vue.component('components',components)

import plugin from './pages/plugin/home.vue'
Vue.component('plugin',plugin)

import toolbox from './utils/toolbox.js';
Vue.prototype.$toolbox = toolbox;

import my from './utils/my.js'
var http = my.http;
var getUserInfo = my.getUserInfo;
var getConfigs = my.getConfigs;

Vue.prototype.$http =http;

import store from './store/index.js';
Vue.prototype.$store =store;

import music from './utils/sounds.js'
Vue.prototype.music = music;

import cuCustom from './colorui/components/cu-custom.vue'
Vue.component('cu-custom',cuCustom)

Vue.config.productionTip = false

App.mpType = 'app'

const app = new Vue({
    ...App
})
app.$mount()



 



