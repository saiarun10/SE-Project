import { createStore } from 'vuex';
import createPersistedState from 'vuex-persistedstate';

const store = createStore({
  state() {
    return {
      access_token: null,
      user: {
        user_id: null,
        email: null,
        username: null,
        user_role: null,
        parent_email: null,
      },
    };
  },
  mutations: {
    setAuthData(state, { access_token, user }) {
      state.access_token = access_token;
      state.user = {
        user_id: user.user_id,
        email: user.email,
        username: user.username,
        user_role: user.user_role,
        parent_email: user.parent_email,
      };
    },
    clearAuthData(state) {
      state.access_token = null;
      state.user = {
        user_id: null,
        email: null,
        username: null,
        user_role: null,
        parent_email: null,
      };
    },
  },
  actions: {
    login({ commit }, { access_token, user }) {
      commit('setAuthData', { access_token, user });
    },
    logout({ commit }) {
      commit('clearAuthData');
    },
  },
  getters: {
    isAuthenticated(state) {
      return !!state.access_token;
    },
    userRole(state) {
      return state.user.user_role;
    },
    user(state) {
      return state.user;
    },
  },
  plugins: [
    createPersistedState({
      storage: window.localStorage, // Persist state in localStorage
    }),
  ],
});

export default store;