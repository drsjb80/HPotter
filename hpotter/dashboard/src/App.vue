<style>


</style>


<template>
  <v-app>

    <v-content>
      <br/>
      <cards/>
    </v-content>
  </v-app>
</template>

<script>

import cards from './components/cards';

export default {

  

  name: 'App',
  components: {
    cards,
  },
  data: () => ({
    //
  }),

    created () {
      this.$vuetify.theme.dark = true
    },
};
</script>
