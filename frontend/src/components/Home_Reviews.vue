<template>
  <section class="bg-white px-4 pb-5">
    <div class="container-fluid">
      <h3 class="text-center fw-bold fs-2 text-primary mb-5 mt-0">User Reviews</h3>

      <div class="row g-4 justify-content-center">
        <div
          v-for="(review, index) in reviews"
          :key="index"
          class="col-12 col-md-6 col-lg-4 d-flex"
        >
          <div class="card review-card shadow-sm w-100 border-0">
            <div class="card-body d-flex flex-column justify-content-between h-100">
              <p class="review-text text-dark mb-4">
                {{ review.text }}
              </p>
              <div>
                <p class="fw-semibold text-primary mb-1">- {{ review.name }}</p>
                <p class="text-muted small">{{ review.role }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'UserReviews',
  data() {
    return {
      reviews: [
        { text: "This platform helped me understand budgeting and savings in a simple, practical way. Truly a must-have for students.", name: "Neha", role: "Student" },
        { text: "An insightful tool for managing personal finances. The investment simulations are great!", name: "Raj", role: "Beta tester" },
        { text: "I used this with my children to help them learn about money. Very effective and intuitive.", name: "Aisha", role: "Parent" },
        { text: "Finally, an edtech product that focuses on real-life skills. Great UI and course content.", name: "Anil", role: "Working Professional" },
        { text: "The quizzes and visuals make complex topics so easy to grasp. Great for self-paced learning.", name: "Simran", role: "Designer" },
        { text: "As a developer, I appreciate the clean experience. I even learned to optimize my own savings!", name: "Karan", role: "Developer" },
      ]
    }
  }
}
</script>

<style scoped>
h3 {
  margin-top: 0 !important;
  padding-top: 0 !important;
}

.review-card {
  background-color: #f8f9fc;
  border-radius: 16px;
  padding: 24px;
  transition: transform 0.3s ease, box-shadow 0.3s ease, background-color 0.3s ease;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

/* Hover effects using odd/even */
.review-card:nth-child(odd):hover {
  background-color: #e6f9f0; /* light green */
  transform: translateY(-6px);
  box-shadow: 0 10px 20px rgba(0, 128, 64, 0.1);
}

.review-card:nth-child(even):hover {
  background-color: #e8f2ff; /* light blue */
  transform: translateY(-6px);
  box-shadow: 0 10px 20px rgba(91, 223, 91, 0.1);
}

.review-text {
  font-size: 1rem;
  line-height: 1.6;
}

.text-primary {
  color: #004080 !important;
}
</style>
