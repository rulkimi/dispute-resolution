<template>
  <div class="flex justify-center items-center h-screen">
    <div class="text-center">
      <h1 class="text-3xl font-bold mb-4 text-primary">Welcome to Deriv Dispute Resolution Demo</h1>
      <p class="text-lg mb-8 text-primary">Please select your role:</p>
      <div class="flex justify-center space-x-4">
        <router-link to="/buyer" class="bg-primary hover:bg-primary-dark text-white font-bold py-2 px-4 rounded">
          Buyer
        </router-link>
        <router-link to="/seller" class="bg-primary hover:bg-primary-dark text-white font-bold py-2 px-4 rounded">
          Seller
        </router-link>
      </div>
    </div>
  </div>
</template>