<template>
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
                            :style="pieChartStyle(getSelectedCategoryScore())"
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
                    <h3 class="detail-section-title">{{ formatTitle(key) }}</h3>

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
                    <div v-else-if="Array.isArray(value) && value.length > 0">
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
                                <tr v-for="(item, index) in value" :key="index">
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
                                <tr v-for="(item, index) in value" :key="index">
                                    <th>#{{ index + 1 }}</th>
                                    <td>{{ item }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <!-- Empty array -->
                    <p
                        v-else-if="Array.isArray(value) && value.length === 0"
                        class="empty-message"
                    >
                        No data available
                    </p>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
// These are the setup methods that would be added to your existing script section
// You would need to add these methods to your dashboard component

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
</script>
