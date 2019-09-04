<template>
  <v-app>
    <v-app-bar app>
      <v-toolbar-title class="headline text-uppercase">
        <span>hpotter</span>
      </v-toolbar-title>
    </v-app-bar>

    <v-content>
      
    </v-content>
  </v-app>
</template>

<script>

export default {
  name: 'App',
  components: {
  },
  data: () => ({
    //
  }),

    created () {
      this.$vuetify.theme.dark = true
    },
};
</script>
