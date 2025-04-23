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

        <!-- PDF Uploader -->
        <div
            class="pdf-upload-container"
            @dragover.prevent="onDragOver"
            @dragleave.prevent="onDragLeave"
            @drop.prevent="onDrop"
            :class="{'drag-over': isDragging}"
        >
            <div v-if="!pdfFile" class="upload-placeholder">
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="40"
                    height="40"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    class="upload-icon"
                >
                    <path
                        d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
                    ></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <path d="M12 18v-6"></path>
                    <path d="M9 15h6"></path>
                </svg>
                <p class="upload-text">Drag & Drop PDF file here</p>
                <p class="upload-subtext">or</p>
                <label for="pdf-upload" class="custom-file-input">
                    Browse Files
                    <input
                        type="file"
                        id="pdf-upload"
                        accept="application/pdf"
                        @change="handleFileUpload"
                        hidden
                    />
                </label>
            </div>

            <!-- PDF Preview -->
            <div v-else class="pdf-preview">
                <div class="pdf-preview-header">
                    <div class="pdf-info">
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            width="24"
                            height="24"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.5"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            class="pdf-icon"
                        >
                            <path
                                d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
                            ></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                        </svg>
                        <div class="pdf-details">
                            <span class="pdf-name">{{ pdfFile.name }}</span>
                            <span class="pdf-size">{{
                                formatFileSize(pdfFile.size)
                            }}</span>
                        </div>
                    </div>
                    <button class="remove-pdf" @click="removePdf">
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
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                </div>
                <div class="pdf-thumbnail">
                    <div class="thumbnail-overlay">
                        <span>PDF</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import {ref} from 'vue'
import '../css/search-page.css'
import {useRouter} from 'vue-router'

const router = useRouter()
const searchQuery = ref('')
const isDragging = ref(false)
const pdfFile = ref(null)

const searchCompanies = () => {
    // access the company name by searchQuery
    router.push('/dashboard')
}

const onDragOver = () => {
    isDragging.value = true
}

const onDragLeave = () => {
    isDragging.value = false
}

const onDrop = (e) => {
    isDragging.value = false
    const files = e.dataTransfer.files

    if (files.length > 0 && files[0].type === 'application/pdf') {
        pdfFile.value = files[0]
    }
}

const handleFileUpload = (e) => {
    const files = e.target.files

    if (files.length > 0 && files[0].type === 'application/pdf') {
        pdfFile.value = files[0]
    }
}

const removePdf = () => {
    pdfFile.value = null
}

const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' bytes'
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
    else return (bytes / 1048576).toFixed(1) + ' MB'
}
</script>
