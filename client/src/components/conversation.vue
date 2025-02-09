<template>
  <div class="flex-grow h-full flex flex-col bg-white">
    <div v-if="hasTopSide" class="px-4 py-2">
      <slot name="top-side"></slot>
    </div>
    <!-- chats -->
    <slot name="header"></slot>
    <div v-if="!loadingConversation" class="flex-grow flex flex-col gap-4 px-4 pt-4 overflow-auto">
      <template v-if="messages.length">
        <div v-for="(message, index) in messages" :key="index" class="message relative"
          :class="{ 'self-end': message.role === 'human', 'self-start': message.role === 'ai' }">
          <div class="flex items-end gap-4">
            <!-- <div
              v-if="message.role === 'ai'"
              class="border-2 border-primary rounded-full h-10 w-10 flex items-center justify-center flex-shrink-0"
            >
              <font-awesome-icon :icon="['fas', 'robot']" class="text-primary" />
            </div> -->
            <div class="flex flex-col">
              <div class="p-3" :class="{
                'bg-primary text-white max-w-md rounded-tl-xl rounded-tr-xl rounded-bl-xl shadow-sm': message.role === 'human',
                'bg-gray-100 text-black min-w-xs max-w-lg rounded-tl-xl rounded-tr-xl rounded-br-xl': message.role === 'ai',
              }">
                <div v-html="formatMessage(message.content)"></div>
                <slot name="message-footer" :message="message" :index="index"></slot>
              </div>
              <DisputeTypes v-if="message.type === 'start'" class="pt-2 max-w-2xl min-w-xs" :disputes="disputes"
                @active-dispute="handleActiveDispute" />
              <Attachment v-else-if="message.type === 'attachment'" class="pt-2 max-w-2xl min-w-xs"
                @attachment-selected="handleAttachmentSelected" />
            </div>
            <!-- <div v-if="message.role === 'human'" class="bg-gray-500 rounded-full h-10 w-10 flex-shrink-0">
              <img v-if="photo && photo !== 'undefined'" :src="`data:image/jpeg;base64,${photo}`" class="rounded-full h-full w-full" alt="sender" />
            </div> -->
          </div>
        </div>
      </template>
      <template v-else>
        <div class="flex justify-center items-center h-full text-gray-400">
          <div class="max-w-[400px] text-center">
            <slot name="no-messages">
              <span>Start a conversation by asking a question.</span>
            </slot>
          </div>
        </div>
      </template>
      <!-- waiting for ai response animation -->
      <div v-if="loading" class="flex gap-4 justify-start items-start">
        <!-- <div class="border-2 border-primary rounded-full h-10 w-10 flex items-center justify-center flex-shrink-0">
          <font-awesome-icon :icon="['fas', 'robot']" class="text-primary" />
        </div> -->
        <div class="p-3 bg-white text-black min-w-xs max-w-2xl rounded-tl-xl rounded-tr-xl rounded-br-xl">
          <div class="flex space-x-1 justify-center items-center">
            <div class="h-2 w-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
            <div class="h-2 w-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
            <div class="h-2 w-2 bg-gray-400 rounded-full animate-bounce"></div>
          </div>
        </div>
      </div>
      <div ref="bottomChat"></div>
    </div>
    <div v-else class="flex-grow flex justify-center items-center gap-4 px-4 pt-4">
      <!-- <Spinner size="xl" /> -->
    </div>
    <!-- query input -->
    <div class="bg-white sticky bottom-0 right-0 px-4 py-4">
      <slot name="query-input"></slot>
    </div>
  </div>
</template>
<script setup>
import DisputeTypes from "./dispute-types.vue"
import Attachment from "./attachment.vue"
import { ref, computed, onMounted, useSlots, nextTick, watch } from 'vue';
// import FormTextarea from '@/components/templates/FormTextarea.vue';
// import Button from '@/components/templates/Button.vue';
// import Spinner from '@/components/templates/Spinner.vue';

const props = defineProps({
  messages: {
    type: Array,
    required: true,
  },
  loading: {
    type: Boolean,
    required: true,
  },
  loadingConversation: {
    type: Boolean,
    required: false,
  },
});

const disputes = ref([
  { label: "Non-payment" },
  { label: "Non-release" },
  { label: "Payment mismatch" },
]);

const emits = defineEmits(['submit', 'active-dispute', 'attachment-selected']);
const slots = useSlots();

const photo = computed(() => localStorage.getItem('photo'));
const hasTopSide = computed(() => !!slots['top-side']);
const bottomChat = ref(null);

const formatMessage = (message) => {
  const div = document.createElement('div');
  div.innerText = message;
  return div.innerHTML;
};

const scrollToBottomChat = () => {
  console.log(bottomChat.value)
  nextTick(() => {
    if (bottomChat.value) bottomChat.value.scrollIntoView({ behavior: 'smooth' });
  });
};

watch(props.messages, () => {
  scrollToBottomChat();
});


const handleActiveDispute = (value) => {
  emits("active-dispute", value)
}

const attachment = ref(null);

const handleAttachmentSelected = (file) => {
  attachment.value = file;
  emits('attachment-selected', file);
};
</script>