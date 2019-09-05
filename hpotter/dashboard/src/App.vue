<style>


</style>


<template>
  <v-app>

    <v-content>
      <br/>
      <cards :kpi="kpi"/>
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
      kpi: [
        { name: 'Attacks', value: '128', icon: 'mdi-knife-military' },
        { name: 'Plug-ins', value: '13', icon: 'mdi-power-plug' },
        { name: 'Creds Used', value: '29', icon: 'mdi-lock-open-outline' }
      ]
  }),

    created () {
      this.$vuetify.theme.dark = true
    },
};
</script>
