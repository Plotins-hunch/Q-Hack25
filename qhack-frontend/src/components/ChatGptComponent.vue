<template>
    <div>
        <ChatGptButton v-if="!isChatOpen" @toggle-chat="toggleChat" />
        <ChatGptPanel
            :isOpen="isChatOpen"
            :businessData="businessData"
            @close="isChatOpen = false"
        />
    </div>
</template>

<script setup>
import {ref} from 'vue'
import ChatGptButton from './ChatGptButton.vue'
import ChatGptPanel from './ChatGptPanel.vue'

/**
const props = defineProps({
    businessData: {
        type: Object,
        default: () => ({}),
    },
})
    */

// Control chat panel visibility
const isChatOpen = ref(false)

// Toggle chat panel
const toggleChat = () => {
    isChatOpen.value = !isChatOpen.value
}
</script>
