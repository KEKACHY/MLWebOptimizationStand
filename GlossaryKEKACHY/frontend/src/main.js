import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import DefaultLayout from "@/layouts/DefaultLayout.vue";

const app = createApp(App);

app.component("DefaultLayout", DefaultLayout);
app.use(router);

app.mount("#app");