<style>
  .v-picker__title{
    background-color: #FFB300;
  }

</style>


<template>
  <v-app>
    <v-navigation-drawer app>
    </v-navigation-drawer>
    <v-content>
      <v-container>
        <v-row>
          <v-col><cards :kpi="kpi"/></v-col>
          <v-col cols="4" class="d-none d-lg-block"><v-date-picker></v-date-picker></v-col>
          <div class="d-lg-none"><v-btn fixed dark fab bottom right color="primary"><v-icon>mdi-calendar</v-icon></v-btn></div>
        </v-row>
      </v-container>
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
        { name: 'Creds Used', value: '29', icon: 'mdi-lock-open-outline' },
        { name: 'Countries', value: '5', icon: 'mdi-map-marker' }
      ]
  }),

    created () {
      this.$vuetify.theme.dark = true
    },
};
</script>
