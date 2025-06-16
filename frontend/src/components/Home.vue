<template>
  <div class="container mt-5">
    <div class="text-center">
      <h1 class="mb-4">Welcome to Our Platform</h1>
      <p class="lead">
        Discover a world of quizzes and learning opportunities. Get started by
        signing up or logging in!
      </p>
      <div class="mt-4">
        <router-link to="/signup" class="btn btn-primary mx-2"
          >Sign Up</router-link
        >
        <router-link to="/login" class="btn btn-outline-primary mx-2"
          >Log In</router-link
        >
        <router-link to="/about" class="btn btn-outline-secondary mx-2"
          >Learn More</router-link
        >
      </div>
    </div>
    <div class="row mt-5">
      <div class="col-md-4">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Explore Quizzes</h5>
            <p class="card-text">
              Take on exciting quizzes designed for all levels.
            </p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Track Progress</h5>
            <p class="card-text">
              Monitor your scores and improve over time.
            </p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Join Community</h5>
            <p class="card-text">
              Connect with learners and share knowledge.
            </p>
          </div>
        </div>
      </div>
    </div>
    <!-- Add ChatBot component -->
    <ChatBot />
  </div>
</template>

<script>
import ChatBot from '@/components/ChatBot.vue'; // Import ChatBot component

export default {
  name: "Home",
  components: {
    ChatBot, // Register ChatBot component
  },
  mounted() {
    console.log("Home component is rendering");
  },
};
</script>

<style scoped>
.card {
  transition: transform 0.2s;
}
.card:hover {
  transform: scale(1.05);
}
</style>