<template>
  <fieldset :class="width">
    <div v-if="hasLabel" class="block">
      <label :for="id" class="mb-2 text-sm font-medium text-black/60" :class="labelClass">
        <slot name="label">{{ label }}</slot>
      </label>
      <span v-if="required && !readonly" class="ml-1 text-red-500">*</span>
    </div>
    <div class="relative items-start" :class="isBlock ? 'flex' : 'inline-flex'">
      <div v-if="hasPrependIcon" :class="[prependIconClass, { 'opacity-50': disabled }]">
        <slot name="prepend-icon"></slot>
      </div>
      <div v-if="hasAppendIcon" :class="[appendIconClass, { 'opacity-50': disabled }]">
        <slot name="append-icon"></slot>
      </div>
      <textarea
        :id="id"
        :type="type"
        :placeholder="placeholder"
        :required="required"
        :value="modelValue"
        @change="onChange"
        @input="updateValue"
        @keydown="handleKeyDown"
        class="block py-3 outline-none bg-input-color"
        :class="[baseInputStyles, conditionalInputStyles]"
        :style="rows === 1 ? { height: height + 'px' } : {}"
        :rows="rows"
        :disabled="disabled"
        :maxLength="maxChars"
        :readonly="readonly"
      ></textarea>
      <small
        v-if="maxChars"
        class="absolute bottom-1 right-3 text-xs p-1 rounded"
        :class="{ 'text-red-500': currentCharCount > maxChars, 'text-gray-400': currentCharCount <= maxChars }"
      >
        {{ readonly ? currentCharCount + ' characters' : `${currentCharCount} / ${maxChars}` }}
      </small>
    </div>
    <div class="flex justify-between w-full">
      <transition name="shake-fade">
        <small v-if="errorMessage" class="text-red-400" :class="{ 'opacity-50': disabled }">
          {{ errorMessage }}
        </small>
      </transition>
    </div>
  </fieldset>
</template>

<script setup>
import { ref, computed, useSlots } from "vue";
/*
    Example usage:

    <FormTextarea
        v-model="description"
        label="Description"
        id="description-textarea"
        placeholder="Enter a detailed description"
        :required="true"
        :readonly="false"
        :error="hasError"
        :errorMessage="descriptionErrorMessage"
        :disabled="isDisabled"
        :rows="5"
        :maxChars="500"
        resizable
        @change="handleDescriptionChange"
    >
        <template #prepend-icon>
            <font-awesome-icon :icon="['fas', 'pencil-alt']" />
        </template>
        <template #append-icon>
            <font-awesome-icon :icon="['fas', 'check']" />
        </template>
    </FormTextarea>
*/
const props = defineProps({
  modelValue: {
    type: [String, Number],
    required: true,
  },
  label: {
    type: String,
    required: false,
  },
  id: {
    type: String,
    required: true,
  },
  type: {
    type: String,
    default: 'text',
  },
  placeholder: {
    type: String,
    required: false,
  },
  required: {
    type: Boolean,
    default: false,
  },
  readonly: {
    type: Boolean,
    default: false,
  },
  error: {
    type: Boolean,
    default: false,
  },
  errorMessage: {
    type: String,
    default: '',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  inputClass: {
    type: [String, Array],
    required: false,
  },
  labelClass: {
    type: String,
    required: false,
  },
  isBlock: {
    type: Boolean,
    default: true,
  },
  width: {
    type: String,
    default: 'w-full',
  },
  rows: {
    type: Number,
    default: 1,
  },
  maxChars: {
    type: Number,
    required: false,
  },
  resizable: {
    type: Boolean,
    default: false,
  },
  height: {
    type: String,
    default: '50',
  },
  submitOnEnter: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['update:modelValue', 'change', 'enter-press', 'submit']);
const slots = useSlots();

const hasLabel = computed(() => slots['label'] || props.label);
const hasPrependIcon = computed(() => slots['prepend-icon']);
const hasAppendIcon = computed(() => slots['append-icon']);
const prependIconClass = computed(() => props.rows === 1 ? 'absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500' : 'absolute left-3 top-3 text-gray-500');
const appendIconClass = computed(() => props.rows === 1 ? 'absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500' : 'absolute right-3 top-3 text-gray-500');
const baseInputStyles = computed(() => [props.inputClass, props.width]);
const conditionalInputStyles = computed(() => ({
  'border': (props.error || props.errorMessage) && !props.readonly,
  'border-red-300': props.error || props.errorMessage,
  'opacity-50 cursor-not-allowed': props.disabled,
  'border-b break-words !bg-transparent': props.readonly,
  'rounded-lg px-3': !props.readonly,
  'pl-10': hasPrependIcon.value,
  'pr-10': hasAppendIcon.value,
  'resize-none': !props.resizable,
}));
const currentCharCount = computed(() => props.modelValue.length);

const onChange = (event) => {
  emit('change', event.target.value);
};

const updateValue = (event) => {
  emit("update:modelValue", event.target.value)
}

const handleKeyDown = (event) => {
  if (props.submitOnEnter && event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    emit('submit');
  }
};
</script>

<style scoped>
.shake-fade-enter-active {
  animation: shake 0.5s ease;
}
.shake-fade-leave-active {
  transition: all 0.5s ease;
}
.shake-fade-enter-from, .shake-fade-leave-to {
  opacity: 0;
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-5px);
  }
  50% {
    transform: translateX(5px);
  }
  75% {
    transform: translateX(-5px);
  }
}
</style>