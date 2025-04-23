<template>
    <div class="navigation">
        <NavButton @nav-click="handleNavClick" />
    </div>

    <div class="dashboard-container">
        <h1>Dashboard for the selected company</h1>
    </div>
</template>

<script setup>
//import {ref} from 'vue'
import '../css/search-page.css'
import NavButton from './NavButton.vue'
import {useRouter} from 'vue-router'

const router = useRouter()
const handleNavClick = () => {
    router.push('/')
}
</script>
