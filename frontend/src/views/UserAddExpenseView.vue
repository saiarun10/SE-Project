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
  <AppFooter />
</template>

<script>
import { ref, watch, onMounted } from 'vue';
import axios from 'axios';
import Navbar from '@/components/Navbar.vue';
import AppFooter from '@/components/Footer.vue';
import { useStore } from 'vuex';
const BASE_URL = `${import.meta.env.VITE_BASE_URL}`;
export default {
  name: 'AddExpense',
  components: {
    Navbar,
    AppFooter
  },
  setup() {
    const selectedTab = ref('expense');
    const store = useStore();
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

    const allCategories = ref([]);  // initially empty
    const showSuggestions = ref(false);
    const filteredCategories = ref([]);

    const fetchCategories = async () => {
      try {
        const response = await axios.get(`${BASE_URL}/api/get_all_categories`);
        allCategories.value = response.data.categories || [];  
      } catch (error) {
        console.error('Failed to load categories:', error);
        allCategories.value = [];
      }
    };

    const filterSuggestions = () => {
      const input = form.value.category.toLowerCase();
      filteredCategories.value = allCategories.value.filter(cat =>
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

    const handleSubmit = async () => {
      const payload = {
        ...form.value,
        type: selectedTab.value
      };
      try {
        const response = await axios.post(`${BASE_URL}/api/add_expense`,
    payload, // payload is the JSON body
    {
        headers: {
            Authorization: `Bearer ${store.state.token}`,
            'Content-Type': 'application/json'
        }
    });
        console.log('Response:', response.data);
        alert('Expense added successfully!');
        resetForm();
      } catch (error) {
        console.error('Error submitting form:', error);
        alert('Failed to add expense. Please try again.');
      }
    };

    onMounted(() => {
      fetchCategories();
    });

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
