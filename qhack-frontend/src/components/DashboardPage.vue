<template>
    <div class="unicorn-dashboard">
        <div class="navigation">
            <NavButton @nav-click="handleNavClick" />
        </div>

        <div class="dashboard-container">
            <!-- Top Row - Overall Score Card -->
            <div class="score-card">
                <div class="score-circle">
                    <div class="score-value">86</div>
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
                <!-- Team Card -->
                <div class="metric-card">
                    <div class="metric-header">
                        <h3>Team</h3>
                        <div class="metric-score">82</div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 82%"></div>
                    </div>
                    <div class="metric-details">
                        <div class="metric-item">
                            <span>Founder Experience</span>
                            <strong>Strong</strong>
                        </div>
                        <div class="metric-item">
                            <span>Tech Expertise</span>
                            <strong>High</strong>
                        </div>
                        <div class="metric-item">
                            <span>Retention</span>
                            <strong>95%</strong>
                        </div>
                    </div>
                </div>

                <!-- Market Card -->
                <div class="metric-card">
                    <div class="metric-header">
                        <h3>Market</h3>
                        <div class="metric-score">94</div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 94%"></div>
                    </div>
                    <div class="metric-details">
                        <div class="metric-item">
                            <span>TAM Size</span>
                            <strong>$7.2B</strong>
                        </div>
                        <div class="metric-item">
                            <span>Growth Rate</span>
                            <strong>23% YoY</strong>
                        </div>
                        <div class="metric-item">
                            <span>Competition</span>
                            <strong>Medium</strong>
                        </div>
                    </div>
                </div>

                <!-- Product Card -->
                <div class="metric-card">
                    <div class="metric-header">
                        <h3>Product</h3>
                        <div class="metric-score">76</div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 76%"></div>
                    </div>
                    <div class="metric-details">
                        <div class="metric-item">
                            <span>Innovation</span>
                            <strong>High</strong>
                        </div>
                        <div class="metric-item">
                            <span>Product-Market Fit</span>
                            <strong>Good</strong>
                        </div>
                        <div class="metric-item">
                            <span>User Feedback</span>
                            <strong>4.7/5</strong>
                        </div>
                    </div>
                </div>

                <!-- Traction Card -->
                <div class="metric-card">
                    <div class="metric-header">
                        <h3>Traction</h3>
                        <div class="metric-score">89</div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 89%"></div>
                    </div>
                    <div class="metric-details">
                        <div class="metric-item">
                            <span>MRR</span>
                            <strong>$320K</strong>
                        </div>
                        <div class="metric-item">
                            <span>Growth</span>
                            <strong>16% MoM</strong>
                        </div>
                        <div class="metric-item">
                            <span>Active Users</span>
                            <strong>48K</strong>
                        </div>
                    </div>
                </div>

                <!-- Funding Card -->
                <div class="metric-card">
                    <div class="metric-header">
                        <h3>Funding</h3>
                        <div class="metric-score">80</div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 80%"></div>
                    </div>
                    <div class="metric-details">
                        <div class="metric-item">
                            <span>Total Raised</span>
                            <strong>$12.5M</strong>
                        </div>
                        <div class="metric-item">
                            <span>Last Round</span>
                            <strong>Series A</strong>
                        </div>
                        <div class="metric-item">
                            <span>Investor Quality</span>
                            <strong>Top-tier</strong>
                        </div>
                    </div>
                </div>

                <!-- Financial Efficiency Card -->
                <div class="metric-card">
                    <div class="metric-header">
                        <h3>Financial Efficiency</h3>
                        <div class="metric-score">85</div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 85%"></div>
                    </div>
                    <div class="metric-details">
                        <div class="metric-item">
                            <span>Burn Rate</span>
                            <strong>$190K/mo</strong>
                        </div>
                        <div class="metric-item">
                            <span>CAC</span>
                            <strong>$380</strong>
                        </div>
                        <div class="metric-item">
                            <span>LTV/CAC</span>
                            <strong>4.2</strong>
                        </div>
                    </div>
                </div>

                <!-- Miscellaneous Card -->
                <div class="metric-card">
                    <div class="metric-header">
                        <h3>Miscellaneous</h3>
                        <div class="metric-score">78</div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 78%"></div>
                    </div>
                    <div class="metric-details">
                        <div class="metric-item">
                            <span>Legal Status</span>
                            <strong>Good</strong>
                        </div>
                        <div class="metric-item">
                            <span>IP Portfolio</span>
                            <strong>3 Patents</strong>
                        </div>
                        <div class="metric-item">
                            <span>Location</span>
                            <strong>Boston</strong>
                        </div>
                    </div>
                </div>

                <!-- Growth Projection Card -->
                <div class="metric-card">
                    <div class="metric-header">
                        <h3>Growth Projection</h3>
                    </div>
                    <div class="growth-chart">
                        <span class="chart-line"></span>
                        <div class="chart-label">Unicorn in ~18 months</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import '../css/dashboard-page.css'
import NavButton from './NavButton.vue'
import {useRouter} from 'vue-router'

const router = useRouter()
const handleNavClick = () => {
    router.push('/')
}

// Ensure proper scrolling when component mounts
import {onMounted} from 'vue'
onMounted(() => {
    // Reset any overflow restrictions that might be present
    document.body.style.overflow = 'auto'
    document.documentElement.style.overflow = 'auto'

    // Scroll to top when dashboard loads
    window.scrollTo(0, 0)
})
</script>
