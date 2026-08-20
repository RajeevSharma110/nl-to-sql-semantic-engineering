const $ = (selector) => document.querySelector(selector);
const form = $("#query-form");
const question = $("#question");
const resultSection = $("#result-section");
const toast = $("#toast");
let latestSql = "";

function notify(message, error = false) {
  toast.textContent = message;
  toast.className = `toast show${error ? " error" : ""}`;
  window.setTimeout(() => { toast.className = "toast"; }, 3600);
}

function prettyName(value) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

async function requestJson(url, options) {
  const response = await fetch(url, options);
  const payload = await response.json();
  if (!response.ok) {
    const detail = payload.detail;
    throw new Error(typeof detail === "object" ? detail.message : detail || "Request failed");
  }
  return payload;
}

async function loadHealth() {
  const pill = $("#health-pill");
  try {
    await requestJson("/health");
    pill.querySelector("span:last-child").textContent = "API + PostgreSQL ready";
  } catch {
    pill.classList.add("offline");
    pill.querySelector("span:last-child").textContent = "Service unavailable";
  }
}

async function loadMetrics() {
  const grid = $("#metric-grid");
  try {
    const metrics = await requestJson("/metrics");
    grid.innerHTML = metrics.map((metric) => `
      <article class="metric-card">
        <div class="metric-top"><span class="panel-label">${metric.owner}</span><span class="version">v${metric.version}</span></div>
        <h3>${prettyName(metric.name)}</h3>
        <p>${metric.description}</p>
        <div class="metric-meta"><span>Grain: ${metric.grain}</span><span>${metric.dimensions.length} dimensions</span></div>
      </article>`).join("");
  } catch (error) {
    grid.innerHTML = `<p>Metric catalog unavailable: ${error.message}</p>`;
  }
}

function renderTable(data) {
  const table = $("#result-table");
  table.querySelector("thead").innerHTML = `<tr>${data.columns.map((column) => `<th>${column}</th>`).join("")}</tr>`;
  table.querySelector("tbody").innerHTML = data.rows.map((row) => `<tr>${row.map((value) => `<td>${value ?? "—"}</td>`).join("")}</tr>`).join("");
  $("#row-summary").textContent = `${data.row_count} row${data.row_count === 1 ? "" : "s"}${data.truncated ? "+" : ""}`;
}

function renderResult(result) {
  latestSql = result.sql;
  $("#resolved-metric").textContent = `${prettyName(result.metric)} · v${result.version}`;
  $("#sql-output").textContent = result.sql;
  $("#lineage").innerHTML = result.lineage.map((item) => `<span>${item}</span>`).join("");

  const score = result.trust.score;
  $("#trust-score").textContent = `${Math.round(score * 100)}%`;
  $("#trust-ring").style.setProperty("--score", `${score * 360}deg`);
  $("#trust-decision").textContent = result.trust.decision;
  $("#trust-reason").textContent = `${Math.round(result.resolution.confidence * 100)}% intent confidence`;
  $("#decision-badge").textContent = result.trust.decision;

  const dryRun = result.dry_run;
  $("#dry-run-cost").textContent = dryRun?.valid ? `Passed · cost ${dryRun.estimated_cost}` : "Unavailable";
  renderTable(result.data || { columns: [], rows: [], row_count: 0 });
  resultSection.hidden = false;
  resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function runQuery() {
  const value = question.value.trim();
  if (!value) return;
  const button = form.querySelector("button[type=submit]");
  const original = button.innerHTML;
  button.disabled = true;
  button.innerHTML = "<span>Resolving and validating…</span><b>···</b>";
  try {
    const result = await requestJson("/query", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ question: value, explain: true, execute: true }),
    });
    renderResult(result);
    notify("Governed query completed successfully");
  } catch (error) {
    notify(error.message, true);
  } finally {
    button.disabled = false;
    button.innerHTML = original;
  }
}

form.addEventListener("submit", (event) => { event.preventDefault(); runQuery(); });
question.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key === "Enter") runQuery();
});
document.querySelectorAll(".example").forEach((button) => {
  button.addEventListener("click", () => { question.value = button.dataset.question; question.focus(); });
});
$("#copy-sql").addEventListener("click", async () => {
  if (!latestSql) return;
  await navigator.clipboard.writeText(latestSql);
  notify("SQL copied to clipboard");
});

loadHealth();
loadMetrics();

