<style scoped>
</style>
<template>
  <v-container>
    <v-layout row wrap ma-2>
      <v-flex>
        <v-window v-bind:value='contentID'>
          <v-window-item value='1'>
            <v-card class="mx-auto text-center">
              <v-card-text>
                <div class="display-1 font-weight-thin">Attacks Last 24h</div>
              </v-card-text>
              <v-card-text>
                <v-sparkline
    :value='valueAttacks' :labels='labelsAttacks' color='white' stroke-linecap='round' show-labels smooth auto-draw></v-sparkline>
              </v-card-text>
              <v-divider></v-divider>
              <v-card-actions>
                <v-chip-group color='primary' mandatory>
                  <v-chip>
                    Past Day
                  </v-chip>
                  <v-chip>
                    Past Hour
                  </v-chip>
                  <v-chip>
                    Past Minute
                  </v-chip>
                  <v-chip>
                    Past Second
                  </v-chip>
                </v-chip-group>
              </v-card-actions>
            </v-card>
          </v-window-item>

          <v-window-item value='2'>
            <v-card class="mx-auto">
              <v-card-text>
                <div class="display-1 font-weight-thin  text-center">Attack Vectors</div>
              </v-card-text>
              <v-card-text>
                <!-- TODO: CHange to Datatable, probably convert each one to a componant, this is getting a lot. -->
              </v-card-text>
            </v-card>
          </v-window-item>

          <v-window-item value='3'>
            <v-card>
              <v-card-text>
              </v-card-text>
            </v-card>
          </v-window-item>

          <v-window-item value='4'>
            <v-card>
              <v-card-text>
              </v-card-text>
            </v-card>
          </v-window-item>
        </v-window>
      </v-flex>
    </v-layout>
  </v-container>
</template>


<script>
  export default{
    data: () => ({
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
    props:['contentID']
  }
</script>
