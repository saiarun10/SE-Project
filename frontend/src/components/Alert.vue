<template>
<div
  v-if="visible"
  class="alert position-fixed z-70 w-auto"
  :class="alertClasses"
  role="alert"
  :style="{ top: '150px', right: '40px' }"
>


    <div class="d-flex align-items-center">
      <svg
        v-if="type === 'success'"
        class="me-2"
        width="24"
        height="24"
        fill="currentColor"
        viewBox="0 0 24 24"
      >
        <path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
      <svg
        v-if="type === 'error'"
        class="me-2"
        width="24"
        height="24"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M6 18L18 6M6 6l12 12"
        />
      </svg>
      <svg
        v-if="type === 'alert'"
        class="me-2"
        width="24"
        height="24"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M12 9v2m0 4h.01M12 3a9 9 0 100 18 9 9 0 000-18z"
        />
      </svg>
      <svg
        v-if="type === 'notification'"
        class="me-2"
        width="24"
        height="24"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 00-5-5.917V5a2 2 0 10-4 0v.083A6 6 0 004 11v3.159c0 .538-.214 1.055-.595 1.436L2 17h5m4 0v1a3 3 0 11-6 0v-1m6 0H9"
        />
      </svg>
      <svg
        v-if="type === 'other'"
        class="me-2"
        width="24"
        height="24"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M13 16h-1v-4h-1m1-4h.01M12 3a9 9 0 100 18 9 9 0 000-18z"
        />
      </svg>
      <span>{{ message }}</span>
      <button
        type="button"
        class="btn-close ms-3"
        aria-label="Close"
        @click="close"
      ></button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Alert',
  props: {
    message: {
      type: String,
      required: true,
    },
    type: {
      type: String,
      default: 'notification',
      validator: (value) =>
        ['success', 'notification', 'alert', 'error', 'other'].includes(value),
    },
    duration: {
      type: Number,
      default: 5000, // 5 seconds
    },
  },
  data() {
    return {
      visible: true,
    };
  },
  computed: {
    alertClasses() {
      return {
        'success': 'alert-success',
        'notification': 'alert-primary',
        'alert': 'alert-warning',
        'error': 'alert-danger',
        'other': 'alert-secondary',
      }[this.type];
    },
  },
  mounted() {
    if (this.duration > 0) {
      setTimeout(() => {
        this.close();
      }, this.duration);
    }
  },
  methods: {
    close() {
      this.visible = false;
      this.$emit('close');
    },
  },
};
</script>