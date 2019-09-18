<style>
  .v-picker__title{
    background-color: #FFB300;
  }

</style>


<template>
  <v-app>
    <v-navigation-drawer app class="elevation-3"> <!--Sidebar-->
    </v-navigation-drawer> <!--End Sidebar-->
    <v-content>
      <v-container ma-2>
        <v-row>
          <v-col> <!--Main Content-->

            <v-row>
              <cards v-on:active="content = 1" :kpi="kpi"/>
            </v-row>

            <v-row>
              <drillDownWindow :content="content"/>
            </v-row>

        </v-col> <!--End Main Content-->

          <v-col cols="4" class="d-none d-lg-block"> <!--Right Bar-->

            <v-date-picker class="elevation-3"></v-date-picker>

          </v-col> <!--End Right Bar-->

          <div class="d-lg-none"><v-btn fixed dark fab bottom right color="primary"><v-icon>mdi-calendar</v-icon></v-btn></div>
        </v-row>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>

import cards from './components/cards';
import drillDownWindow from './components/drilldownwindow';

export default {



  name: 'App',
  components: {
    cards,
    drillDownWindow
  },
  data: () => ({
      kpi: [
        { name: 'Attacks', value: '128', icon: 'mdi-knife-military' },
        { name: 'Plug-ins', value: '13', icon: 'mdi-power-plug' },
        { name: 'Creds Used', value: '29', icon: 'mdi-lock-open-outline' },
        { name: 'Countries', value: '5', icon: 'mdi-map-marker' }
      ],
      content: 2
  }),

    created () {
      this.$vuetify.theme.dark = true
    },
};
</script>
