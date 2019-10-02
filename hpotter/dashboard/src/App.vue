<style>
  .theme--dark.v-application {
    background: #2B3648 !important;
}
  .theme--dark.v-sheet {
  background-color: #212936 !important;
  border-color: #212936 !important;
}
  .slateNav {
    background-color: #212936 !important;
}
  .hiddenNav {
  background-color: rgba(0,0,0,0) !important;
}
  .theme--dark.v-picker__body{
  background: #212936 !important;
}
  .theme--dark.v-card {
    background-color: #212936 !important;
}
  .theme--dark.v-chip:not(.v-chip--active) {
  background: #293245;
}
</style>


<template>
  <v-app>
    <v-navigation-drawer floating app class="elevation-3 slateNav"><!--Left Sidebar-->
      <sideNavBar />
    </v-navigation-drawer> <!--End Sidebar-->
    <v-navigation-drawer floating right app width="300px" class="hiddenNav"><!--Right hand content-->
      <v-date-picker class="elevation-3 mt-8"></v-date-picker>
    </v-navigation-drawer>
    <v-content>
      <v-container ma-2>
        <v-row>
          <v-col> <!--Main Content-->

            <v-row>
              <cards v-on:update:content="updateContent($event)" :kpi="kpi" :contentID="contentID" />
            </v-row>

            <v-row>
              <drillDownWindow :contentID="contentID"/>
            </v-row>

        </v-col> <!--End Main Content-->
          <v-fab-transition><v-btn v-show="$vuetify.breakpoint.mdAndDown" fixed dark fab bottom right color="primary"><v-icon>mdi-calendar</v-icon></v-btn></v-fab-transition>
        </v-row>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>

import sideNavBar from './components/sideNavBar';
import cards from './components/cards';
import drillDownWindow from './components/drilldownwindow';

export default {



  name: 'App',
  components: {
    sideNavBar,
    cards,
    drillDownWindow
  },
  data: () => ({
    kpi: [
      { name: 'Attacks', value: '128', icon: 'mdi-knife-military', id: '1' },
      { name: 'Plug-ins', value: '13', icon: 'mdi-power-plug', id: '2' },
      { name: 'Creds Used', value: '29', icon: 'mdi-lock-open-outline', id: '3' },
      { name: 'Countries', value: '5', icon: 'mdi-map-marker', id: '4' }
    ],
    content: 1,
  }),
  methods: {
    updateContent(value) {
      return this.content = value
    }
  },
  computed: {
    contentID: {
      get: function () {
        return this.content
      },
      set: function () {
        this.contentID = this.content
      }
    }
  },

  created () {
    this.$vuetify.theme.dark = true
  },
};
</script>
