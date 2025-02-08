<template>
  <div class="flex flex-wrap space-x-1">
    <div
      v-for="dispute in disputes"
      :key="dispute.id"
      @click="setActiveDispute(dispute)"
      :class="{
        'bg-primary text-white': activeDispute === dispute,
        'bg-white text-black': activeDispute !== dispute
      }"
      class="border border-dashed rounded-md py-1 px-2 cursor-pointer text-sm"
    >
      {{ dispute.label }}
    </div>
  </div>
</template>

<script setup>
import { ref, defineEmits } from 'vue';

const props = defineProps({
  disputes: {
    type: Array,
    required: true,
  },
});

const emits = defineEmits(["active-dispute"]);

const activeDispute = ref(null);

const setActiveDispute = (dispute) => {
  activeDispute.value = dispute;
  emits("active-dispute", dispute);
};
</script>