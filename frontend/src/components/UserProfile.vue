<template>
  <div class="container mt-5">
    <nav class="d-flex justify-content-between align-items-center mb-4">
      <div class="fw-bold">GrowUp Richie</div>
      <div>
        <a href="#" class="text-decoration-none me-2">Home</a>
        <button class="btn btn-outline-secondary">
          <i class="bi bi-person-lines-fill"></i>
        </button>
      </div>
    </nav>

    <h2 class="fw-bold">Hello Richie </h2>

    <div class="text-center my-4">
      <div class="position-relative d-inline-block">
        <img
          src="https://cdn-icons-png.flaticon.com/512/194/194931.png"
          alt="Profile"
          class="rounded-circle border"
          width="150"
          height="150"
        />
        <div class="mt-2">
          <span class="fw-semibold">Choose Profile Picture</span>
          <i class="bi bi-pencil ms-2"></i>
        </div>
      </div>
    </div>

    <table class="table table-borderless w-75 mx-auto">
      <tbody>
        <tr>
          <th scope="row">Name</th>
          <td>Suraaj Mehta</td>
        </tr>
        <tr>
          <th scope="row">Date of Birth</th>
          <td>14th February 1998</td>
        </tr>
        <tr>
          <th scope="row">Contact</th>
          <td>+91-9876543210</td>
        </tr>
        <tr>
          <th scope="row">Email</th>
          <td><a href="mailto:suraaj.mehta@example.com">suraaj.mehta@example.com</a></td>
        </tr>
        <tr>
          <th scope="row">Premium ID</th>
          <td>PRM-982341</td>
        </tr>
        <tr>
          <th scope="row">Date Joined</th>
          <td>15th March 2024</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
// You can add reactive data or props if needed
</script>

<style scoped>
img {
  background-color: #f0f0f0;
  padding: 10px;
}
</style>
