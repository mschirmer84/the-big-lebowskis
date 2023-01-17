import { createApp } from "vue";
import App from "./App.vue";

import "./assets/main.css";

const app = createApp(App);

fetch("config.json")
  .then((response) => response.json())
  .then((config) => {
    // either use window.config
    window.config = config
    // or use [Vue Global Config][1]
    app.config.globalProperties.config = config;
    // FINALLY, mount the app
    app.mount("#app");
  });
