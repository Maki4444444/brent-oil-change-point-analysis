import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ReferenceDot,
  Brush,
} from "recharts";

// Downsample long series for chart performance; keeps every Nth point.
// Not used for computation (backend/model already computed exact stats),
// only for what gets drawn on screen.
function downsample(data, maxPoints = 1500) {
  if (data.length <= maxPoints) return data;
  const stride = Math.ceil(data.length / maxPoints);
  return data.filter((_, i) => i % stride === 0);
}

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null;
  const point = payload[0].payload;
  return (
    <div className="chart-tooltip">
      <div className="chart-tooltip-date mono">{label}</div>
      <div className="chart-tooltip-price mono">${point.price.toFixed(2)}</div>
    </div>
  );
}

export default function PriceChart({
  data,
  changePoints,
  events,
  highlightedEventDate,
  onBrushChange,
}) {
  const chartData = downsample(data);

  return (
    <div className="price-chart-wrap">
      <ResponsiveContainer width="100%" height={420}>
        <ComposedChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="priceFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--accent-crude)" stopOpacity={0.35} />
              <stop offset="100%" stopColor="var(--accent-crude)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="var(--border-soft)" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fill: "var(--text-muted)", fontSize: 11, fontFamily: "var(--font-mono)" }}
            tickLine={false}
            axisLine={{ stroke: "var(--border)" }}
            minTickGap={40}
          />
          <YAxis
            tick={{ fill: "var(--text-muted)", fontSize: 11, fontFamily: "var(--font-mono)" }}
            tickLine={false}
            axisLine={false}
            width={48}
            tickFormatter={(v) => `$${v}`}
          />
          <Tooltip content={<CustomTooltip />} />

          <Area
            type="monotone"
            dataKey="price"
            stroke="var(--accent-crude)"
            strokeWidth={1.5}
            fill="url(#priceFill)"
            isAnimationActive={false}
          />

          {changePoints.map((cp) => (
            <ReferenceLine
              key={cp.id}
              x={cp.change_point_date}
              stroke="var(--accent-refined)"
              strokeDasharray="4 3"
              strokeWidth={1.5}
              label={{
                value: cp.label,
                position: "top",
                fill: "var(--accent-refined)",
                fontSize: 10,
                fontFamily: "var(--font-body)",
              }}
            />
          ))}

          {events.map((ev) => {
            const point = chartData.find((d) => d.date === ev.date);
            if (!point) return null;
            const isHighlighted = highlightedEventDate === ev.date;
            return (
              <ReferenceDot
                key={ev.event_id}
                x={ev.date}
                y={point.price}
                r={isHighlighted ? 7 : 4}
                fill={isHighlighted ? "var(--accent-crude)" : "var(--text-muted)"}
                stroke="var(--bg)"
                strokeWidth={1.5}
              />
            );
          })}

          <Brush
            dataKey="date"
            height={26}
            stroke="var(--accent-refined-dim)"
            fill="var(--panel-raised)"
            travellerWidth={8}
            onChange={onBrushChange}
          />
        </ComposedChart>
      </ResponsiveContainer>
      <p className="chart-caption">
        Dashed lines mark detected Bayesian change points. Dots mark catalogued events. Drag
        the handles below the chart to zoom into a window.
      </p>
    </div>
  );
}
