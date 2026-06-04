<template>
  <DefaultLayout>
    <section class="graph-page">
      <div ref="graph" class="graph"></div>
    </section>
  </DefaultLayout>
</template>

<script setup>
import { onMounted, ref } from "vue";
import cytoscape from "cytoscape";
import fcose from "cytoscape-fcose";
import { apiUrl } from "../utils/apiBase";

cytoscape.use(fcose);

const graph = ref(null);

onMounted(async () => {
  try {
    const glossaries = await fetch(apiUrl("/glossaries/"))
      .then(r => r.json());

    const relations = await fetch(apiUrl("/glossaries/relations/"))
      .then(r => r.json());

    const nodesMap = new Map();

    glossaries.forEach(t => {
      nodesMap.set(t.keyword, {
        data: {
          id: t.keyword,
          label: t.keyword,
          description: t.description,
          score: t.keyword.length
        }
      });
    });

    relations.forEach(r => {
      if (!nodesMap.has(r.source)) {
        nodesMap.set(r.source, {
          data: { id: r.source, label: r.source }
        });
      }
      if (!nodesMap.has(r.target)) {
        nodesMap.set(r.target, {
          data: { id: r.target, label: r.target }
        });
      }
    });

    const nodes = Array.from(nodesMap.values());

    const edges = relations.map(r => ({
      data: {
        source: r.source,
        target: r.target,
        label: r.type
      }
    }));

    const cy = cytoscape({
      container: graph.value,
      elements: [...nodes, ...edges],
      nodeDimensionsIncludeLabels: true,

      layout: {
        name: "fcose",
        nodeSeparation: 60,
        idealEdgeLength: 70,
        gravity: 0.2,
        animate: true
      },

      style: [
        {
          selector: "node",
          style: {
            "shape": "ellipse",
            "padding": "12px",
            "width": "mapData(score, 1, 20, 40, 120)",
            "height": "mapData(score, 1, 20, 40, 120)",
            "background-fill": "linear-gradient",
            "background-gradient-stop-colors": "#A8D5BA #CDE7F0",
            "background-gradient-stop-positions": "0 100",

            "border-width": 2,
            "border-color": "#c89fb1",

            "label": "data(label)",
            "font-family": "Nunito, Roboto, Arial, sans-serif",
            "font-size": 13,
            "font-weight": 500,
            "color": "#25665e",

            "text-valign": "center",
            "text-halign": "center",

            "text-wrap": "wrap",
            "text-max-width": 120
          }
        },

        {
          selector: ".hovered",
          style: {
            "border-color": "#25665e",
            "border-width": 3,
            "font-size": 14
          }
        },

        {
          selector: ".root",
          style: {
            "background-gradient-stop-colors": "#F6C1CC #FBE4EA",
            "color": "#7A2E3A",
            "font-size": 16
          }
        },

        {
          selector: "edge",
          style: {
            "curve-style": "bezier",
            "line-color": "#c89fb1",
            "width": 1.2,

            "label": "data(label)",
            "font-family": "Nunito, sans-serif",
            "font-size": 9,
            "color": "#8a6b7a",

            "text-background-color": "#FFF8F0",
            "text-background-opacity": 1,
            "text-background-padding": "3px",
            "text-background-shape": "round-rectangle"
          }
        },

        {
          selector: 'edge[label = "narrower"]',
          style: {
            "target-arrow-shape": "triangle",
            "target-arrow-color": "#c89fb1"
          }
        },
        {
          selector: 'edge[label = "related"]',
          style: {
            "line-style": "dashed",
            "target-arrow-shape": "none",
            "opacity": 0.7
          }
        }
      ]
    });

    if (cy.getElementById("ВКР").length) {
      cy.getElementById("ВКР").addClass("root");
    }

    cy.on("tap", "node", evt => {
      const { label, description } = evt.target.data();
      if (description) {
        alert(`${label}\n\n${description}`);
      }
    });

    cy.on("mouseover", "node", e => e.target.addClass("hovered"));
    cy.on("mouseout", "node", e => e.target.removeClass("hovered"));
    
  } catch (err) {
    console.error("Ошибка загрузки графа:", err);
  }
});
</script>

<style lang="scss" scoped>
@use '@/assets/styles/graph.scss' as *;
</style>