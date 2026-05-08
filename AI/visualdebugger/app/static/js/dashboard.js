/**
 * dashboard.js — Charts and dashboard interactions
 */

const CHART_COLORS = {
  cyan:   '#00d4ff', purple: '#7c3aed', green:  '#10b981',
  orange: '#f59e0b', red:    '#ef4444', blue:   '#3b82f6',
};
const BUG_TYPE_COLORS = [
  CHART_COLORS.red, CHART_COLORS.orange, CHART_COLORS.purple,
  CHART_COLORS.cyan, CHART_COLORS.blue, CHART_COLORS.green,
];
const chartDefaults = {
  font: { family: 'Inter, system-ui, sans-serif', size: 12 },
  color: '#94a3b8',
};

Chart.defaults.font = chartDefaults.font;
Chart.defaults.color = chartDefaults.color;

function initDashboard(bugTypeData, timeSeriesData, severityData) {
  initBugTypeChart(bugTypeData);
  initTimelineChart(timeSeriesData);
  initSeverityChart(severityData);
}

// ── Bug Type Doughnut ─────────────────────────────────────────────────────
function initBugTypeChart(data) {
  const ctx = document.getElementById('bugTypeChart');
  if (!ctx || !data.length) return;

  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: data.map(d => d.bug_type.charAt(0).toUpperCase() + d.bug_type.slice(1)),
      datasets: [{
        data: data.map(d => d.cnt),
        backgroundColor: BUG_TYPE_COLORS.map(c => c + '30'),
        borderColor: BUG_TYPE_COLORS,
        borderWidth: 2,
        hoverOffset: 8,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      cutout: '68%',
      plugins: {
        legend: {
          position: 'right',
          labels: { boxWidth: 12, padding: 16, font: { size: 12 } },
        },
        tooltip: {
          backgroundColor: '#131d2e',
          borderColor: '#1e2d45',
          borderWidth: 1,
          padding: 12,
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ${ctx.raw} bugs`,
          },
        },
      },
    },
  });
}

// ── Timeline Line Chart ────────────────────────────────────────────────────
function initTimelineChart(data) {
  const ctx = document.getElementById('timelineChart');
  if (!ctx) return;

  // If no data, generate demo data
  const labels = data.length ? data.map(d => d.d) : generateDateLabels(14);
  const values = data.length ? data.map(d => d.c) : generateDemoValues(14);

  new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Bugs Found',
        data: values,
        borderColor: CHART_COLORS.cyan,
        backgroundColor: 'rgba(0,212,255,0.08)',
        borderWidth: 2,
        pointRadius: 4,
        pointBackgroundColor: CHART_COLORS.cyan,
        pointBorderColor: '#0d1424',
        pointBorderWidth: 2,
        fill: true,
        tension: 0.4,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      scales: {
        x: {
          grid: { color: 'rgba(30,45,69,0.6)' },
          ticks: { maxTicksLimit: 8 },
        },
        y: {
          grid: { color: 'rgba(30,45,69,0.6)' },
          beginAtZero: true,
          ticks: { stepSize: 1 },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#131d2e',
          borderColor: '#1e2d45',
          borderWidth: 1,
          padding: 10,
        },
      },
    },
  });
}

// ── Severity Doughnut ─────────────────────────────────────────────────────
function initSeverityChart(data) {
  const ctx = document.getElementById('severityChart');
  if (!ctx || !data.length) return;

  const SCOLORS = {
    critical: CHART_COLORS.red,
    high:     CHART_COLORS.orange,
    medium:   '#d97706',
    low:      CHART_COLORS.green,
  };
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: data.map(d => d.severity.charAt(0).toUpperCase() + d.severity.slice(1)),
      datasets: [{
        data: data.map(d => d.cnt),
        backgroundColor: data.map(d => (SCOLORS[d.severity] || '#64748b') + '30'),
        borderColor: data.map(d => SCOLORS[d.severity] || '#64748b'),
        borderWidth: 2,
        hoverOffset: 6,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      cutout: '65%',
      plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 10, padding: 12, font: { size: 11 } } },
        tooltip: {
          backgroundColor: '#131d2e', borderColor: '#1e2d45', borderWidth: 1, padding: 10,
        },
      },
    },
  });
}

// ── Model Metrics Line Charts ─────────────────────────────────────────────
function initModelMetricsCharts(metrics) {
  if (!metrics || !metrics.length) return;
  const epochs = metrics.map(m => `E${m.epoch}`);

  // Accuracy Chart
  const accCtx = document.getElementById('accChart');
  if (accCtx) {
    new Chart(accCtx, {
      type: 'line',
      data: {
        labels: epochs,
        datasets: [
          { label: 'Train Acc', data: metrics.map(m => +(m.train_acc * 100).toFixed(2)), borderColor: CHART_COLORS.cyan, backgroundColor: 'rgba(0,212,255,0.1)', borderWidth: 2, fill: true, tension: 0.4, pointRadius: 3 },
          { label: 'Val Acc',   data: metrics.map(m => +(m.val_acc * 100).toFixed(2)),   borderColor: CHART_COLORS.purple, backgroundColor: 'rgba(124,58,237,0.08)', borderWidth: 2, fill: true, tension: 0.4, pointRadius: 3 },
        ],
      },
      options: { responsive: true, scales: { x: { grid: { color: 'rgba(30,45,69,0.6)' } }, y: { grid: { color: 'rgba(30,45,69,0.6)' }, min: 50, max: 100, ticks: { callback: v => v + '%' } } }, plugins: { legend: { position: 'top', labels: { boxWidth: 12, padding: 14 } }, tooltip: { backgroundColor: '#131d2e', borderColor: '#1e2d45', borderWidth: 1, padding: 10 } } },
    });
  }

  // Loss Chart
  const lossCtx = document.getElementById('lossChart');
  if (lossCtx) {
    new Chart(lossCtx, {
      type: 'line',
      data: {
        labels: epochs,
        datasets: [
          { label: 'Train Loss', data: metrics.map(m => +m.train_loss.toFixed(4)), borderColor: CHART_COLORS.red,   backgroundColor: 'rgba(239,68,68,0.08)', borderWidth: 2, fill: true, tension: 0.4, pointRadius: 3 },
          { label: 'Val Loss',   data: metrics.map(m => +m.val_loss.toFixed(4)),   borderColor: CHART_COLORS.orange, backgroundColor: 'rgba(245,158,11,0.08)', borderWidth: 2, fill: true, tension: 0.4, pointRadius: 3 },
        ],
      },
      options: { responsive: true, scales: { x: { grid: { color: 'rgba(30,45,69,0.6)' } }, y: { grid: { color: 'rgba(30,45,69,0.6)' }, beginAtZero: true } }, plugins: { legend: { position: 'top', labels: { boxWidth: 12, padding: 14 } }, tooltip: { backgroundColor: '#131d2e', borderColor: '#1e2d45', borderWidth: 1, padding: 10 } } },
    });
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────
function generateDateLabels(n) {
  return Array.from({ length: n }, (_, i) => {
    const d = new Date(); d.setDate(d.getDate() - (n - 1 - i));
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  });
}
function generateDemoValues(n) {
  return Array.from({ length: n }, () => Math.floor(Math.random() * 8) + 1);
}
