<template>
  <div class="flex flex-wrap space-x-1">
    <div
      @click="onFileSelected"
      class="border border-dashed rounded-md py-1 px-2 cursor-pointer text-sm"
    >
      <input type="file" ref="fileInput" style="display:none;" @change="handleFileSelected">
      <font-awesome-icon :icon="['fas', 'paperclip']" />
      {{ attachment ? attachment.name : 'Attach file' }}
    </div>
  </div>
</template>

<script setup>
import { ref, defineEmits } from 'vue';

const emits = defineEmits(['attachment-selected']);
const attachment = ref(null);
const fileInput = ref(null);

const onFileSelected = () => {
  fileInput.value.click();
};

const handleFileSelected = (event) => {
  const file = event.target.files[0];
  attachment.value = file;
  emits('attachment-selected', file);
};

</script>
