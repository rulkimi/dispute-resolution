import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from '@/routers'

/* import the fontawesome core */
import { library } from '@fortawesome/fontawesome-svg-core'

/* import font awesome icon component */
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

/* import specific icons */
import { fas } from '@fortawesome/free-solid-svg-icons'
import { far } from '@fortawesome/free-regular-svg-icons'
import { fab } from '@fortawesome/free-brands-svg-icons'

library.add(fas)
library.add(far)
library.add(fab)

const app = createApp(App);

app.use(router)
app.component('font-awesome-icon', FontAwesomeIcon)
app.mount('#app');