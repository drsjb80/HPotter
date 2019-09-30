import '@mdi/font/css/materialdesignicons.css'
import Vue from 'vue';
import Vuetify from 'vuetify/lib';


Vue.use(Vuetify);

export default new Vuetify({
  icons: {
    iconfont: 'mdi',
  },
  theme: {
    themes: {
      dark: {
        primary: '#FFB300',
        secondary: '#FADF63',
        accent: '#FFB300'
      },
    },
  },
});
