<style scoped>
</style>
<template>
  <v-container>
    <v-layout row wrap ma-2>
      <v-flex>
        <v-window v-bind:value="contentID">
          <v-window-item value="1">
            <v-card>
              <v-card-title>Attacks</v-card-title>
              <v-card-text>
              S	A	T	O	R<br>
              A	R	E	P	O<br>
              T	E	N	E	T<br>
              O	P	E	R	A<br>
              R	O	T	A	S
              </v-card-text>
              <v-card-actions>
                <v-chip-group color="primary" mandatory>
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

          <v-window-item value="2">
            <v-card>
              <v-card-title>Plug-ins</v-card-title>
              <v-card-text>
              S	A	T	O	R<br>
              A	R	E	P	O<br>
              T	E	N	E	T<br>
              O	P	E	R	A<br>
              R	O	T	A	S
              </v-card-text>
            </v-card>
          </v-window-item>

          <v-window-item value="3">
            <v-card>
              <v-card-title>Creds Used</v-card-title>
              <v-card-text>
              S	A	T	O	R<br>
              A	R	E	P	O<br>
              T	E	N	E	T<br>
              O	P	E	R	A<br>
              R	O	T	A	S
              </v-card-text>
            </v-card>
          </v-window-item>

          <v-window-item value="4">
            <v-card>
              <v-card-title>Countries</v-card-title>
              <v-card-text>
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
    }),
    props:['contentID']
  }
</script>
