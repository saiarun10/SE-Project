<template>
  <Navbar />
  <div class="container mt-4" style="font-family: var(--bs-body-font-family);">
    <h2 class="text-center mb-4 fw-bold fs-3">Let's Look at your Expenses, Richie</h2>

    <!-- Tabs -->
    <ul class="nav nav-tabs justify-content-center mb-4 border-0">
      <li class="nav-item" v-for="tab in tabs" :key="tab">
        <a
          href="#"
          class="nav-link px-4 py-2"
          :class="{ active: selectedTab === tab, 'fw-bold': selectedTab === tab }"
          @click.prevent="selectTab(tab)"
        >
          {{ tab }}
        </a>
      </li>
    </ul>

    <!-- KPI Row (Used in Daily & Summary Tabs) -->
    <div v-if="selectedTab === 'Daily' || selectedTab === 'Summary'" class="row text-center mb-4 g-3">
      <div class="col-md-4">
        <div class="bg-light p-3 border rounded">
          <h6 class="text-muted">Monthly Budget</h6>
          <h4 class="fw-bold text-success">Rs. {{ monthlyBudget.toLocaleString() }}</h4>
        </div>
      </div>
      <div class="col-md-4">
        <div class="bg-light p-3 border rounded">
          <h6 class="text-muted">Monthly Expense</h6>
          <h4 class="fw-bold text-danger">Rs. {{ monthlyExpense.toLocaleString() }}</h4>
        </div>
      </div>
      <div class="col-md-4">
        <div class="bg-light p-3 border rounded">
          <label for="monthDropdown" class="form-label text-muted">Choose Month</label>
          <select id="monthDropdown" class="form-select" v-model="selectedMonth" @change="filterMonthlyData">
            <option v-for="month in months" :key="month" :value="month">{{ month }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Daily View -->
    <div v-if="selectedTab === 'Daily'">
      <div v-for="(expenses, date) in groupedExpenses" :key="date" class="mb-4">
        <h5 class="text-dark border-bottom pb-2">{{ formatDate(date) }}</h5>
        <ul class="list-group">
          <li
            class="list-group-item d-flex justify-content-between align-items-start"
            v-for="expense in expenses"
            :key="expense.name + expense.amount + expense.date"
          >
            <div class="me-auto">
              <div class="fw-bold">{{ expense.name }}</div>
              <small class="text-muted">{{ expense.category }}</small>
            </div>
            <span :class="{'text-success': expense.type === 'income', 'text-danger': expense.type === 'expense'}">
              ₹{{ Number(expense.amount).toLocaleString() }}
            </span>
          </li>
        </ul>
      </div>
    </div>

    <!-- Monthly View -->
    <div v-else-if="selectedTab === 'Monthly'">
      <div class="table-responsive">
        <table class="table table-bordered">
          <thead class="table-light">
            <tr>
              <th>Month</th>
              <th>Income</th>
              <th>Expense</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="month in months" :key="month">
              <td>{{ month }}</td>
              <td class="text-success fw-bold">
                ₹{{ monthlyGroupedData[month]?.filter(e => e.type.toLowerCase() === 'income').reduce((sum, e) => sum + Number(e.amount), 0).toLocaleString() }}
              </td>
              <td class="text-danger fw-bold">
                ₹{{ monthlyGroupedData[month]?.filter(e => e.type.toLowerCase() === 'expense').reduce((sum, e) => sum + Number(e.amount), 0).toLocaleString() }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Summary View -->
    <div v-else-if="selectedTab === 'Summary'">
      <div class="row mt-5">
        <div class="col-md-6">
          <h5 class="text-center mb-3">Expense Distribution</h5>
          <canvas id="expenseChart"></canvas>
        </div>
        <div class="col-md-6">
          <h5 class="text-center mb-3">Income Distribution</h5>
          <canvas id="incomeChart"></canvas>
        </div>
      </div>
    </div>
  </div>
  <router-link to="/add_expense" class="fab">
  <span class="fs-1 text-white">+</span>  
</router-link>
<Footer/>
</template>

<script>
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue'
import { ref, onMounted, computed, watch } from 'vue';
import { Chart, registerables } from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';

Chart.register(...registerables, ChartDataLabels);

export default {
  name: 'ExpenseInterface',
  components: {
    Navbar,
    Footer
  },
  setup() {
    const tabs = ['Daily', 'Monthly', 'Summary'];
    const selectedTab = ref('Daily');
    const selectedMonth = ref('');

    const months = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];

    const allTransactions = ref([]);
    const monthlyGroupedData = ref({});
    const currentMonthData = ref([]);

    const fetchAllExpenses = async () => {
      try {
        // const res = await fetch(`/api/get_all_expense`);
        // const data = await res.json();
                      const data = {
        "expenses": [
          // January
          { "date": "2025-01-05", "name": "Salary", "category": "Job", "type": "income", "amount": 30000 },
          { "date": "2025-01-10", "name": "Groceries", "category": "Household", "type": "expense", "amount": 3200 },
          { "date": "2025-01-18", "name": "Internet", "category": "Utilities", "type": "expense", "amount": 800 },

          // February
          { "date": "2025-02-05", "name": "Salary", "category": "Job", "type": "income", "amount": 30000 },
          { "date": "2025-02-14", "name": "Dining", "category": "Food", "type": "expense", "amount": 1500 },
          { "date": "2025-02-25", "name": "Electricity", "category": "Utilities", "type": "expense", "amount": 1200 },

          // March
          { "date": "2025-03-03", "name": "Freelance", "category": "Side Hustle", "type": "income", "amount": 8000 },
          { "date": "2025-03-12", "name": "Shopping", "category": "Lifestyle", "type": "expense", "amount": 2500 },
          { "date": "2025-03-20", "name": "Petrol", "category": "Travel", "type": "expense", "amount": 1800 },

          // April
          { "date": "2025-04-01", "name": "Salary", "category": "Job", "type": "income", "amount": 30000 },
          { "date": "2025-04-07", "name": "Gym", "category": "Health", "type": "expense", "amount": 1200 },
          { "date": "2025-04-15", "name": "Mobile Recharge", "category": "Utilities", "type": "expense", "amount": 500 },

          // May
          { "date": "2025-05-01", "name": "Salary", "category": "Job", "type": "income", "amount": 30000 },
          { "date": "2025-05-02", "name": "Groceries", "category": "Household", "type": "expense", "amount": 2200 },
          { "date": "2025-05-20", "name": "Medical Checkup", "category": "Health", "type": "expense", "amount": 2000 },

          // June
          { "date": "2025-06-05", "name": "Bonus", "category": "Job", "type": "income", "amount": 10000 },
          { "date": "2025-06-11", "name": "Movie", "category": "Entertainment", "type": "expense", "amount": 700 },
          { "date": "2025-06-24", "name": "Electricity", "category": "Utilities", "type": "expense", "amount": 1100 },

          // July
          { "date": "2025-07-05", "name": "Salary", "category": "Job", "type": "income", "amount": 30000 },
          { "date": "2025-07-06", "name": "allowance", "category": "Job", "type": "income", "amount": 4000 },
          { "date": "2025-07-06", "name": "freelance", "category": "freelance", "type": "income", "amount": 10000 },
          { "date": "2025-07-07", "name": "profit", "category": "investment", "type": "income", "amount": 10000 },
          { "date": "2025-07-08", "name": "freelance", "category": "freelance", "type": "income", "amount": 5000 },
          { "date": "2025-07-05", "name": "mobile recharge", "category": "Bills", "type": "expense", "amount": 1000 },
          { "date": "2025-07-11", "name": "medicines", "category": "health", "type": "expense", "amount": 4000 },
          { "date": "2025-07-21", "name": "Travel", "category": "Vacation", "type": "expense", "amount": 15000 },
          { "date": "2025-07-22", "name": "stay", "category": "Vacation", "type": "expense", "amount": 5000 },
          { "date": "2025-07-24", "name": "gym", "category": "health", "type": "expense", "amount": 3000 },
          { "date": "2025-07-24", "name": "Dining Out", "category": "Food", "type": "expense", "amount": 1200 },

          // August
          { "date": "2025-08-05", "name": "Salary", "category": "Job", "type": "income", "amount": 30000 },
          { "date": "2025-08-08", "name": "Books", "category": "Education", "type": "expense", "amount": 1500 },
          { "date": "2025-08-29", "name": "Online Course", "category": "Education", "type": "expense", "amount": 2500 },

          // September
          { "date": "2025-09-01", "name": "Freelance", "category": "Side Hustle", "type": "income", "amount": 5000 },
          { "date": "2025-09-15", "name": "Gym", "category": "Health", "type": "expense", "amount": 1200 },
          { "date": "2025-09-30", "name": "Internet", "category": "Utilities", "type": "expense", "amount": 800 },

          // October
          { "date": "2025-10-05", "name": "Salary", "category": "Job", "type": "income", "amount": 30000 },
          { "date": "2025-10-10", "name": "Rent", "category": "Housing", "type": "expense", "amount": 8000 },
          { "date": "2025-10-28", "name": "Snacks", "category": "Food", "type": "expense", "amount": 500 },

          // November
          { "date": "2025-11-05", "name": "Interest", "category": "Savings", "type": "income", "amount": 1000 },
          { "date": "2025-11-18", "name": "Laptop Repair", "category": "Electronics", "type": "expense", "amount": 3000 },
          { "date": "2025-11-25", "name": "Gifts", "category": "Misc", "type": "expense", "amount": 1000 },

          // December
          { "date": "2025-12-01", "name": "Salary", "category": "Job", "type": "income", "amount": 30000 },
          { "date": "2025-12-15", "name": "Christmas Shopping", "category": "Lifestyle", "type": "expense", "amount": 4000 },
          { "date": "2025-12-24", "name": "Dining Out", "category": "Food", "type": "expense", "amount": 2000 }
        ]
      }
;
        allTransactions.value = data.expenses || [];
        groupMonthlyData();
        filterMonthlyData();
      } catch (err) {
        console.error('Fetch error:', err);
      }
    };

    const groupMonthlyData = () => {
      const grouped = {};
      for (const item of allTransactions.value) {
        const dateObj = new Date(item.date);
        const month = months[dateObj.getMonth()];
        if (!grouped[month]) grouped[month] = [];
        grouped[month].push(item);
      }
      monthlyGroupedData.value = grouped;
    };

    const filterMonthlyData = () => {
      currentMonthData.value = monthlyGroupedData.value[selectedMonth.value] || [];
      updateCharts();
    };

    const monthlyBudget = computed(() => {
      return currentMonthData.value
        .filter(item => item.type.toLowerCase() === 'income')
        .reduce((sum, item) => sum + Number(item.amount), 0);
    });

    const monthlyExpense = computed(() => {
      return currentMonthData.value
        .filter(item => item.type.toLowerCase() === 'expense')
        .reduce((sum, item) => sum + Number(item.amount), 0);
    });

    const groupedExpenses = computed(() => {
      const groups = {};
      for (const item of currentMonthData.value) {
        const dateKey = item.date;
        if (!groups[dateKey]) groups[dateKey] = [];
        groups[dateKey].push(item);
      }
      return groups;
    });

    const selectTab = (tab) => {
      selectedTab.value = tab;
      if (tab === 'Monthly' || tab === 'Summary') {
        groupMonthlyData();
        filterMonthlyData();
      }
    };

    const getCurrentMonthName = () => {
      const date = new Date();
      return months[date.getMonth()];
    };

    const formatDate = (dateStr) => {
      const options = { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' };
      return new Date(dateStr).toLocaleDateString('en-GB', options);
    };

    let expenseChart, incomeChart;

const updateCharts = () => {
  const expenseCtx = document.getElementById('expenseChart');
  const incomeCtx = document.getElementById('incomeChart');

  const expenseData = {};
  const incomeData = {};

  for (const item of currentMonthData.value) {
    const category = item.category;
    if (item.type.toLowerCase() === 'expense') {
      expenseData[category] = (expenseData[category] || 0) + Number(item.amount);
    } else if (item.type.toLowerCase() === 'income') {
      incomeData[category] = (incomeData[category] || 0) + Number(item.amount);
    }
  }

  if (expenseChart) expenseChart.destroy();
  if (incomeChart) incomeChart.destroy();

  // ---- Chart Options with % Labels ----
  const pieChartOptions = (title) => ({
    responsive: true,
    plugins: {
      datalabels: {
        formatter: (value, context) => {
          const total = context.chart.data.datasets[0].data.reduce((sum, v) => sum + v, 0);
          const percentage = (value / total * 100).toFixed(1);
          return `${percentage}%`;
        },
        color: '#fff',
        font: {
          weight: 'bold',
          size: 14
        }
      },
      title: {
        display: true,
        text: title,
        font: {
          size: 16
        }
      },
      legend: {
        position: 'right'
      }
    }
  });

  // ---- Expense Chart ----
  expenseChart = new Chart(expenseCtx, {
    type: 'pie',
    data: {
      labels: Object.keys(expenseData),
      datasets: [{
        data: Object.values(expenseData),
        backgroundColor: ['#f39c12', '#e74c3c', '#8e44ad', '#27ae60', '#3498db', '#2c3e50']
      }]
    },
    options: pieChartOptions('Expense Distribution'),
    plugins: [ChartDataLabels]
  });

  // ---- Income Chart ----
  incomeChart = new Chart(incomeCtx, {
    type: 'pie',
    data: {
      labels: Object.keys(incomeData),
      datasets: [{
        data: Object.values(incomeData),
        backgroundColor: ['#1abc9c', '#9b59b6', '#2980b9', '#f1c40f', '#34495e', '#c0392b']
      }]
    },
    options: pieChartOptions('Income Distribution'),
    plugins: [ChartDataLabels]
  });
};


    onMounted(() => {
      selectedMonth.value = getCurrentMonthName();
      fetchAllExpenses();
    });

    return {
      tabs,
      selectedTab,
      selectTab,
      selectedMonth,
      months,
      allTransactions,
      monthlyGroupedData,
      currentMonthData,
      monthlyBudget,
      monthlyExpense,
      groupedExpenses,
      formatDate,
      filterMonthlyData
    };
  }
};
</script>

<style scoped>
.nav-link.active {
  background-color: #e0e0e0;
  color: black !important;
  border-radius: 0;
}
canvas {
  max-width: 100%;
}
.fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 60px;
  height: 60px;
  background-color: #007bff;
  border-radius: 50%;
  text-align: center;
  line-height: 60px;
  font-size: 32px;
  font-weight: bold;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  text-decoration: none;
  display: flex;
  justify-content: center;
  align-items: center;
}

.fab:hover {
  background-color: #0056b3;
  text-decoration: none;
}

</style>
