<style scoped>
</style>


<template>
  <v-container class="pt-0 mt-0">
    <v-layout row wrap>
      <v-flex xs3 v-for="stat in kpi" :key="stat.id">
        <statcard v-on:active="$emit('active', stat.id)" :kpi="stat"/>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
  import statcard from './statcard';

  export default {
    data() {
    },
    components: {
      statcard,
    },
    props:['kpi']
  }
</script>
