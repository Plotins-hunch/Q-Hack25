<template>
    <nav class="navigation">
        <button class="nav-button" @click="handleNavClick">
            <svg
                class="arrow-icon"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
            >
                <path
                    d="M19 12H5M12 19l-7-7 7-7"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                />
            </svg>
        </button>
    </nav>
</template>

<script setup>
import {defineEmits} from 'vue'
import '../css/nav-button.css'

const emit = defineEmits(['nav-click'])

const handleNavClick = () => {
    emit('nav-click')
}
</script>
