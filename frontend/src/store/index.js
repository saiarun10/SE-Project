import { createStore } from 'vuex';

const store = createStore({
  state() {
    return {
      access_token: null,
      role: null,
    };
  },
  mutations: {
    setToken(state, token) {
      state.access_token = token;
    },
    setRole(state, role) {
      state.role = role;
    },
  },
  actions: {
    login({ commit }, { token, role }) {
      commit('setToken', token);
      commit('setRole', role);
    },
  },
  getters: {
    isAuthenticated(state) {
      return !!state.access_token;
    },
    userRole(state) {
      return state.role;
    },
  },
});

export default store;