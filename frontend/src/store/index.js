import { createStore } from 'vuex'

export default createStore({
  state: {
    access_token: null,
    refresh_token: null,
    role: null
  },
  mutations: {
    setAuth(state, { access, refresh, role }) {
      state.access_token = access
      state.refresh_token = refresh
      state.role = role
    },
    clearAuth(state) {
      state.access_token = null
      state.refresh_token = null
      state.role = null
    }
  }
})
