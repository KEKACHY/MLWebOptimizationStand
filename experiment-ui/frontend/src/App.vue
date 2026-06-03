<template>
  <div class="page">
    <header class="header">
      <div>
        <h1>Экспериментальный стенд ВКР</h1>
        <p>Панель управления нагрузочным тестированием</p>
      </div>

      <div class="status-pill" :class="{ active: status.is_running }">
        {{ status.is_running ? "Нагрузка активна" : "Нагрузка остановлена" }}
      </div>
    </header>

    <section class="scenarios">
      <div
        v-for="(scenario, key) in scenarios"
        :key="key"
        class="scenario-card"
        :class="{
          selected: selectedScenario === key,
          disabled: !scenario.available
        }"
        @click="selectScenario(key)"
      >
        <div class="scenario-title">
          <h2>{{ scenario.title }}</h2>
          <span v-if="scenario.available" class="badge ready">Доступен</span>
          <span v-else class="badge disabled">Не доступен</span>
        </div>

        <p>{{ scenario.description }}</p>
      </div>
    </section>

    <section class="control-panel">
      <div>
        <h2>Управление экспериментом</h2>
        <p>
          Выбранный сценарий:
          <strong>{{ scenarios[selectedScenario]?.title || "—" }}</strong>
        </p>
        <p class="profile">
          Профиль нагрузки: циклический рост до 150 пользователей, удержание,
          спад и повтор.
        </p>
      </div>

      <button
        class="main-button"
        :class="{ stop: status.is_running }"
        :disabled="!scenarios[selectedScenario]?.available"
        @click="toggleLoad"
      >
        {{ status.is_running ? "Остановить нагрузку" : "Запустить нагрузку" }}
      </button>
    </section>

    <section class="metrics-grid">
      <div class="metric-card">
        <span>p95 latency</span>
        <strong>{{ metricValue("p95") }} мс</strong>
      </div>

      <div class="metric-card">
        <span>p99 latency</span>
        <strong>{{ metricValue("p99") }} мс</strong>
      </div>

      <div class="metric-card">
        <span>Throughput</span>
        <strong>{{ metricValue("rps") }} TPS</strong>
      </div>

      <div class="metric-card">
        <span>Ошибки</span>
        <strong>{{ metricValue("failures") }}</strong>
      </div>

      <div class="metric-card">
        <span>Среднее время ответа</span>
        <strong>{{ metricValue("avg_response_time") }} мс</strong>
      </div>

      <div class="metric-card">
        <span>Backend-реплики</span>
        <strong>1</strong>
      </div>
    </section>

    <section class="charts">
      <div class="chart-card">
        <h3>p95 / p99 latency</h3>
        <div ref="latencyChart" class="chart"></div>
      </div>

      <div class="chart-card">
        <h3>Throughput</h3>
        <div ref="throughputChart" class="chart"></div>
      </div>
    </section>

    <section class="download-section">
      <button class="download-button" @click="downloadResults">
        Скачать результаты
      </button>
    </section>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, nextTick } from "vue";
import * as echarts from "echarts";

const apiBase = `http://${window.location.hostname}:7000`;

const scenarios = ref({});
const selectedScenario = ref("baseline");

const status = ref({
  is_running: false,
  active_scenario: null
});

const metrics = ref({
  stats: null,
  history: []
});

const latencyChart = ref(null);
const throughputChart = ref(null);

let latencyChartInstance = null;
let throughputChartInstance = null;
let intervalId = null;

function selectScenario(key) {
  if (!scenarios.value[key]?.available) {
    return;
  }

  selectedScenario.value = key;
}

function metricValue(key) {
  if (!metrics.value.stats) {
    return "—";
  }

  const value = metrics.value.stats[key];

  if (value === undefined || value === null) {
    return "—";
  }

  return value;
}

async function fetchScenarios() {
  const response = await fetch(`${apiBase}/api/scenarios`);
  const data = await response.json();

  scenarios.value = data.scenarios;
  status.value.is_running = data.is_running;
  status.value.active_scenario = data.active_scenario;
}

async function fetchStatus() {
  const response = await fetch(`${apiBase}/api/load/status`);
  const data = await response.json();

  status.value = data;
}

async function fetchMetrics() {
  const response = await fetch(`${apiBase}/api/metrics`);
  const data = await response.json();

  metrics.value = data;

  await nextTick();
  renderCharts();
}

async function toggleLoad() {
  if (status.value.is_running) {
    await fetch(`${apiBase}/api/load/stop`, {
      method: "POST"
    });
  } else {
    await fetch(`${apiBase}/api/load/start/${selectedScenario.value}`, {
      method: "POST"
    });
  }

  await fetchStatus();
  await fetchMetrics();
}

function downloadResults() {
  window.location.href = `${apiBase}/api/results/download`;
}

function renderCharts() {
  const history = metrics.value.history || [];

  const labels = history.map((item, index) => index + 1);
  const p95 = history.map(item => item.p95);
  const p99 = history.map(item => item.p99);
  const rps = history.map(item => item.rps);

  if (latencyChart.value) {
    if (!latencyChartInstance) {
      latencyChartInstance = echarts.init(latencyChart.value);
    }

    latencyChartInstance.setOption({
      tooltip: { trigger: "axis" },
      legend: { data: ["p95", "p99"] },
      xAxis: { type: "category", data: labels },
      yAxis: { type: "value" },
      series: [
        { name: "p95", type: "line", smooth: true, data: p95 },
        { name: "p99", type: "line", smooth: true, data: p99 }
      ]
    });
  }

  if (throughputChart.value) {
    if (!throughputChartInstance) {
      throughputChartInstance = echarts.init(throughputChart.value);
    }

    throughputChartInstance.setOption({
      tooltip: { trigger: "axis" },
      legend: { data: ["TPS"] },
      xAxis: { type: "category", data: labels },
      yAxis: { type: "value" },
      series: [
        { name: "TPS", type: "line", smooth: true, data: rps }
      ]
    });
  }
}

onMounted(async () => {
  await fetchScenarios();
  await fetchStatus();
  await fetchMetrics();

  intervalId = setInterval(async () => {
    await fetchStatus();
    await fetchMetrics();
  }, 3000);
});

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId);
  }
});
</script>

<style>
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: #0f172a;
  color: #e5e7eb;
  font-family: Arial, sans-serif;
}

.page {
  max-width: 1320px;
  margin: 0 auto;
  padding: 32px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.header h1 {
  margin: 0 0 8px;
  font-size: 36px;
}

.header p {
  margin: 0;
  color: #94a3b8;
}

.status-pill {
  padding: 12px 18px;
  border-radius: 999px;
  background: #334155;
  color: #cbd5e1;
  font-weight: 600;
}

.status-pill.active {
  background: #14532d;
  color: #bbf7d0;
}

.scenarios {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
  margin-bottom: 24px;
}

.scenario-card {
  padding: 22px;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 20px;
  cursor: pointer;
  transition: 0.2s;
}

.scenario-card:hover {
  transform: translateY(-2px);
  border-color: #38bdf8;
}

.scenario-card.selected {
  border-color: #38bdf8;
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.25);
}

.scenario-card.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.scenario-card.disabled:hover {
  transform: none;
  border-color: #334155;
}

.scenario-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.scenario-card h2 {
  margin: 0;
}

.scenario-card p {
  color: #94a3b8;
  line-height: 1.5;
}

.badge {
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.badge.ready {
  background: #0f766e;
  color: #ccfbf1;
}

.badge.disabled {
  background: #475569;
  color: #cbd5e1;
}

.control-panel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #111827;
  border: 1px solid #374151;
  border-radius: 22px;
  padding: 24px;
  margin-bottom: 24px;
}

.profile {
  color: #94a3b8;
}

.main-button {
  border: none;
  border-radius: 16px;
  padding: 18px 28px;
  background: #2563eb;
  color: white;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  min-width: 220px;
}

.main-button:hover {
  background: #1d4ed8;
}

.main-button.stop {
  background: #dc2626;
}

.main-button.stop:hover {
  background: #b91c1c;
}

.main-button:disabled {
  background: #475569;
  cursor: not-allowed;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 14px;
  margin-bottom: 24px;
}

.metric-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 18px;
  padding: 18px;
}

.metric-card span {
  display: block;
  color: #94a3b8;
  font-size: 13px;
  margin-bottom: 10px;
}

.metric-card strong {
  font-size: 22px;
}

.charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

.chart-card {
  background: #f8fafc;
  color: #0f172a;
  border-radius: 22px;
  padding: 20px;
}

.chart-card h3 {
  margin-top: 0;
}

.chart {
  height: 340px;
}

.download-section {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

.download-button {
  padding: 14px 22px;
  border-radius: 14px;
  border: 1px solid #38bdf8;
  background: transparent;
  color: #e0f2fe;
  font-weight: 700;
  cursor: pointer;
}

.download-button:hover {
  background: rgba(56, 189, 248, 0.12);
}
</style>