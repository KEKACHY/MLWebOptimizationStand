import { createRouter, createWebHistory } from "vue-router";

import HomeView from "@/views/HomeView.vue";
import Glossary from "@/components/Glossary.vue";
import SemanticGraph from "@/components/SemanticGraph.vue";

const routes = [
  {
    path: "/",
    component: HomeView,
    children: [
      {
        path: "",
        name: "Glossary",
        component: Glossary
      },
      {
        path: "graph",
        name: "SemanticGraph",
        component: SemanticGraph
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;