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
  <v-card width="156" height="140" v-on:click="$emit('update:content', kpi.id)" class="justify-center text-center ma-2 elevation-3 rounded-cards pt-0 mt-0">
    <v-icon size="45" class="pt-5">{{ kpi.icon }}</v-icon>
    <p class="headline c-title">{{ kpi.value }}</p>
    <p class="caption c-subtitle">{{ kpi.name }}</p>
  </v-card>
</template>


<script>
export default{
    props:['kpi', 'content']
  }
</script>
