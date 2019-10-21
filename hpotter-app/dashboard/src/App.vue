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
      <sideNavBar v-on:update:window="updateWindow($event)"/>
    </v-navigation-drawer> <!--End Sidebar-->
    <v-navigation-drawer floating right app width="300px" class="hiddenNav"><!--Right hand content-->
      <div class="mt-8">
        <v-date-picker v-model="viewDate"></v-date-picker>
      </div>
      <br /> <!-- Space with CSS -->
      <v-card class="mr-2 text-center">
        <v-card-title>
        Activity
        </v-card-title>
        <v-card-text>
          <v-sparkline :value="weekData" :labels='labelsWeek' line-width="10"  stroke-linecap='round' type='bars' show-labels smooth auto-draw></v-sparkline>
        </v-card-text>
      </v-card>
    </v-navigation-drawer>
    <v-content>
      <v-container ma-2>
        <v-row>
          <v-col>
            <v-window v-model='window'> <!--Main Content-->

              <!--Dashboard-->
              <v-window-item>
                <v-row>
                  <cards v-on:update:content="updateContent($event)" :kpi="kpi" :contentID="contentID" />
                </v-row>

                <v-row>
                  <drillDownWindow :contentID="contentID" :valueAttacks="valueAttacks" :labelsAttacks="labelsAttacks" :vectors="vectors"/>
                </v-row>
              </v-window-item>


              <!--Analytics-->
              <v-window-item>
                <v-card>
                  <v-card-text>
                    Analytics Here
                  </v-card-text>
                </v-card>
              </v-window-item>


            </v-window> <!--End Main Content-->
          </v-col>
          <v-dialog v-model="dialog" width="300">
            <template v-slot:activator="{ on }">
              <v-fab-transition><v-btn v-on="on" v-show="$vuetify.breakpoint.mdAndDown" fixed dark fab bottom right color="primary"><v-icon>mdi-calendar</v-icon></v-btn></v-fab-transition>
            </template>
            <v-date-picker v-model="viewDate"></v-date-picker>
          </v-dialog>
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
    window: 0,
    kpi: [
      { name: 'Attacks', value: '128', icon: 'mdi-knife-military', id: '1' },
      { name: 'Attack Vectors', value: '6', icon: 'mdi-directions-fork', id: '2' },
      { name: 'Creds Used', value: '29', icon: 'mdi-lock-open-outline', id: '3' },
      { name: 'Countries', value: '5', icon: 'mdi-map-marker', id: '4' }
    ],
    viewDate: new Date().toISOString().substr(0, 10),
    content: 1,
    weekData: [7, 6, 4, 9, 8, 10, 1],
    labelsWeek: [
      'Mon',
      'Tue',
      'Wed',
      'Thu',
      'Fri',
      'Sat',
      'Sun',
    ],

      valueAttacks: [0, 2, 5, 9, 5, 10, 0, 5],
      labelsAttacks: [
        '12am',
        '3am',
        '6am',
        '9am',
        '12pm',
        '3pm',
        '6pm',
        '9pm',
      ],
      vectors: [
        { name: 'Telnet', port: 23, number: 3 },
        { name: 'ssh', port: 22, number: 7 },
        { name: 'Maria', port: 3306, number: 2 },
        { name: 'http', port: 22, number: 0 },
        { name: 'https', port: 443, number: 18 },
        { name: 'maria_tls', port: 99, number: 4 }
      ],
  }),
  methods: {
    updateContent(value) {
      return this.content = value
    },
    updateWindow(value) {
      return this.window = value
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
