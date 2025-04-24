<template>
    <div class="search-container">
        <h1 class="headline">What company do you want to invest in?</h1>

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
                    <div class="action-buttons">
                        <button
                            class="upload-button"
                            @click="uploadPdf"
                            :disabled="isUploading"
                        >
                            <div
                                v-if="isUploading"
                                class="loading-spinner"
                            ></div>
                            <span v-else>Upload</span>
                        </button>
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
                </div>
                <div class="pdf-thumbnail">
                    <div class="thumbnail-overlay">
                        <span>PDF</span>
                    </div>
                </div>

                <!-- Upload Status -->
                <div v-if="uploadStatus" class="status-container">
                    <div class="status-icon" :class="uploadStatus.type">
                        <svg
                            v-if="uploadStatus.type === 'success'"
                            xmlns="http://www.w3.org/2000/svg"
                            width="18"
                            height="18"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="2"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        >
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                            <polyline points="22 4 12 14.01 9 11.01"></polyline>
                        </svg>
                        <svg
                            v-else
                            xmlns="http://www.w3.org/2000/svg"
                            width="18"
                            height="18"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="2"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                        >
                            <circle cx="12" cy="12" r="10"></circle>
                            <line x1="12" y1="8" x2="12" y2="12"></line>
                            <line x1="12" y1="16" x2="12.01" y2="16"></line>
                        </svg>
                    </div>
                    <span class="status-message" :class="uploadStatus.type">{{
                        uploadStatus.message
                    }}</span>
                </div>

                <!-- Analysis Status -->
                <div v-if="analysisStatus" class="analysis-container">
                    <div class="analysis-header">
                        <div class="analysis-title">
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="18"
                                height="18"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                class="analysis-icon"
                            >
                                <path
                                    d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"
                                ></path>
                                <polyline
                                    points="3.27 6.96 12 12.01 20.73 6.96"
                                ></polyline>
                                <line x1="12" y1="22.08" x2="12" y2="12"></line>
                            </svg>
                            <span>Analysis Status</span>
                        </div>
                        <div
                            class="analysis-badge"
                            :class="analysisStatus.type"
                        >
                            {{ analysisStatus.status }}
                        </div>
                    </div>
                    <p class="analysis-message">{{ analysisStatus.message }}</p>

                    <!-- View Analysis Button -->
                    <button
                        v-if="analysisStatus.type === 'success' && analysisData"
                        class="upload-button view-analysis"
                        @click="viewAnalysis"
                    >
                        View Analysis
                    </button>
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
const isUploading = ref(false)
const uploadStatus = ref(null)
const analysisStatus = ref(null)
const analysisData = ref(null)
const analysisPollingInterval = ref(null)
window.localStorage.setItem('business_data', JSON.stringify({}))

// Base URL for the API - change as needed for your environment
const API_BASE_URL = 'http://localhost:8000'

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
        uploadStatus.value = null // Reset upload status when new file is selected
        analysisStatus.value = null // Reset analysis status
        analysisData.value = null // Reset analysis data

        // Clear any polling interval
        if (analysisPollingInterval.value) {
            clearInterval(analysisPollingInterval.value)
            analysisPollingInterval.value = null
        }
    }
}

const removePdf = () => {
    pdfFile.value = null
    uploadStatus.value = null
    analysisStatus.value = null
    analysisData.value = null

    // Clear any polling interval
    if (analysisPollingInterval.value) {
        clearInterval(analysisPollingInterval.value)
        analysisPollingInterval.value = null
    }
}

const uploadPdf = async () => {
    if (!pdfFile.value) return

    isUploading.value = true
    uploadStatus.value = null
    analysisStatus.value = null
    analysisData.value = null

    try {
        const formData = new FormData()
        formData.append('file', pdfFile.value)

        const response = await fetch(`${API_BASE_URL}/api/upload/pdf`, {
            method: 'POST',
            body: formData,
        })

        const result = await response.json()

        if (response.ok) {
            uploadStatus.value = {
                type: 'success',
                message: 'PDF uploaded successfully!',
            }
            console.log('Upload successful:', result)

            // Check if analysis is already available
            if (result.analysis) {
                window.localStorage.setItem(
                    'business_data',
                    JSON.stringify(result.analysis),
                )
                handleAnalysisComplete(result)
            } else if (result.file_path) {
                // Start tracking analysis progress
                startAnalysisTracking(result.file_path)
            }
        } else {
            uploadStatus.value = {
                type: 'error',
                message: `Upload failed: ${result.detail || 'Unknown error'}`,
            }
            console.error('Upload failed:', result)
        }
    } catch (error) {
        uploadStatus.value = {
            type: 'error',
            message: `Error: ${error.message}`,
        }
        console.error('Error uploading PDF:', error)
    } finally {
        isUploading.value = false
    }
}

const startAnalysisTracking = (filePath) => {
    // Set initial analysis status
    analysisStatus.value = {
        type: 'pending',
        status: 'Processing',
        message: 'Your PDF is being analyzed. This may take a few minutes...',
    }

    // Poll for analysis status every 5 seconds
    analysisPollingInterval.value = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/analyze-pdf`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({file_path: filePath}),
            })

            const result = await response.json()

            if (response.ok && result) {
                window.localStorage.setItem(
                    'business_data',
                    JSON.stringify(analysisData.value.analysis),
                )
                handleAnalysisComplete(result)
            }
        } catch (error) {
            console.error('Error checking analysis status:', error)
        }
    }, 5000)
}

const handleAnalysisComplete = (data) => {
    // Clear polling interval
    if (analysisPollingInterval.value) {
        clearInterval(analysisPollingInterval.value)
        analysisPollingInterval.value = null
    }

    // Update status
    analysisStatus.value = {
        type: 'success',
        status: 'Complete',
        message: 'PDF analysis completed successfully!',
    }

    // Store analysis data
    analysisData.value = data.analysis
    console.log('jjaajaj: ' + data.analysis)
}

const viewAnalysis = () => {
    // Store the analysis data in sessionStorage to access it on the dashboard
    if (analysisData.value) {
        sessionStorage.setItem(
            'pdfAnalysisData',
            JSON.stringify(analysisData.value),
        )
        router.push('/dashboard?source=pdf')
    }
}

const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' bytes'
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
    else return (bytes / 1048576).toFixed(1) + ' MB'
}
</script>

<style>
/* Updated styles for better consistency with the main theme */

/* Status Container */
.status-container {
    margin-top: 15px;
    display: flex;
    align-items: center;
    padding: 12px 15px;
    border-radius: 12px;
    background-color: rgba(36, 36, 40, 0.5);
    border: 1px solid var(--border-color);
}

.status-icon {
    margin-right: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.status-icon.success {
    color: var(--primary-color);
}

.status-icon.error {
    color: #ff6b6b;
}

.status-message {
    font-size: 14px;
    color: var(--text-color);
}

.status-message.success {
    color: var(--text-color);
}

.status-message.error {
    color: #ff6b6b;
}

/* Analysis Container */
.analysis-container {
    margin-top: 20px;
    padding: 15px;
    border-radius: 15px;
    background-color: rgba(36, 36, 40, 0.5);
    border: 1px solid var(--border-color);
}

.analysis-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
}

.analysis-title {
    display: flex;
    align-items: center;
    font-weight: 500;
    color: var(--text-color);
}

.analysis-icon {
    color: var(--primary-color);
    margin-right: 10px;
}

.analysis-badge {
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.3px;
}

.analysis-badge.pending {
    background-color: rgba(255, 193, 7, 0.15);
    color: #ffc107;
    border: 1px solid rgba(255, 193, 7, 0.2);
}

.analysis-badge.success {
    background-color: rgba(164, 123, 246, 0.15);
    color: var(--primary-color);
    border: 1px solid rgba(164, 123, 246, 0.2);
}

.analysis-badge.error {
    background-color: rgba(255, 107, 107, 0.15);
    color: #ff6b6b;
    border: 1px solid rgba(255, 107, 107, 0.2);
}

.analysis-message {
    font-size: 14px;
    margin-bottom: 15px;
    color: var(--placeholder-color);
    line-height: 1.4;
}

/* Action Buttons */
.action-buttons {
    display: flex;
    align-items: center;
    gap: 10px;
}

.upload-button {
    padding: 10px 20px;
    border-radius: 20px;
    background-color: var(--primary-color);
    color: white;
    font-size: 14px;
    font-weight: 500;
    border: none;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 36px;
}

.upload-button:hover:not(:disabled) {
    background-color: var(--primary-hover);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(164, 123, 246, 0.3);
}

.upload-button:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.view-analysis {
    width: 100%;
    max-width: 180px;
    margin: 0 auto;
}

/* Media query adjustments */
@media (max-width: 768px) {
    .upload-button {
        padding: 8px 16px;
        font-size: 13px;
    }

    .analysis-container {
        padding: 12px;
    }

    .analysis-badge {
        padding: 3px 8px;
        font-size: 11px;
    }
}
</style>
