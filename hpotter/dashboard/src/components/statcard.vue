<style scoped>
  .c-subtitle {
    position: relative;
    top: -10px;
  }

  .c-title {
    position: relative;
    top: 5px;
  }

  .rounded-cards {
    border-radius: 2px;
  }

</style>

<template>
  <v-card width="156" height="140" class="justify-center text-center ma-2 elevation-3 rounded-cards">
    <v-icon size="45" class="pt-5">{{ icon }}</v-icon>
    <p class="headline c-title">{{ value }}</p>
    <p class="caption c-subtitle">{{ name }}</p>
  </v-card>
</template>


<script>
export default{
    props:['name', 'value', 'icon']
  }
</script>
