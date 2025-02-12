<script setup>
import Conversation from '@/components/conversation.vue'
import Textarea from '@/components/textarea.vue'
import { ref } from 'vue';

const messages = ref([
  {
    role: 'ai',
    content: 'Hello Joel! \n\n Are you looking to raise a dispute? Please choose the type of dispute that best describes your concern and provide a brief explanation of the issue.',
    type: 'start'
  },
  { role: 'human', content: 'I paid for the item, but the seller claims they never received the payment and hasn\'t sent it.', type: 'text' },
  {
    role: 'ai',
    content: "Thank you for providing details about your dispute. I'm now reviewing the information you've provided. This may take a few minutes.",
    type: 'text'
  },
  {
    role: 'ai',
    content: "I've completed my review. Our investigation reveals a potential issue. The seller's account shows no record of receiving the payment, however, we've uncovered evidence suggesting the seller may be using a secondary account to conduct transactions outside of our platform.",
    type: 'text'
  },
  {
    role: 'ai',
    content: "This is a serious violation of our terms of service. We are taking steps to address this issue and ensure the safety of our users. We've temporarily suspended the seller's accounts pending a full investigation.",
    type: 'text'
  },
  {
    role: 'ai',
    content: "We understand your frustration. While we are investigating the seller's actions, we cannot issue a refund at this time.  We will issue a warning to the seller regarding conducting transactions outside of the platform. We will update you on the progress of our investigation and the next steps.",
    type: 'text'
  },
  {
    role: 'ai',
    content: "Our investigation is complete.  We have determined that the seller violated our terms of service by conducting transactions outside of the platform. As a result, the seller's account has been permanently suspended. We have issued a warning to the seller and will be monitoring their activity closely. We are unable to issue a refund at this time due to the seller's actions.",
    type: 'text'
  },
  {
    role: 'ai',
    content: "We sincerely apologize for the inconvenience this has caused. We are committed to providing a safe and secure marketplace for all our users.",
    type: 'end'
  },
  {
    role: 'human',
    content: 'Thank you!',
    type: 'text'
  },
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

const sendMessage = async () => {
  isLoading.value = true;
  if (query.value.trim() !== "") {
    messages.value.push({ role: 'human', content: query.value, type: 'text' });

    try {
      const response = await fetch(`http://localhost:8000/chat/dispute/send?dispute_id=${activeOrderId.value}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sender_id: 'buyer123', // Replace with actual buyer ID
          receiver_id: 'system', // Or 'agent'
          message: query.value,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      messages.value.push({ role: 'ai', content: data.response, type: 'text' }); // Assuming the API returns a 'response' field
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      isLoading.value = false; // Ensure loading is set to false
    }

    query.value = "";
  } else {
    isLoading.value = false;
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
            <td class="p-2" :class="{ 'text-primary': order.status === 'In Dispute' }">{{ order.status }}</td>
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

    <div class="fixed w-[600px] top-0 bottom-0 shadow-md transition-all duration-500 ease-out"
      :class="isConversationOpen ? 'right-0' : 'right-[-1000px]'">
      <Conversation :messages="messages" :loading="isLoading" :loadingConversation="false"
        @active-dispute="handleActiveDispute" @attachment-selected="handleAttachmentSelected">
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
                <!-- <div class="bg-gray-100 px-2 py-1 rounded-lg cursor-pointer hover:bg-gray-200">
                  <font-awesome-icon :icon="['fas', 'paperclip']" />
                </div> -->
                <div
                  :class="isLoading ? 'bg-gray-400' : 'bg-primary hover:bg-red-700'"
                  class="px-2 py-1 rounded-lg cursor-pointer"
                  @click="sendMessage"
                  :disabled="isLoading"
                >
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
