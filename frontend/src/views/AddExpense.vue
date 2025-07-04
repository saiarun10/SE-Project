<template>
 <Navbar /> 
  <div class="container mt-5" style="font-family: var(--bs-body-font-family); max-width: 600px;">
    <h2 class="fw-bold text-center mb-4">Add A New Expense</h2>

    <!-- Tab Toggle -->
    <div class="nav nav-tabs justify-content-center mb-4">
      <button
        class="nav-link"
        :class="{ active: selectedTab === 'expense' }"
        @click="selectedTab = 'expense'"
      >
        Expense
      </button>
      <button
        class="nav-link"
        :class="{ active: selectedTab === 'income' }"
        @click="selectedTab = 'income'"
      >
        Income
      </button>
    </div>

    <!-- Form -->
    <form @submit.prevent="handleSubmit">
      <div class="mb-3">
        <label class="form-label">Date</label>
        <input type="date" v-model="form.date" class="form-control" required />
      </div>

      <div class="mb-3">
        <label class="form-label">{{ selectedTab === 'expense' ? 'Expense' : 'Income' }} Name</label>
        <input type="text" v-model="form.name" class="form-control" placeholder="e.g. Grocery, Bonus" required />
      </div>

      <div class="mb-3 position-relative">
        <label class="form-label">Category</label>
        <input
          type="text"
          v-model="form.category"
          @input="filterSuggestions"
          @focus="showSuggestions = true"
          @blur="hideSuggestions"
          class="form-control"
          autocomplete="off"
          placeholder="Start typing..."
          required
        />
        <ul v-if="showSuggestions && filteredCategories.length" class="list-group position-absolute w-100 shadow">
          <li
            v-for="(cat, index) in filteredCategories"
            :key="index"
            class="list-group-item list-group-item-action"
            @mousedown.prevent="selectCategory(cat)"
          >
            {{ cat }}
          </li>
        </ul>
      </div>

      <div class="mb-3">
        <label class="form-label">Amount</label>
        <input type="number" v-model="form.amount" class="form-control" placeholder="₹" required />
      </div>

      <button type="submit" class="btn btn-primary w-100">Save</button>
    </form>
  </div>
  <Footer />
</template>

<script>
import { ref, watch } from 'vue';
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue'
export default {
  name: 'AddExpense'
  ,
  components: {
    Navbar,
    Footer
  },
  setup() {
    const selectedTab = ref('expense');

    const form = ref({
      date: '',
      name: '',
      category: '',
      amount: ''
    });

    const resetForm = () => {
      form.value = {
        date: '',
        name: '',
        category: '',
        amount: ''
      };
    };

    watch(selectedTab, () => {
      resetForm();
    });

    const allCategories = [
      'Food', 'Travel', 'Utilities', 'Entertainment', 'Health',
      'Education', 'Job', 'Side Hustle', 'Investment', 'Misc'
    ];

    const showSuggestions = ref(false);
    const filteredCategories = ref([]);

    const filterSuggestions = () => {
      const input = form.value.category.toLowerCase();
      filteredCategories.value = allCategories.filter(cat =>
        cat.toLowerCase().includes(input)
      );
    };

    const selectCategory = (category) => {
      form.value.category = category;
      showSuggestions.value = false;
    };

    const hideSuggestions = () => {
      setTimeout(() => {
        showSuggestions.value = false;
      }, 200);
    };

    const handleSubmit = () => {
      const payload = {
        ...form.value,
        type: selectedTab.value
      };
      console.log('Sending JSON:', JSON.stringify(payload, null, 2));
      alert(`Submitted:\n${JSON.stringify(payload, null, 2)}`);
    };

    return {
      selectedTab,
      form,
      allCategories,
      showSuggestions,
      filteredCategories,
      filterSuggestions,
      selectCategory,
      hideSuggestions,
      handleSubmit
    };
  }
};

</script>

<style scoped>
.nav-link.active {
  background-color: #e0e0e0;
  font-weight: bold;
}
ul.list-group {
  z-index: 10;
  max-height: 200px;
  overflow-y: auto;
}
</style>
