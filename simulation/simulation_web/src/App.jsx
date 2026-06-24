import { useEffect, useMemo, useState } from 'react';

const SCENARIOS = [
  { id: 'default', label: 'Default' },
  { id: 'moderate_scarcity', label: 'Moderate scarcity' },
  { id: 'scarcity', label: 'Scarcity' },
];

const POLICY_FAMILIES = {
  "Random": ["random"],
  "Rule-based": ["rule"],
  "Zero-shot": [
    "llm_survival",
    "llm_social_welfare",
    "llm_wealth_maximizing",
  ],
  "Few-shot": [
    "llm_survival_few_shot",
    "llm_social_welfare_few_shot",
    "llm_wealth_maximizing_few_shot",
  ],
  "Fine-tuned": [
    "finetuned_survival",
    "finetuned_social_welfare",
    "finetuned_wealth_maximizing",
  ],
};

const POLICY_DISPLAY_NAMES = {
  random: "Random",
  rule: "Rule-based",
  llm_survival: "Zero-shot Survival",
  llm_social_welfare: "Zero-shot Social Welfare",
  llm_wealth_maximizing: "Zero-shot Wealth Maximizing",
  llm_survival_few_shot: "Few-shot Survival",
  llm_social_welfare_few_shot: "Few-shot Social Welfare",
  llm_wealth_maximizing_few_shot: "Few-shot Wealth Maximizing",
  finetuned_survival: "Fine-tuned Survival",
  finetuned_social_welfare: "Fine-tuned Social Welfare",
  finetuned_wealth_maximizing: "Fine-tuned Wealth Maximizing",
};

const BASE_DELAY_MS = 900;

const SPEEDS = [
  { id: '0.25x', label: '0.25x', multiplier: 0.25 },
  { id: '0.5x', label: '0.5x', multiplier: 0.5 },
  { id: '1x', label: '1x', multiplier: 1 },
  { id: '2x', label: '2x', multiplier: 2 },
  { id: '4x', label: '4x', multiplier: 4 },
];

const AGENT_IDS = Array.from({ length: 10 }, (_, index) => index);

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  if (!lines.length) return [];

  const headers = lines[0].split(',').map((header) => header.trim());
  return lines.slice(1).filter(Boolean).map((line) => {
    const values = line.split(',');
    return headers.reduce((row, header, index) => {
      row[header] = coerceValue(values[index]?.trim() ?? '');
      return row;
    }, {});
  });
}

function coerceValue(value) {
  if (value === 'True') return true;
  if (value === 'False') return false;
  if (value !== '' && !Number.isNaN(Number(value))) return Number(value);
  return value;
}

function formatNumber(value, digits = 2) {
  if (typeof value !== 'number' || Number.isNaN(value)) return '0';
  return value.toLocaleString(undefined, {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  });
}

function signedDelta(value, digits = 3) {
  if (typeof value !== 'number' || Number.isNaN(value)) return '0';
  const sign = value > 0 ? '+' : '';
  return `${sign}${value.toFixed(digits)}`;
}

function hashString(input) {
  let hash = 2166136261;
  for (let index = 0; index < input.length; index += 1) {
    hash ^= input.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

function visualPosition({ agentId, timestep, policy, scenario }) {
  const seed = hashString(`${scenario}:${policy}:${timestep}:${agentId}`);
  const x = 6 + (seed % 88);
  const y = 8 + (Math.floor(seed / 97) % 80);
  return { x, y };
}

function InlineIcon({ type, label }) {
  const src = type === 'coin' ? '/assets/icons/coin.png' : '/assets/icons/food.png';
  return <img className="inline-icon" src={src} alt={label} title={label} />;
}

function actionIcon(agent) {
  if (!agent.alive) return '☠️';
  if (agent.action === 'gather') return <InlineIcon type="food" label="Gather" />;
  if (agent.action === 'work') return <InlineIcon type="coin" label="Work" />;
  return '🟢';
}

function agentSprite(agent) {
  if (!agent.alive) return '/assets/agents/agent-dead.png';
  if (agent.action === 'gather') return '/assets/agents/agent-gather.png';
  if (agent.action === 'work') return '/assets/agents/agent-work.png';
  return '/assets/agents/agent-work.png';
}

function agentLabel(agentId) {
  return `A${String(agentId).padStart(2, '0')}`;
}

function buildIndexes(stepRows, agentRows) {
  const stepsByTime = new Map();
  const agentsByTime = new Map();
  const latestByAgent = new Map();
  const seenAgents = new Set();

  for (const row of stepRows) {
    stepsByTime.set(Number(row.timestep), row);
  }

  for (const row of agentRows) {
    const timestep = Number(row.timestep);
    const agentId = Number(row.agent_id);
    seenAgents.add(agentId);
    latestByAgent.set(agentId, row);

    if (!agentsByTime.has(timestep)) agentsByTime.set(timestep, new Map());
    agentsByTime.get(timestep).set(agentId, row);
  }

  const maxTimestep = Math.max(0, ...stepRows.map((row) => Number(row.timestep)));
  return { stepsByTime, agentsByTime, latestByAgent, seenAgents, maxTimestep };
}

function getAgentState(indexes, timestep, agentId) {
  const current = indexes.agentsByTime.get(timestep)?.get(agentId);
  if (current) return current;

  let latestBefore = null;
  for (let cursor = timestep - 1; cursor >= 0; cursor -= 1) {
    const prior = indexes.agentsByTime.get(cursor)?.get(agentId);
    if (prior) {
      latestBefore = prior;
      break;
    }
  }

  if (latestBefore || indexes.seenAgents.has(agentId)) {
    return {
      ...(latestBefore ?? { agent_id: agentId, food: 0, coin: 0, action: 'missing' }),
      timestep,
      agent_id: agentId,
      action: 'missing',
      alive: false,
    };
  }

  return {
    timestep,
    agent_id: agentId,
    food: 0,
    coin: 0,
    action: 'missing',
    alive: false,
  };
}

function lastAliveTimestep(indexes, timestep, agentId) {
  for (let cursor = timestep; cursor >= 0; cursor -= 1) {
    const prior = getAgentState(indexes, cursor, agentId);
    if (prior?.alive === true) return cursor;
  }
  return timestep;
}

function App() {
  const [scenario, setScenario] = useState(SCENARIOS[0].id);
  const [policyFamily, setPolicyFamily] = useState(Object.keys(POLICY_FAMILIES)[0]);
  const [policy, setPolicy] = useState(POLICY_FAMILIES.Random[0]);
  const [speedId, setSpeedId] = useState(SPEEDS[2].id);
  const [timestep, setTimestep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showSummary, setShowSummary] = useState(false);
  const [data, setData] = useState({ stepRows: [], agentRows: [] });
  const [loadState, setLoadState] = useState({ status: 'loading', message: '' });

  const activePolicies = useMemo(
    () => POLICY_FAMILIES[policyFamily] ?? POLICY_FAMILIES.Random,
    [policyFamily],
  );

  const activeSpeed = useMemo(
    () => SPEEDS.find((speed) => speed.id === speedId) ?? SPEEDS[2],
    [speedId],
  );

  const activeSpeedDelay = Math.round(BASE_DELAY_MS / activeSpeed.multiplier);

  const indexes = useMemo(
    () => buildIndexes(data.stepRows, data.agentRows),
    [data.stepRows, data.agentRows],
  );

  const currentStep = indexes.stepsByTime.get(timestep) ?? null;
  const previousStep = indexes.stepsByTime.get(Math.max(0, timestep - 1)) ?? null;
  const agents = AGENT_IDS.map((agentId) => {
    const row = getAgentState(indexes, timestep, agentId);
    const visualTimestep = row?.alive === true ? timestep : lastAliveTimestep(indexes, timestep, agentId);
    return {
      ...row,
      agent_id: Number(row.agent_id),
      alive: row.alive === true,
      position: visualPosition({ agentId, timestep: visualTimestep, policy, scenario }),
    };
  });

  useEffect(() => {
    const firstPolicy = activePolicies[0];
    if (!activePolicies.includes(policy)) {
      setPolicy(firstPolicy);
    }
  }, [activePolicies, policy]);

  useEffect(() => {
    let cancelled = false;

    async function loadLogs() {
      setLoadState({ status: 'loading', message: '' });
      setIsPlaying(false);
      setShowSummary(false);
      setTimestep(0);

      const baseName = `${scenario}_${policy}_seed_1`;
      const stepUrl = `/final_logs/${baseName}_step_log.csv`;
      const agentUrl = `/final_logs/${baseName}_agent_log.csv`;

      try {
        const [stepResponse, agentResponse] = await Promise.all([
          fetch(stepUrl),
          fetch(agentUrl),
        ]);

        if (!stepResponse.ok || !agentResponse.ok) {
          throw new Error(`Missing CSV log for ${baseName}`);
        }

        const [stepText, agentText] = await Promise.all([
          stepResponse.text(),
          agentResponse.text(),
        ]);

        if (!cancelled) {
          setData({
            stepRows: parseCsv(stepText),
            agentRows: parseCsv(agentText),
          });
          setLoadState({ status: 'ready', message: '' });
        }
      } catch (error) {
        if (!cancelled) {
          setData({ stepRows: [], agentRows: [] });
          setLoadState({
            status: 'error',
            message: error instanceof Error ? error.message : 'Could not load CSV logs.',
          });
        }
      }
    }

    loadLogs();
    return () => {
      cancelled = true;
    };
  }, [scenario, policy]);

  useEffect(() => {
    if (!isPlaying || loadState.status !== 'ready') return undefined;

    const timer = window.setInterval(() => {
      setTimestep((current) => {
        const nextTimestep = current + 1;
        if (nextTimestep >= indexes.maxTimestep) {
          setIsPlaying(false);
          return indexes.maxTimestep;
        }
        return nextTimestep;
      });
    }, activeSpeedDelay);

    return () => window.clearInterval(timer);
  }, [activeSpeedDelay, indexes.maxTimestep, isPlaying, loadState.status]);

  useEffect(() => {
    setTimestep((current) => Math.min(current, indexes.maxTimestep));
  }, [indexes.maxTimestep]);

  const canInteract = loadState.status === 'ready';
  const isAtFinalTimestep = canInteract && data.stepRows.length > 0 && timestep >= indexes.maxTimestep;
  const showFinalReport = isAtFinalTimestep && showSummary;
  const showCompletionOverlay = isAtFinalTimestep && !showSummary;

  useEffect(() => {
    if (isPlaying && isAtFinalTimestep) {
      setIsPlaying(false);
    }
  }, [isAtFinalTimestep, isPlaying]);

  useEffect(() => {
    if (!isAtFinalTimestep) {
      setShowSummary(false);
      return undefined;
    }

    if (showSummary) return undefined;

    const timer = window.setTimeout(() => {
      setShowSummary(true);
    }, 800);

    return () => window.clearTimeout(timer);
  }, [isAtFinalTimestep, showSummary]);

  const events = useMemo(
    () => buildEvents({ agents, currentStep, previousStep, indexes, timestep }),
    [agents, currentStep, previousStep, indexes, timestep],
  );

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">Completed CSV logs</p>
          <h1>AI Society Simulation</h1>
        </div>

        <label className="control">
          <span>Scenario</span>
          <select value={scenario} onChange={(event) => setScenario(event.target.value)}>
            {SCENARIOS.map((item) => (
              <option key={item.id} value={item.id}>{item.label}</option>
            ))}
          </select>
        </label>

        <label className="control">
          <span>Policy type</span>
          <select value={policyFamily} onChange={(event) => setPolicyFamily(event.target.value)}>
            {Object.keys(POLICY_FAMILIES).map((family) => (
              <option key={family} value={family}>{family}</option>
            ))}
          </select>
        </label>

        <label className="control">
          <span>Policy</span>
          <select value={policy} onChange={(event) => setPolicy(event.target.value)}>
            {activePolicies.map((policyId) => (
              <option key={policyId} value={policyId}>{POLICY_DISPLAY_NAMES[policyId]}</option>
            ))}
          </select>
        </label>

        <div className="control">
          <div className="slider-row">
            <span>Timestep</span>
            <strong>{timestep}</strong>
          </div>
          <input
            type="range"
            min="0"
            max={indexes.maxTimestep}
            value={timestep}
            disabled={!canInteract}
            onChange={(event) => setTimestep(Number(event.target.value))}
          />
          <div className="timeline-caption">0 to {indexes.maxTimestep} · stops at end</div>
        </div>

        <div className="transport">
          <button type="button" disabled={!canInteract} onClick={() => setTimestep((value) => Math.max(0, value - 1))}>
            Previous
          </button>
          <button type="button" disabled={!canInteract} className="primary" onClick={() => setIsPlaying((value) => !value)}>
            {isPlaying ? 'Pause' : 'Play'}
          </button>
          <button
            type="button"
            disabled={!canInteract}
            onClick={() => setTimestep((value) => {
              const nextTimestep = Math.min(indexes.maxTimestep, value + 1);
              if (nextTimestep >= indexes.maxTimestep) setIsPlaying(false);
              return nextTimestep;
            })}
          >
            Next
          </button>
          <button type="button" disabled={!canInteract} onClick={() => { setIsPlaying(false); setShowSummary(false); setTimestep(0); }}>
            Reset
          </button>
        </div>

        <div className="control">
          <span>Speed</span>
          <div className="speed-buttons" role="group" aria-label="Playback speed">
            {SPEEDS.map((speed) => (
              <button
                type="button"
                className={`speed-button${speed.id === speedId ? ' active' : ''}`}
                aria-pressed={speed.id === speedId}
                onClick={() => setSpeedId(speed.id)}
                key={speed.id}
              >
                {speed.label}
              </button>
            ))}
          </div>
        </div>

        <MiniCharts rows={data.stepRows} timestep={timestep} />
      </aside>

      <section className={`simulation-view${showFinalReport ? ' summary-mode' : ''}`}>
        {showFinalReport ? (
          <EndSummary rows={data.stepRows} />
        ) : (
          <>
            <MetricStrip step={currentStep} timestep={timestep} />

            <div className="stage">
              <section className="board-panel" aria-label="Pixel simulation board">
                <div className="board-grid">
                  <div className="field-label">
                    <span>Society Field</span>
                    <small>visual positions only</small>
                  </div>
                  <div className="field-path path-one" aria-hidden="true" />
                  <div className="field-path path-two" aria-hidden="true" />
                  <div className="field-decor house house-one" aria-hidden="true">⌂</div>
                  <div className="field-decor house house-two" aria-hidden="true">⌂</div>
                  <div className="field-decor tree tree-one" aria-hidden="true" />
                  <div className="field-decor tree tree-two" aria-hidden="true" />
                  <div className="field-decor tree tree-three" aria-hidden="true" />
                  <div className="field-decor stone stone-one" aria-hidden="true" />
                  <div className="field-decor stone stone-two" aria-hidden="true" />
                  <div className="field-decor grass-tuft tuft-one" aria-hidden="true" />
                  <div className="field-decor grass-tuft tuft-two" aria-hidden="true" />
                  <div className="field-decor grass-tuft tuft-three" aria-hidden="true" />
                  {agents.map((agent) => (
                    <AgentPixel key={agent.agent_id} agent={agent} />
                  ))}
                </div>
              </section>

              <div className="side-stack">
                <EventFeed events={events} />
              </div>

              {showCompletionOverlay && (
                <div className="completion-overlay" role="status" aria-live="polite">
                  <div className="completion-card">
                    <strong>Run Complete</strong>
                    <span>Generating final report…</span>
                  </div>
                </div>
              )}
            </div>

            <AgentStrip agents={agents} />
          </>
        )}
      </section>
    </main>
  );
}

function MetricStrip({ step, timestep }) {
  const metrics = [
    { label: 'Timestep', value: timestep },
    { label: 'Alive / Dead', value: `${step?.alive ?? 0} / ${step?.dead_total ?? 0}` },
    { label: 'Deaths this step', value: step?.deaths_this_step ?? 0 },
    { label: 'Price', value: formatNumber(step?.price, 3) },
    { label: 'Gini population', value: formatNumber(step?.gini_population, 3) },
    { label: 'Gather / Work', value: `${step?.gather_count ?? 0} / ${step?.work_count ?? 0}` },
    { label: 'Total food', value: formatNumber(step?.total_food, 1) },
    { label: 'Total coin', value: formatNumber(step?.total_coin, 1) },
  ];

  return (
    <section className="metric-strip" aria-label="Current timestep metrics">
      {metrics.map((metric) => (
        <div className="metric-card" key={metric.label}>
          <span>{metric.label}</span>
          <strong>{metric.value}</strong>
        </div>
      ))}
    </section>
  );
}

function AgentPixel({ agent }) {
  const label = agentLabel(agent.agent_id);
  return (
    <div
      className={`agent-pixel ${agent.alive ? agent.action : 'dead'}`}
      style={{ left: `${agent.position.x}%`, top: `${agent.position.y}%` }}
      title={`${label}: ${agent.alive ? agent.action : 'dead'}`}
    >
      <img className="agent-sprite" src={agentSprite(agent)} alt="" aria-hidden="true" />
      <span className="agent-id">{label}</span>
    </div>
  );
}

function EventFeed({ events }) {
  return (
    <aside className="event-feed" aria-label="Live Events">
      <div className="panel-heading">
        <span>Live Events</span>
        <strong>{events.length}</strong>
      </div>
      <div className="event-list">
        {events.map((event) => (
          <div className={`event-item ${event.kind}`} key={event.id}>
            <span>{event.icon}</span>
            <p>{event.text}</p>
          </div>
        ))}
      </div>
    </aside>
  );
}

function MiniCharts({ rows, timestep }) {
  const chartRows = useMemo(
    () => rows
      .filter((row) => Number(row.timestep) <= timestep)
      .sort((first, second) => Number(first.timestep) - Number(second.timestep)),
    [rows, timestep],
  );
  const latest = chartRows.at(-1) ?? {};
  const charts = [
    {
      label: 'Alive',
      keyName: 'alive',
      color: '#a8c66c',
      value: latest.alive ?? 0,
    },
    {
      label: 'Price',
      keyName: 'price',
      color: '#f0cb74',
      value: formatNumber(latest.price, 2),
    },
    {
      label: 'Gini',
      keyName: 'gini_population',
      color: '#d98564',
      value: formatNumber(latest.gini_population, 3),
    },
    {
      label: 'Actions',
      keyName: 'gather_count',
      secondKeyName: 'work_count',
      color: '#a8c66c',
      secondColor: '#f0cb74',
      value: (
        <>
          <InlineIcon type="food" label="Gather" /> {latest.gather_count ?? 0}{' '}
          <InlineIcon type="coin" label="Work" /> {latest.work_count ?? 0}
        </>
      ),
    },
  ];

  return (
    <section className="mini-charts" aria-label="Mini charts">
      <div className="panel-heading compact charts-heading">
        <span>Charts</span>
      </div>
      <div className="chart-grid">
        {charts.map((chart) => (
          <MiniChart chart={chart} rows={chartRows} key={chart.label} />
        ))}
      </div>
    </section>
  );
}

function MiniChart({ chart, rows }) {
  const primaryPoints = linePoints(rows, chart.keyName);
  const secondaryPoints = chart.secondKeyName ? linePoints(rows, chart.secondKeyName) : '';

  return (
    <div className="mini-chart">
      <div className="chart-meta">
        <span>{chart.label}</span>
        <strong>{chart.value}</strong>
      </div>
      <svg viewBox="0 0 120 34" preserveAspectRatio="none" role="img" aria-label={`${chart.label} over time`}>
        <line className="chart-base" x1="2" x2="118" y1="30" y2="30" />
        {primaryPoints && (
          <polyline points={primaryPoints} fill="none" stroke={chart.color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
        )}
        {secondaryPoints && (
          <polyline points={secondaryPoints} fill="none" stroke={chart.secondColor} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
        )}
      </svg>
    </div>
  );
}

function EndSummary({ rows }) {
  const orderedRows = useMemo(
    () => [...rows].sort((first, second) => Number(first.timestep) - Number(second.timestep)),
    [rows],
  );
  const first = orderedRows[0] ?? {};
  const final = orderedRows[orderedRows.length - 1] ?? {};
  const startTimestep = formatSummaryValue(finalField(first, 'timestep'), 0);
  const endTimestep = formatSummaryValue(finalField(final, 'timestep'), 0);
  const initialAlive = finalField(first, 'alive');
  const finalAlive = finalField(final, 'alive');
  const deadTotal = finalField(final, 'dead_total');
  const finalFood = finalField(final, 'total_food');
  const finalCoin = finalField(final, 'total_coin');
  const finalGini = finalField(final, 'gini_population');
  const gatherActions = sumField(orderedRows, 'gather_count');
  const workActions = sumField(orderedRows, 'work_count');
  const totalTrades = sumField(orderedRows, 'trades');
  const hasActionData = gatherActions !== null || workActions !== null;
  const actionTotal = hasActionData ? (gatherActions ?? 0) + (workActions ?? 0) : null;
  const gatherPercent = percent(gatherActions ?? 0, actionTotal ?? 0);
  const workPercent = percent(workActions ?? 0, actionTotal ?? 0);
  const outcomeCards = [
    {
      label: 'Survival',
      value: initialAlive === null
        ? formatSummaryValue(finalAlive, 0)
        : `${formatSummaryValue(finalAlive, 0)} / ${formatSummaryValue(initialAlive, 0)}`,
      detail: 'final alive / initial alive',
    },
    {
      label: 'Deaths',
      value: formatSummaryValue(deadTotal, 0),
      detail: 'cumulative dead_total',
    },
    {
      label: 'Final resources',
      value: (
        <>
          <InlineIcon type="food" label="Food" /> {formatSummaryValue(finalFood, 1)}
          <InlineIcon type="coin" label="Coin" /> {formatSummaryValue(finalCoin, 1)}
        </>
      ),
      detail: 'food and coin at final timestep',
    },
    {
      label: 'Inequality',
      value: formatSummaryValue(finalGini, 3),
      detail: 'final gini_population',
    },
  ];
  const riskStats = [
    { label: 'Max deaths / step', value: formatSummaryValue(maxField(orderedRows, 'deaths_this_step'), 0) },
    { label: 'Lowest food', value: formatSummaryValue(minField(orderedRows, 'total_food'), 1) },
    { label: 'Highest price', value: formatSummaryValue(maxField(orderedRows, 'price'), 3) },
    { label: 'Final Gini', value: formatSummaryValue(finalGini, 3) },
  ];

  return (
    <section className="end-summary" aria-label="End of run summary">
      <div className="end-summary-header">
        <div>
          <span className="report-kicker">Final Report</span>
          <h2>End Summary</h2>
          <p>Final technical report for selected run</p>
        </div>
        <strong>t{startTimestep}-t{endTimestep}</strong>
      </div>
      <div className="outcome-grid">
        {outcomeCards.map((card) => (
          <div className="outcome-card" key={card.label}>
            <span>{card.label}</span>
            <strong>{card.value}</strong>
            <small>{card.detail}</small>
          </div>
        ))}
      </div>

      <section className="behavior-panel" aria-label="Policy behavior">
        <div className="summary-line">
          <span>Policy behavior</span>
          <strong>{formatSummaryValue(actionTotal, 0)} total actions</strong>
        </div>
        <div className="action-ratio-bar" aria-label="Gather versus work ratio">
          <span className="gather" style={{ width: `${gatherPercent}%` }} />
          <span className="work" style={{ width: `${workPercent}%` }} />
        </div>
        <div className="behavior-metrics">
          <span><b>Gather</b> {formatSummaryValue(gatherActions, 0)} ({actionTotal === null ? '—' : formatPercent(gatherPercent)})</span>
          <span><b>Work</b> {formatSummaryValue(workActions, 0)} ({actionTotal === null ? '—' : formatPercent(workPercent)})</span>
          <span><b>Trades</b> {formatSummaryValue(totalTrades, 0)}</span>
        </div>
      </section>

      <div className="report-visual-grid">
        <ReportChart title="Survival timeline" detail="alive and dead_total">
          <SurvivalTimeline rows={orderedRows} finalAlive={finalAlive} deadTotal={deadTotal} />
        </ReportChart>
        <ReportChart title="Resource trajectory" detail="total_food and total_coin">
          <ResourceTrajectory rows={orderedRows} finalFood={finalFood} finalCoin={finalCoin} />
        </ReportChart>
        <ReportChart title="Action rhythm" detail="gather_count and work_count by timestep">
          <ActionRhythm rows={orderedRows} />
        </ReportChart>
        <ReportChart title="Risk / instability" detail="derived from step metrics">
          <div className="risk-grid">
            {riskStats.map((item) => (
              <div className="risk-chip" key={item.label}>
                <span>{item.label}</span>
                <strong>{item.value}</strong>
              </div>
            ))}
          </div>
          <SpikeTimeline rows={orderedRows} />
        </ReportChart>
      </div>
    </section>
  );
}

function ReportChart({ title, detail, children }) {
  return (
    <section className="report-chart">
      <div className="summary-line">
        <span>{title}</span>
        <small>{detail}</small>
      </div>
      {children}
    </section>
  );
}

function SurvivalTimeline({ rows, finalAlive, deadTotal }) {
  const aliveArea = makeAreaPoints(rows, 'alive', 260, 116);
  const alivePoints = linePoints(rows, 'alive', 260, 116);
  const deadPoints = linePoints(rows, 'dead_total', 260, 116);

  return (
    <svg viewBox="0 0 260 116" preserveAspectRatio="none" role="img" aria-label="Survival timeline">
      {aliveArea && <polygon points={aliveArea} fill="rgba(168, 198, 108, 0.2)" />}
      {alivePoints && <polyline points={alivePoints} fill="none" stroke="#a8c66c" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />}
      {deadPoints && (
        <polyline points={deadPoints} fill="none" stroke="#d98564" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
      )}
      <line className="chart-base" x1="8" x2="252" y1="106" y2="106" />
      <text x="12" y="18">alive {formatSummaryValue(finalAlive, 0)}</text>
      <text x="12" y="34">dead {formatSummaryValue(deadTotal, 0)}</text>
    </svg>
  );
}

function ResourceTrajectory({ rows, finalFood, finalCoin }) {
  const foodEnd = endpointPoint(rows, 'total_food', 260, 116);
  const coinEnd = endpointPoint(rows, 'total_coin', 260, 116);

  return (
    <svg viewBox="0 0 260 116" preserveAspectRatio="none" role="img" aria-label="Resource trajectory">
      <line className="chart-base" x1="8" x2="252" y1="106" y2="106" />
      <polyline points={linePoints(rows, 'total_food', 260, 116)} fill="none" stroke="#a8c66c" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
      <polyline points={linePoints(rows, 'total_coin', 260, 116)} fill="none" stroke="#f0cb74" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
      {foodEnd && <circle cx={foodEnd.x} cy={foodEnd.y} r="4" fill="#a8c66c" />}
      {coinEnd && <circle cx={coinEnd.x} cy={coinEnd.y} r="4" fill="#f0cb74" />}
      <text x="12" y="18">food {formatSummaryValue(finalFood, 1)}</text>
      <text x="12" y="34">coin {formatSummaryValue(finalCoin, 1)}</text>
    </svg>
  );
}

function ActionRhythm({ rows }) {
  const width = 260;
  const height = 116;
  const baseline = 58;
  const hasActionFields = hasField(rows, 'gather_count') || hasField(rows, 'work_count');
  const values = rows.flatMap((row) => [Number(row.gather_count) || 0, Number(row.work_count) || 0]);
  const maxValue = Math.max(1, ...values);
  const step = rows.length ? width / rows.length : width;
  const barWidth = Math.max(2, Math.min(10, step * 0.34));

  return (
    <svg viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none" role="img" aria-label="Action rhythm">
      <line className="chart-base" x1="6" x2="254" y1={baseline} y2={baseline} />
      {hasActionFields ? rows.map((row, index) => {
        const gatherHeight = ((Number(row.gather_count) || 0) / maxValue) * 46;
        const workHeight = ((Number(row.work_count) || 0) / maxValue) * 46;
        const x = index * step + Math.max(2, (step - barWidth * 2 - 1) / 2);
        return (
          <g key={`${row.timestep}-${index}`}>
            <rect x={x} y={baseline - gatherHeight} width={barWidth} height={gatherHeight} fill="#a8c66c" rx="1" />
            <rect x={x + barWidth + 1} y={baseline} width={barWidth} height={workHeight} fill="#f0cb74" rx="1" />
          </g>
        );
      }) : <text x="12" y="18">No action data</text>}
      {hasActionFields && <text x="12" y="14">gather up</text>}
      {hasActionFields && <text x="12" y="108">work down</text>}
    </svg>
  );
}

function SpikeTimeline({ rows }) {
  if (!hasField(rows, 'deaths_this_step')) return null;
  const maxDeaths = maxField(rows, 'deaths_this_step') ?? 0;

  return (
    <svg className="spike-timeline" viewBox="0 0 260 34" preserveAspectRatio="none" role="img" aria-label="Deaths per step spike timeline">
      <line className="chart-base" x1="6" x2="254" y1="28" y2="28" />
      {rows.map((row, index) => {
        const value = Number(row.deaths_this_step) || 0;
        const x = rows.length <= 1 ? 130 : 6 + (index / (rows.length - 1)) * 248;
        const height = maxDeaths > 0 ? (value / maxDeaths) * 22 : 0;
        return <line x1={x} x2={x} y1={28 - height} y2="28" stroke="#d98564" strokeWidth={value > 0 ? 2 : 1} key={`${row.timestep}-${index}`} />;
      })}
    </svg>
  );
}

function hasField(rows, keyName) {
  return rows.some((row) => Object.prototype.hasOwnProperty.call(row, keyName));
}

function finalField(row, keyName) {
  if (!Object.prototype.hasOwnProperty.call(row, keyName)) return null;
  const value = Number(row[keyName]);
  return Number.isFinite(value) ? value : null;
}

function sumField(rows, keyName) {
  if (!hasField(rows, keyName)) return null;
  return rows.reduce((total, row) => {
    const value = Number(row[keyName]);
    return total + (Number.isFinite(value) ? value : 0);
  }, 0);
}

function minField(rows, keyName) {
  const values = fieldValues(rows, keyName);
  return values.length ? Math.min(...values) : null;
}

function maxField(rows, keyName) {
  const values = fieldValues(rows, keyName);
  return values.length ? Math.max(...values) : null;
}

function fieldValues(rows, keyName) {
  if (!hasField(rows, keyName)) return [];
  return rows.map((row) => Number(row[keyName])).filter((value) => Number.isFinite(value));
}

function percent(value, total) {
  if (!Number.isFinite(value) || !Number.isFinite(total) || total <= 0) return 0;
  return clamp((value / total) * 100, 0, 100);
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function formatPercent(value) {
  return `${formatNumber(value, 1)}%`;
}

function formatSummaryValue(value, digits = 1) {
  if (value === null || value === undefined) return '—';
  return formatNumber(value, digits);
}

function chartPointList(rows, keyName, width = 120, height = 34) {
  if (!hasField(rows, keyName)) return [];
  const values = rows.map((row) => Number(row[keyName]) || 0);
  if (!values.length) return [];

  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;

  return values.map((value, index) => {
    const x = values.length === 1 ? width / 2 : 4 + (index / (values.length - 1)) * (width - 8);
    const y = height - 4 - ((value - min) / span) * (height - 8);
    return { x, y, value };
  });
}

function makeAreaPoints(rows, keyName, width = 120, height = 34) {
  const points = chartPointList(rows, keyName, width, height);
  if (!points.length) return '';
  const baseline = height - 4;
  const first = points[0];
  const last = points[points.length - 1];
  return `${points.map((point) => `${point.x.toFixed(2)},${point.y.toFixed(2)}`).join(' ')} ${last.x.toFixed(2)},${baseline.toFixed(2)} ${first.x.toFixed(2)},${baseline.toFixed(2)}`;
}

function endpointPoint(rows, keyName, width = 120, height = 34) {
  const points = chartPointList(rows, keyName, width, height);
  return points.at(-1) ?? null;
}

function linePoints(rows, keyName, width = 120, height = 34) {
  return chartPointList(rows, keyName, width, height)
    .map((point) => `${point.x.toFixed(2)},${point.y.toFixed(2)}`)
    .join(' ');
}

function AgentStrip({ agents }) {
  return (
    <section className="agent-strip" aria-label="Agent state strip">
      {agents.map((agent) => (
        <div className={`agent-chip ${agent.alive ? agent.action : 'dead'}`} key={agent.agent_id}>
          <strong>{agentLabel(agent.agent_id)}</strong>
          <span>{actionIcon(agent)} {agent.alive ? agent.action : 'dead'}</span>
          <small>f {formatNumber(agent.food, 1)} · c {formatNumber(agent.coin, 1)}</small>
        </div>
      ))}
    </section>
  );
}

function buildEvents({ agents, currentStep, previousStep, indexes, timestep }) {
  const events = [];
  const gatherers = agents.filter((agent) => agent.alive && agent.action === 'gather');
  const workers = agents.filter((agent) => agent.alive && agent.action === 'work');
  const deathsThisStep = Number(currentStep?.deaths_this_step ?? 0);
  const died = agents.filter((agent) => {
    const previous = timestep > 0 ? getAgentState(indexes, timestep - 1, agent.agent_id) : null;
    return previous?.alive === true && agent.alive === false;
  });

  if (deathsThisStep >= 3) {
    events.push({
      id: 'collapse',
      kind: 'collapse',
      icon: '💥',
      text: `Population collapse detected: ${deathsThisStep} deaths this step.`,
    });
  }

  if (deathsThisStep > 0) {
    if (died.length) {
      died.forEach((agent) => {
        events.push({
          id: `died-${agent.agent_id}`,
          kind: 'dead',
          icon: '☠️',
          text: `${agentLabel(agent.agent_id)} died.`,
        });
      });
    } else {
      events.push({
        id: 'died-summary',
        kind: 'dead',
        icon: '☠️',
        text: `${deathsThisStep} agents died this step.`,
      });
    }
  }

  gatherers.forEach((agent) => {
    events.push({
      id: `gather-${agent.agent_id}`,
      kind: 'gather',
      icon: <InlineIcon type="food" label="Gather" />,
      text: `${agentLabel(agent.agent_id)} gathered food.`,
    });
  });

  workers.forEach((agent) => {
    events.push({
      id: `work-${agent.agent_id}`,
      kind: 'work',
      icon: <InlineIcon type="coin" label="Work" />,
      text: `${agentLabel(agent.agent_id)} worked for coins.`,
    });
  });

  if (currentStep) {
    const gatherCount = Number(currentStep.gather_count ?? 0);
    const workCount = Number(currentStep.work_count ?? 0);
    const aliveCount = Number(currentStep.alive ?? 0);
    const foodPerAgent = aliveCount > 0 ? Number(currentStep.total_food ?? 0) / aliveCount : 0;

    if (workCount > gatherCount && gatherCount <= Math.max(2, Math.floor(workCount * 0.45))) {
      events.push({
        id: 'work-priority-warning',
        kind: 'warning',
        icon: '⚠️',
        text: 'Agents are prioritizing work over food.',
      });
    }

    if (foodPerAgent > 0 && foodPerAgent < 3) {
      events.push({
        id: 'low-food-warning',
        kind: 'warning',
        icon: '🍞',
        text: 'Food reserves are low.',
      });
    }
  }

  if (previousStep && currentStep) {
    const foodDelta = Number(currentStep.total_food ?? 0) - Number(previousStep.total_food ?? 0);
    const sharpFoodDrop = foodDelta < -Math.max(3, Number(previousStep.total_food ?? 0) * 0.08);

    if (sharpFoodDrop) {
      events.push({
        id: 'food-drop-warning',
        kind: 'warning',
        icon: '⚠️',
        text: `Food reserves decreased by ${formatNumber(Math.abs(foodDelta), 1)}.`,
      });
    }

    events.push({
      id: 'price-change',
      kind: 'signal',
      icon: currentStep.price >= previousStep.price ? '↗' : '↘',
      text: `Price shifted ${signedDelta(currentStep.price - previousStep.price, 4)} from the previous step.`,
    });
    events.push({
      id: 'gini-change',
      kind: 'signal',
      icon: currentStep.gini_population >= previousStep.gini_population ? '↗' : '↘',
      text: `Gini changed ${signedDelta(currentStep.gini_population - previousStep.gini_population, 4)}.`,
    });
  } else {
    events.push({
      id: 'start',
      kind: 'signal',
      icon: '•',
      text: 'Initial timestep loaded.',
    });
  }

  if (deathsThisStep === 0) {
    events.push({
      id: 'no-deaths',
      kind: 'quiet',
      icon: '🟢',
      text: 'No deaths this step.',
    });
  }

  return events;
}

export default App;
