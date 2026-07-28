import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/style.css'
import { installDomTranslator } from './i18n-dom'

createApp(App).use(router).mount('#app')
installDomTranslator(router)
