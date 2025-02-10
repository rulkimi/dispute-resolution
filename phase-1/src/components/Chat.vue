<template>
  <div class="container-sm mt-20">
    <div class="mx-5">
      <Message
        v-for="{ id, text, userPhotoURL, userName, userId } in messages"
        :key="id"
        :name="userName"
        :photo-url="userPhotoURL"
        :sender="userId === user?.uid"
      >
        {{ text }}
      </Message>
    </div>
  </div>

  <div ref="bottom" class="mt-20" />

  <div class="bottom">
    <div class="container-sm">
      <form v-if="isLogin" @submit.prevent="send">
        <input class="bg-white" v-model="message" placeholder="Message" required />
        <button type="submit">
          <SendIcon />
        </button>
      </form>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script>
import { ref, watch, nextTick } from 'vue'
import { useAuth, useChat } from '@/firebase'
import SendIcon from './SendIcon.vue'
import Message from './Message.vue'
import axios from 'axios' // Import Axios for API calls

export default {
  components: { Message, SendIcon },
  setup() {
    const { user, isLogin } = useAuth()
    const { messages, sendMessage } = useChat()

    const bottom = ref(null)
    const message = ref('')
    const errorMessage = ref('') // Error message state

    watch(
      messages,
      () => {
        nextTick(() => {
          bottom.value?.scrollIntoView({ behavior: 'smooth' })
        })
      },
      { deep: true }
    )

    const analyzeMessage = async (text) => {
    console.log('Analyzing message:', text)
    try {
      const response = await fetch(`http://localhost:8000/analyze_text?text=${encodeURIComponent(text)}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        }
      });

      if (!response.ok) {
        throw new Error("Failed to analyze text");
      }

      const result = await response.json();
      const { platform_switch_intent } = result.data;

      if (platform_switch_intent) {
        sendMessage("Message deleted. This user appears to be attempting unauthorized platform switching, which is a violation of our terms of service and may result in account termination.  We recommend avoiding further communication with this user.");
        message.value = ""
        errorMessage.value = "Platform switching intention detected. This action is not permitted."
        return false;
      }

      //URGENT: User [username/ID] attempting platform switch. Be aware of any potential fraud .
      return true;
    } catch (error) {
      console.error('Error analyzing text:', error);
      errorMessage.value = "Failed to analyze message. Please try again.";
      return false;
    }
  };


    const send = async () => {
      errorMessage.value = '' // Clear previous error

      const isSafe = await analyzeMessage(message.value)
      if (!isSafe) return // Stop message from sending if flagged

      sendMessage(message.value)
      message.value = ''
    }

    return { user, isLogin, messages, bottom, message, send, errorMessage }
  }
}
</script>
