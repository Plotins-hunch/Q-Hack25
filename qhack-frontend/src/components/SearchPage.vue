<!-- TODO: add field where the user can upload a pdf file for the scraper to go through -->

<template>
    <div class="search-container">
        <h1 class="headline">What company do you want to invest in?</h1>
        <div class="search-box">
            <input
                type="text"
                class="search-input"
                placeholder="Search for potential unicorns..."
                v-model="searchQuery"
                @keyup.enter="searchCompanies"
            />
            <button class="search-button" @click="searchCompanies">
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                >
                    <circle cx="11" cy="11" r="8"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
            </button>
        </div>
    </div>
</template>

<script setup>
import {ref} from 'vue'
import '../css/search-page.css'
import {useRouter} from 'vue-router'

const router = useRouter()
const searchQuery = ref('')
const searchCompanies = () => {
    // access the company name by searchQuery
    router.push('/dashboard')
}
</script>
