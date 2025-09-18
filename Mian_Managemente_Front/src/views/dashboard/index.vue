<template>
  <div class="dashboard-container">
    <component :is="currentRole" />
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import adminDashboard from './admin'
import editorDashboard from './editor'

export default {
  name: 'Dashboard',
  components: { adminDashboard, editorDashboard },
  data() {
    return {
      currentRole: 'adminDashboard'
    }
  },
  computed: {
    ...mapGetters([
      'roles'
    ])
  },
  created() {
    var contant = false
    this.roles.forEach(element => {
      element.NAME === 'admin' ? contant = true : false
    })

    contant ? this.currentRole = 'adminDashboard' : this.currentRole = 'editorDashboard'
  }
}
</script>
