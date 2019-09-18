<style scoped></style>
<template>
  <v-window v-model="content">
    <v-window-item :value="1">
      <v-card ma-2 class="elevation-3">
        <div> <!--Dummy Content -->
        Attacks<br>
        S	A	T	O	R<br>
        A	R	E	P	O<br>
        T	E	N	E	T<br>
        O	P	E	R	A<br>
        R	O	T	A	S
        </div>
      </v-card>
    </v-window-item>

    <v-window-item :value="2">
      <v-card ma-2 class="elevation-3">
        <div> <!--Dummy Content -->
        Plug-ins<br>
        S	A	T	O	R<br>
        A	R	E	P	O<br>
        T	E	N	E	T<br>
        O	P	E	R	A<br>
        R	O	T	A	S
        </div>
      </v-card>
    </v-window-item>
  </v-window>
</template>


<script>
  export default{
    props:['content']
  }
</script>
