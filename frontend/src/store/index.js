import { createStore } from 'vuex';
import axios from 'axios';

const BASE_URL = `${import.meta.env.VITE_BASE_URL}/api`;

export default createStore({
  state: {
    user: null,
    token: null,
  },
  getters: {
    isAuthenticated: (state) => !!state.token,
    userRole: (state) => state.user?.user_role || null,
    currentUser: (state) => state.user,
  },
  mutations: {
    SET_USER(state, { user, token }) {
      state.user = user;
      state.token = token;
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    },
    CLEAR_USER(state) {
      state.user = null;
      state.token = null;
      delete axios.defaults.headers.common['Authorization'];
    },
  },
  actions: {
    async login({ commit }, { token, user }) {
      commit('SET_USER', { user, token });
    },
    async logout({ commit }) {
      try {
        await axios.post(`${BASE_URL}/logout`);
        commit('CLEAR_USER');
      } catch (error) {
        console.error('Logout failed:', error);
      }
    },
  },
});