p,<style scoped>
  .titleDrip {
    position: absolute;
    left: 170px;
    top: 85px;
    z-index: 4;
  }
</style>
<template>
  <div>
    <v-list nav color="primary">
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title class="title">
            <v-img src="../assets/LogoTextWhite.png"></v-img>
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </v-list>

    <div class="titleDrip">
      <v-img max-width="80" src="../assets/dripnav.png"></v-img>
    </div>

    <v-list>
      <v-list-item-group v-model="item" color="white">
        <v-list-item
          v-for="(item, i) in items"
          :key="i">
          <v-list-item-icon>
            <v-icon v-text="item.icon"></v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title v-text="item.text"></v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list-item-group>
    </v-list>
  </div>
</template>


<script>
  export default {
      data: () => ({
        items: [
          {
            icon: 'mdi-view-dashboard',
            text: 'Dashboard',
          },
          {
            icon: 'mdi-pencil',
            text: 'Management',
          },
          {
            icon: 'mdi-settings',
            text: 'Settings',
          },
        ],
        item: 0,
      }),
    }
</script>
