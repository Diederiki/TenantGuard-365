"use client";

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const STROKE = "rgba(148,163,184,0.18)";
const TEXT = "#94a3b8";

const tooltipStyle = {
  contentStyle: {
    backgroundColor: "#020617",
    border: "1px solid rgba(148,163,184,0.3)",
    borderRadius: 8,
    color: "#e2e8f0",
    fontSize: 12,
  },
  cursor: { fill: "rgba(59,130,246,0.08)" },
};

export function AuditTrendChart({
  data,
}: {
  data: { day: string; events: number; failures: number }[];
}) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="ev" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.5} />
            <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={STROKE} />
        <XAxis dataKey="day" stroke={TEXT} fontSize={11} />
        <YAxis stroke={TEXT} fontSize={11} />
        <Tooltip {...tooltipStyle} />
        <Area
          type="monotone"
          dataKey="events"
          stroke="#3b82f6"
          fill="url(#ev)"
          strokeWidth={2}
        />
        <Line type="monotone" dataKey="failures" stroke="#f43f5e" strokeWidth={2} dot={false} />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function SigninRiskChart({
  data,
}: {
  data: { day: string; low: number; medium: number; high: number }[];
}) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke={STROKE} />
        <XAxis dataKey="day" stroke={TEXT} fontSize={11} />
        <YAxis stroke={TEXT} fontSize={11} />
        <Tooltip {...tooltipStyle} />
        <Legend wrapperStyle={{ fontSize: 11, color: TEXT }} />
        <Bar dataKey="low" stackId="a" fill="#3b82f6" />
        <Bar dataKey="medium" stackId="a" fill="#f59e0b" />
        <Bar dataKey="high" stackId="a" fill="#f43f5e" />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function LicenseUseChart({
  data,
}: {
  data: { sku: string; used: number; bought: number }[];
}) {
  // Transform to show used vs free.
  const rows = data.map((d) => ({
    sku: d.sku,
    used: d.used,
    free: Math.max(0, d.bought - d.used),
  }));
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={rows} layout="vertical" margin={{ left: 60 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={STROKE} />
        <XAxis type="number" stroke={TEXT} fontSize={11} />
        <YAxis type="category" dataKey="sku" stroke={TEXT} fontSize={11} width={150} />
        <Tooltip {...tooltipStyle} />
        <Legend wrapperStyle={{ fontSize: 11, color: TEXT }} />
        <Bar dataKey="used" stackId="b" fill="#3b82f6" />
        <Bar dataKey="free" stackId="b" fill="#1e293b" />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function AlertSeverityChart({
  data,
}: {
  data: { sev: string; open: number; closed: number }[];
}) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke={STROKE} />
        <XAxis dataKey="sev" stroke={TEXT} fontSize={11} />
        <YAxis stroke={TEXT} fontSize={11} />
        <Tooltip {...tooltipStyle} />
        <Legend wrapperStyle={{ fontSize: 11, color: TEXT }} />
        <Bar dataKey="open" stackId="s" fill="#f43f5e" />
        <Bar dataKey="closed" stackId="s" fill="#1e293b" />
      </BarChart>
    </ResponsiveContainer>
  );
}

const SHARING_COLORS = ["#f43f5e", "#f59e0b", "#3b82f6", "#1e293b"];

export function SharingRiskChart({
  data,
}: {
  data: { name: string; value: number }[];
}) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Tooltip {...tooltipStyle} />
        <Legend wrapperStyle={{ fontSize: 11, color: TEXT }} />
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          innerRadius={50}
          outerRadius={85}
          paddingAngle={2}
        >
          {data.map((_, i) => (
            <Cell key={i} fill={SHARING_COLORS[i % SHARING_COLORS.length]} />
          ))}
        </Pie>
      </PieChart>
    </ResponsiveContainer>
  );
}
