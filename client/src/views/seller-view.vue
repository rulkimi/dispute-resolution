<script setup>
import Conversation from '@/components/conversation.vue'
import Textarea from '@/components/textarea.vue'
import { ref } from 'vue';

const messages = ref([
  {
    role: 'ai',
    content: 'Hello! We understand you are involved in a dispute regarding order #67890. We have received a report that the buyer may have requested to make a payment outside of the Deriv platform. We are investigating this matter to ensure the safety and security of our platform.',
    type: 'text'
  },
  {
    role: 'human',
    content: 'The buyer contacted me directly and said they were having trouble with the payment system on the platform.',
    type: 'text'
  },
  {
    role: 'ai',
    content: 'Thank you for your response. To help us with our investigation, could you please provide any communication logs or other evidence that supports your claim?',
    type: 'attachment'
  },
  {
    role: 'human',
    content: 'I can provide screenshots of our conversation.',
    type: 'text'
  },
  {
    role: 'ai',
    content: 'Thank you for providing the evidence. We are reviewing the information. Please note that facilitating transactions outside of the Deriv platform is strictly prohibited and can lead to account penalties. We will update you within 24-48 hours with the outcome of our investigation.',
    type: 'text'
  },
  {
    role: 'ai',
    content: 'Our investigation is complete. We have reviewed the evidence and determined that the buyer initiated the off-platform payment. While we understand the payment system may have presented challenges, facilitating transactions outside of the Deriv platform is a violation of our terms of service. This action compromises the security of our platform and puts both you and the buyer at risk. Your account has been temporarily suspended pending further review. We will contact you shortly with further instructions.',
    type: 'text'
  }
])

const handleActiveDispute = (value) => {
  console.log(value)
}

const handleAttachmentSelected = (value) => {
  console.log(value)
}

const query = ref("");
const isLoading = ref(false);
const isConversationOpen = ref(false)
const orderIds = ref([
  { orderId: '12345', date: '2023-10-27', amount: '$10', status: 'Pending' },
  { orderId: '67890', date: '2023-10-26', amount: '$20', status: 'In Dispute' },
  { orderId: '13579', date: '2023-10-25', amount: '$30', status: 'Pending' },
]);
const activeOrderId = ref("");

const raiseDispute = (orderId) => {
  activeOrderId.value = orderId;
  isConversationOpen.value = true;

  // send api request here
}

const sendMessage = () => {
  isLoading.value = true;
  if (query.value.trim() !== "") {
    messages.value.push({ role: 'human', content: query.value, type: 'text' });
    query.value = "";
  }
};
</script>

<template>
  <div class="container mx-auto">
    <div class="flex justify-start border-b">
      <img src="/public/deriv-logo.jpg" alt="" class="h-14">
      <!-- <div
        class="w-fit bg-primary text-white font-semibold my-3.5 px-2 py-1 rounded-lg cursor-pointer hover:bg-red-700"
        @click="isConversationOpen = true"
      >
        Raise a Dispute
      </div> -->
    </div>

    <div class="p-4">
      <table class="w-full border-collapse">
        <thead>
          <tr>
            <th class="text-left font-medium p-2">Order ID</th>
            <th class="text-left font-medium p-2">Date</th>
            <th class="text-left font-medium p-2">Amount</th>
            <th class="text-left font-medium p-2">Status</th>
            <th class="text-right font-medium p-2"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orderIds" :key="order.orderId" class="border-b">
            <td class="p-2">{{ order.orderId }}</td>
            <td class="p-2">{{ order.date }}</td>
            <td class="p-2">{{ order.amount }}</td>
            <td class="p-2">{{ order.status }}</td>
            <td class="p-2 text-right">
              <button :class="{
                'bg-primary text-white': order.status === 'In Dispute',
                'border border-primary text-primary hover:bg-primary hover:text-white': order.status !== 'In Dispute',
              }" class="py-1 px-3 rounded-full" @click="raiseDispute(order.orderId)">
                <template v-if="order.status === 'In Dispute'">
                  <font-awesome-icon :icon="['fas', 'circle-exclamation']" class="text-white" /> Check Dispute
                </template>
                <template v-else>
                  Raise Dispute
                </template>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div
      class="fixed w-[600px] top-0 bottom-0 shadow-md transition-all duration-500 ease-out"
      :class="isConversationOpen ? 'right-0' : 'right-[-1000px]'"
    >
      <Conversation
        :messages="messages"
        :loading="isLoading"
        :loadingConversation="false"
        @active-dispute="handleActiveDispute"
        @attachment-selected="handleAttachmentSelected"
      >
        <template #header>
          <div class="flex items-center justify-between px-4 py-2 border-b">
            <div class="flex items-center gap-4">
              <div class="rounded-full bg-gray-300 p-3 flex items-center justify-center">
                <font-awesome-icon :icon="['fas', 'user']" class="text-gray-600" />
              </div>
              <div>
                <p class="font-medium text-gray-800">Deriv Agent</p>
                <p class="text-sm text-gray-500">Order ID: {{ activeOrderId }}</p>
              </div>
            </div>
            <div class="text-primary hover:underline cursor-pointer" @click="isConversationOpen = false">Close</div>
          </div>
        </template>
        <template #query-input>
          <Textarea submit-on-enter id="query-input w-full" input-class="border" v-model="query" @submit="sendMessage">
            <template #append-icon>   
              <div class="flex gap-1">
                <div class="bg-gray-100 px-2 py-1 rounded-lg cursor-pointer hover:bg-gray-200">
                  <font-awesome-icon :icon="['fas', 'paperclip']" />
                </div>
                <div class="bg-primary px-2 py-1 rounded-lg cursor-pointer hover:bg-red-700" @click="sendMessage">
                  <font-awesome-icon class="text-white" :icon="['fas', 'paper-plane']" />
                </div>
              </div>
            </template>
          </Textarea>
        </template>
      </Conversation>
    </div>
  </div>
  <!-- <div class="absolute inset-0 bg-green-500 z-[-1]"></div> -->
</template>
