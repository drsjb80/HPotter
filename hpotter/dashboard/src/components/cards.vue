<style scoped>
  .c-subtitle {
    position: relative;
    top: -10px;
  }

  .c-title {
    position: relative;
    top: 5px;
  }
  
</style>
<template>
  <v-container class="pt-0 mt-0">
    <v-layout row wrap>
      <v-flex xs3 v-for="kpi in kpis" :key="kpi.name">
        <v-card flat width="156" height="140" class="justify-center text-center ma-3">
          <v-icon size="45" class="pt-5">{{ kpi.icon }}</v-icon>
          <p class="headline c-title">{{ kpi.value }}</p>
          <p class="caption c-subtitle">{{ kpi.name }}</p>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
  

</template>


<script>
  export default {
    data() {
      return {
        kpis: [
          { name: 'Attacks', value: '128', icon: 'mdi-knife-military' },
          { name: 'Plug-ins', value: '13', icon: 'mdi-power-plug' },
          { name: 'Creds Used', value: '29', icon: 'mdi-lock-open-outline' }
        ]
      }
    }
  }
</script>