<template>
    <div class="unicorn-dashboard">
        <div class="navigation">
            <NavButton @nav-click="handleNavClick" />
        </div>

        <div class="dashboard-container">
            <h1 class="headline2">
                Analysis of {{ business_data.company_name }}
            </h1>

            <!-- Overall Score Card - Simplified with Pie Chart -->
            <div class="score-card">
                <div class="pie-chart-large">
                    <div
                        class="pie-slice"
                        :style="
                            pieChartStyle(business_data.metrics.UnicornScore)
                        "
                    ></div>
                    <div class="pie-center">
                        <div class="score-value">
                            {{ business_data.metrics.UnicornScore }}
                        </div>
                    </div>
                </div>
                <div class="score-info">
                    <h2>Overall Unicorn Score</h2>
                </div>
            </div>

            <!-- Metrics Grid with Mixed Visualizations -->
            <div class="metrics-grid">
                <div
                    v-for="(data, category) in metricData"
                    :key="category"
                    class="metric-card"
                    @click="openDetailModal(category)"
                >
                    <div class="metric-header">
                        <h3>{{ formatTitle(category) }}</h3>
                        <div class="metric-score">{{ data.score }}</div>
                    </div>

                    <!-- Pie Chart for Team, Market, and Product -->
                    <div
                        v-if="['team', 'market', 'product'].includes(category)"
                        class="pie-chart-container"
                    >
                        <div class="pie-chart">
                            <div
                                class="pie-slice"
                                :style="pieChartStyle(data.score)"
                            ></div>
                            <div class="pie-center"></div>
                        </div>
                    </div>

                    <!-- Progress Bar for Traction, Funding, Financial Efficiency, and Miscellaneous -->
                    <div v-else class="progress-bar-container">
                        <div class="progress-bar">
                            <div
                                class="progress-fill"
                                :style="{width: data.score + '%'}"
                            ></div>
                        </div>
                    </div>

                    <!-- Click indicator -->
                    <div class="click-indicator">
                        <span>Click for details</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Modal with Table-Based Layout -->
        <div v-if="showModal" class="modal-overlay" @click="closeModal">
            <div class="modal-container" @click.stop>
                <div class="modal-header">
                    <h2>{{ formatTitle(selectedCategory) }} Details</h2>
                    <button class="close-button" @click="closeModal">×</button>
                </div>
                <div class="modal-content">
                    <div class="modal-score">
                        <div class="modal-score-label">Score</div>
                        <div
                            v-if="
                                ['team', 'market', 'product'].includes(
                                    selectedCategory,
                                )
                            "
                            class="modal-pie-chart"
                        >
                            <div
                                class="pie-slice"
                                :style="
                                    pieChartStyle(getSelectedCategoryScore())
                                "
                            ></div>
                            <div class="pie-center">
                                <div class="modal-score-value">
                                    {{ getSelectedCategoryScore() }}
                                </div>
                            </div>
                        </div>
                        <div v-else class="modal-progress-container">
                            <div class="modal-score-value">
                                {{ getSelectedCategoryScore() }}
                            </div>
                            <div class="modal-progress-bar">
                                <div
                                    class="progress-fill"
                                    :style="{
                                        width: getSelectedCategoryScore() + '%',
                                    }"
                                ></div>
                            </div>
                        </div>
                    </div>

                    <!-- Simple Key-Value Pairs -->
                    <table v-if="hasSimpleData" class="detail-table">
                        <tbody>
                            <tr
                                v-for="(value, key) in getSimpleDetails()"
                                :key="key"
                            >
                                <th>{{ formatTitle(key) }}</th>
                                <td>{{ value }}</td>
                            </tr>
                        </tbody>
                    </table>

                    <!-- Nested Objects -->
                    <div
                        v-for="(value, key) in getComplexDetails()"
                        :key="key"
                        class="detail-section"
                    >
                        <h3 class="detail-section-title">
                            {{ formatTitle(key) }}
                        </h3>

                        <!-- Object with key-value pairs -->
                        <table
                            v-if="isObject(value) && !Array.isArray(value)"
                            class="detail-table"
                        >
                            <tbody>
                                <tr
                                    v-for="(nestedVal, nestedKey) in value"
                                    :key="nestedKey"
                                >
                                    <th>{{ formatTitle(nestedKey) }}</th>
                                    <td>{{ nestedVal }}</td>
                                </tr>
                            </tbody>
                        </table>

                        <!-- Array of objects -->
                        <div
                            v-else-if="Array.isArray(value) && value.length > 0"
                        >
                            <table
                                v-if="isObjectArray(value)"
                                class="detail-table array-table"
                            >
                                <thead>
                                    <tr>
                                        <th
                                            v-for="header in getObjectArrayHeaders(
                                                value,
                                            )"
                                            :key="header"
                                        >
                                            {{ formatTitle(header) }}
                                        </th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr
                                        v-for="(item, index) in value"
                                        :key="index"
                                    >
                                        <td
                                            v-for="header in getObjectArrayHeaders(
                                                value,
                                            )"
                                            :key="header"
                                        >
                                            {{ item[header] }}
                                        </td>
                                    </tr>
                                </tbody>
                            </table>

                            <!-- Array of simple values -->
                            <table v-else class="detail-table">
                                <tbody>
                                    <tr
                                        v-for="(item, index) in value"
                                        :key="index"
                                    >
                                        <th>#{{ index + 1 }}</th>
                                        <td>{{ item }}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <!-- Empty array -->
                        <p
                            v-else-if="
                                Array.isArray(value) && value.length === 0
                            "
                            class="empty-message"
                        >
                            No data available
                        </p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Pass business_data properly to ChatGPT component -->
        <ChatGptComponent :businessData="business_data" />
    </div>
</template>

<script setup>
import '../css/dashboard-page.css'
import NavButton from './NavButton.vue'
import ChatGptComponent from './ChatGptComponent.vue'
import {useRouter} from 'vue-router'
import {computed, onMounted, ref} from 'vue'

// Get business data from localStorage, ensuring it's a proper object
let business_data = {}
try {
    const storedData = window.localStorage.getItem('business_data')
    if (storedData) {
        business_data = JSON.parse(storedData)
        console.log('Loaded business data:', business_data)
    } else {
        console.warn('No business data found in localStorage')
        business_data = {
            company_name: 'Sample Company',
            metrics: {
                UnicornScore: 75,
                Team: 80,
                Market: 70,
                Product: 85,
                Traction: 65,
                Funding: 60,
                FinancialEfficiency: 75,
                Miscellaneous: 70,
            },
        }
    }
} catch (error) {
    console.error('Error parsing business data from localStorage:', error)
}

const router = useRouter()
const showModal = ref(false)
const selectedCategory = ref(null)

const handleNavClick = () => {
    router.push('/')
}

// Format category names for display
const formatTitle = (str) => {
    return str
        .replace(/_/g, ' ')
        .split(' ')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')
}

// Generate pie chart style based on score
const pieChartStyle = (score) => {
    // Convert score to a percentage (assuming score is already 0-100)
    const percentage = Math.min(Math.max(score, 0), 100)

    // Calculate the background conic gradient degrees
    // If percentage is 100, we need a full 360deg gradient
    // Otherwise, we calculate the degrees based on percentage
    const degrees = percentage * 3.6 // 3.6 = 360/100

    if (percentage >= 100) {
        return {
            background: 'conic-gradient(#a47bf6 0deg, #a47bf6 360deg)',
        }
    } else if (percentage <= 0) {
        return {
            background:
                'conic-gradient(rgba(255, 255, 255, 0.1) 0deg, rgba(255, 255, 255, 0.1) 360deg)',
        }
    } else {
        return {
            background: `conic-gradient(#a47bf6 0deg, #a47bf6 ${degrees}deg, rgba(255, 255, 255, 0.1) ${degrees}deg, rgba(255, 255, 255, 0.1) 360deg)`,
        }
    }
}

// Simplified metric data - only includes category and score
const metricData = computed(() => {
    return {
        team: {
            score: business_data.metrics?.Team || 0,
        },
        market: {
            score: business_data.metrics?.Market || 0,
        },
        product: {
            score: business_data.metrics?.Product || 0,
        },
        traction: {
            score: business_data.metrics?.Traction || 0,
        },
        funding: {
            score: business_data.metrics?.Funding || 0,
        },
        financial_efficiency: {
            score: business_data.metrics?.FinancialEfficiency || 0,
        },
        miscellaneous: {
            score: business_data.metrics?.Miscellaneous || 0,
        },
    }
})

// Open modal with selected category details
const openDetailModal = (category) => {
    selectedCategory.value = category
    showModal.value = true
    // Disable background scrolling when modal is open
    document.body.style.overflow = 'hidden'
}

// Close modal
const closeModal = () => {
    showModal.value = false
    // Re-enable background scrolling
    document.body.style.overflow = 'auto'
}

// Get the score for the selected category
const getSelectedCategoryScore = () => {
    if (!selectedCategory.value) return 0
    return metricData.value[selectedCategory.value].score
}

// Check if value is an object
const isObject = (value) => {
    return typeof value === 'object' && value !== null
}

// Check if array contains objects
const isObjectArray = (arr) => {
    return (
        Array.isArray(arr) &&
        arr.length > 0 &&
        typeof arr[0] === 'object' &&
        arr[0] !== null
    )
}

// Get headers for an array of objects
const getObjectArrayHeaders = (arr) => {
    if (!isObjectArray(arr)) return []
    return Object.keys(arr[0])
}

// Get simple key-value pairs from category details (not objects or arrays)
const getSimpleDetails = () => {
    if (!selectedCategory.value) return {}

    const data = business_data[selectedCategory.value]
    if (!data) return {}

    const simpleData = {}

    for (const [key, value] of Object.entries(data)) {
        if (
            (typeof value !== 'object' || value === null) &&
            key !== 'id' &&
            key !== '_id'
        ) {
            simpleData[key] = value
        }
    }

    return simpleData
}

// Check if there are any simple key-value pairs
const hasSimpleData = computed(() => {
    return Object.keys(getSimpleDetails()).length > 0
})

// Get complex data (objects and arrays)
const getComplexDetails = () => {
    if (!selectedCategory.value) return {}

    const data = business_data[selectedCategory.value]
    if (!data) return {}

    const complexData = {}

    for (const [key, value] of Object.entries(data)) {
        if (
            typeof value === 'object' &&
            value !== null &&
            key !== 'id' &&
            key !== '_id'
        ) {
            complexData[key] = value
        }
    }

    return complexData
}

// Get all category details
const getCategoryDetails = () => {
    if (!selectedCategory.value) return {}
    return business_data[selectedCategory.value]
}

// Ensure proper scrolling when component mounts
onMounted(() => {
    // Reset any overflow restrictions that might be present
    document.body.style.overflow = 'auto'
    document.documentElement.style.overflow = 'auto'

    // Scroll to top when dashboard loads
    window.scrollTo(0, 0)
})
</script>
