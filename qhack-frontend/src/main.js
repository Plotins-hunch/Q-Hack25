import {createApp} from 'vue'
import App from './App.vue'
import {createMemoryHistory, createRouter} from 'vue-router'
import SearchPage from './components/SearchPage.vue'
import DashboardPage from './components/DashboardPage.vue'

const routes = [
    {
        path: '/',
        component: SearchPage,
    },
    {
        path: '/dashboard',
        component: DashboardPage,
    },
]

const router = createRouter({
    history: createMemoryHistory(),
    routes,
})

createApp(App).use(router).mount('#app')
