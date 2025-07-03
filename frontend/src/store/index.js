import { createStore } from 'vuex';
import axios from 'axios';

const BASE_URL = `${import.meta.env.VITE_BASE_URL}/api`;

export default createStore({
  state: {
    user: null, // Includes additional_claims (user_id, user_email, username, user_role, parent_email, is_premium_user)
    token: null,
  },
  getters: {
    isAuthenticated: (state) => !!state.token,
    userRole: (state) => state.user?.user_role || null,
    currentUser: (state) => state.user,
    userId: (state) => state.user?.user_id || null,
    userEmail: (state) => state.user?.user_email || null,
    username: (state) => state.user?.username || null,
    parentEmail: (state) => state.user?.parent_email || null,
    isPremiumUser: (state) => state.user?.is_premium_user || false,
  },
  mutations: {
    SET_USER(state, { user, token }) {
      state.user = user;
      state.token = token;
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      localStorage.setItem('user', JSON.stringify(user));
      localStorage.setItem('token', token);
    },
    CLEAR_USER(state) {
      state.user = null;
      state.token = null;
      delete axios.defaults.headers.common['Authorization'];
      localStorage.removeItem('user');
      localStorage.removeItem('token');
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
    async initializeAuth({ commit }) {
      const token = localStorage.getItem('token');
      const user = localStorage.getItem('user');
      if (token && user) {
        try {
          await axios.get(`${BASE_URL}/validate-token`, {
            headers: { Authorization: `Bearer ${token}` },
          });
          commit('SET_USER', { user: JSON.parse(user), token });
        } catch (error) {
          console.error('Token validation failed:', error);
          commit('CLEAR_USER');
        }
      }
    },
  },
});