<style scoped></style>
<template>
  <v-window :contentID="contentID" v-on:update:content="$emit('update:content')">
    <v-window-item v-if="contentID == 1">
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

    <v-window-item v-if="contentID == 2">
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

    <v-window-item v-if="contentID == 3">
      <v-card ma-2 class="elevation-3">
        <div> <!--Dummy Content -->
        Creds Used<br>
        S	A	T	O	R<br>
        A	R	E	P	O<br>
        T	E	N	E	T<br>
        O	P	E	R	A<br>
        R	O	T	A	S
        </div>
      </v-card>
    </v-window-item>

    <v-window-item v-if="contentID == 4">
      <v-card ma-2 class="elevation-3">
        <div> <!--Dummy Content -->
        Countries<br>
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
    props:['contentID']
  }
</script>
