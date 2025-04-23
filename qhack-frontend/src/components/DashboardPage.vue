<template>
    <div class="unicorn-dashboard">
        <div class="navigation">
            <NavButton @nav-click="handleNavClick" />
        </div>

        <div class="dashboard-container">
            <!-- Top Row - Overall Score Card -->
            <div class="score-card">
                <div class="score-circle">
                    <div class="score-value">
                        {{ business_data.overall_score }}
                    </div>
                </div>
                <div class="score-info">
                    <h2>Overall Unicorn Score</h2>
                    <div class="score-tags">
                        <span class="tag success">High Potential</span>
                        <span class="tag primary">Series B Ready</span>
                    </div>
                </div>
            </div>

            <!-- Metrics Grid -->
            <div class="metrics-grid">
                <!-- Dynamic Metric Cards -->
                <div
                    v-for="(data, category) in metricData"
                    :key="category"
                    class="metric-card"
                >
                    <div class="metric-header">
                        <h3>{{ formatTitle(category) }}</h3>
                        <div class="metric-score">{{ data.score }}</div>
                    </div>
                    <div class="progress-bar">
                        <div
                            class="progress-fill"
                            :style="{width: data.score + '%'}"
                        ></div>
                    </div>
                    <div class="metric-details">
                        <div
                            v-for="(value, key) in data.metrics"
                            :key="key"
                            class="metric-item"
                        >
                            <span>{{ formatTitle(key) }}</span>
                            <strong>{{ value }}</strong>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Add ChatGPT Component -->
        <ChatGptComponent :businessData="business_data" />
    </div>
</template>

<script setup>
import '../css/dashboard-page.css'
import NavButton from './NavButton.vue'
import ChatGptComponent from './ChatGptComponent.vue'
import {useRouter} from 'vue-router'
import {computed, onMounted} from 'vue'
import business_data from '../model/business_data.json'

const router = useRouter()
const handleNavClick = () => {
    router.push('/')
}

// Format category or key names for display
const formatTitle = (str) => {
    return str
        .replace(/_/g, ' ')
        .split(' ')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')
}

// Transform the JSON data into a format suitable for the v-for loop
const metricData = computed(() => {
    return {
        team: {
            score: business_data.team.team_score,
            metrics: {
                founder: business_data.team.founders[0].name,
                team_strength: business_data.team.team_strength + '/10',
                network_strength: business_data.team.network_strength + '/10',
            },
        },
        market: {
            score: business_data.market.market_score,
            metrics: {
                tam_size: business_data.market.TAM,
                growth_rate: business_data.market.growth_rate,
                som: business_data.market.SOM,
            },
        },
        product: {
            score: business_data.product.product_score,
            metrics: {
                stage: business_data.product.stage,
                usp: business_data.product.USP,
                customer_acquisition:
                    business_data.product.customer_acquisition,
            },
        },
        traction: {
            score: business_data.traction.customer_validation.NPS,
            metrics: {
                mrr: '$' + business_data.traction.revenue_growth.MRR + 'K',
                user_growth: business_data.traction.user_growth,
                engagement: business_data.traction.engagement,
            },
        },
        funding: {
            score: business_data.funding.cap_table_strength,
            metrics: {
                total_raised: business_data.funding.amount,
                stage: business_data.funding.stage,
                investor: business_data.funding.investors_on_board[0].name,
            },
        },
        financial_efficiency: {
            score: business_data.financial_efficiency.unit_economics * 20,
            metrics: {
                burn_rate: business_data.financial_efficiency.burn_rate,
                cac_ltv: business_data.financial_efficiency.CAC_vs_LTV,
                unit_economics:
                    business_data.financial_efficiency.unit_economics + '/5',
            },
        },
        miscellaneous: {
            score: 70, // Fixed score since there's no direct score in your JSON
            metrics: {
                regulatory_risk: business_data.miscellaneous.regulatory_risk,
                geographic_focus: business_data.miscellaneous.geographic_focus,
                timing_fad_risk: business_data.miscellaneous.timing_fad_risk,
            },
        },
    }
})

// Ensure proper scrolling when component mounts
onMounted(() => {
    // Reset any overflow restrictions that might be present
    document.body.style.overflow = 'auto'
    document.documentElement.style.overflow = 'auto'

    // Scroll to top when dashboard loads
    window.scrollTo(0, 0)
})
</script>
