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
                <v-list> <!-- TODO: CHange to Datatable! -->
                  <v-list-item v-for="vector in vectors" :key="vector.name">
                    <v-list-item-icon>
                      <v-btn fab depressed small color="#293245" class="title">{{ vector.number }}</v-btn>
                    </v-list-item-icon>
                    <v-list-item-content>
                      <v-list-item-title>{{ vector.name }}</v-list-item-title>
                      <v-list-item-subtitle>Port: {{ vector.port }}</v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                </v-list>
              </v-card-text>
            </v-card>
          </v-window-item>

          <v-window-item value='3'>
            <v-card>
              <v-card-title>Creds Used</v-card-title>
              <v-card-text>
                <!-- ToDo: List of pairs of most used credentials -->
              S	A	T	O	R<br>
              A	R	E	P	O<br>
              T	E	N	E	T<br>
              O	P	E	R	A<br>
              R	O	T	A	S
              </v-card-text>
            </v-card>
          </v-window-item>

          <v-window-item value='4'>
            <v-card>
              <v-card-title>Countries</v-card-title>
              <v-card-text>
                <!-- ToDo: Map of world, with pins for IPs who attacked -->
              S	A	T	O	R<br>
              A	R	E	P	O<br>
              T	E	N	E	T<br>
              O	P	E	R	A<br>
              R	O	T	A	S
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
