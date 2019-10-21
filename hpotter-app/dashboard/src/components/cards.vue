<style scoped>
</style>


<template>
  <v-container class="pt-0 mt-0">
    <v-layout row wrap>
      <v-flex xs3 v-for="stat in kpi" :key="stat.id">
        <statcard :kpi="stat" v-on:update:content="$emit('update:content', stat.id)" :active="contentID == stat.id"/>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
  import statcard from './cards/statcard';

  export default {
    data() {
      return {

      }
    },
    components: {
      statcard,
    },
    created(){
      this.$emit('update:content', "1")
    },
    props:['kpi', 'contentID'],
  }
</script>
