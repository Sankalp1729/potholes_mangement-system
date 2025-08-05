"use client"

import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"

const data = [
  { month: "Jan", reports: 45, completed: 38 },
  { month: "Feb", reports: 52, completed: 41 },
  { month: "Mar", reports: 48, completed: 45 },
  { month: "Apr", reports: 61, completed: 52 },
  { month: "May", reports: 55, completed: 48 },
  { month: "Jun", reports: 67, completed: 58 },
  { month: "Jul", reports: 72, completed: 65 },
  { month: "Aug", reports: 69, completed: 62 },
  { month: "Sep", reports: 58, completed: 55 },
  { month: "Oct", reports: 63, completed: 59 },
  { month: "Nov", reports: 71, completed: 64 },
  { month: "Dec", reports: 68, completed: 61 },
]

const chartConfig = {
  reports: {
    label: "Reports",
    color: "hsl(var(--chart-1))",
  },
  completed: {
    label: "Completed",
    color: "hsl(var(--chart-2))",
  },
}

export function PotholeChart() {
  return (
    <ChartContainer config={chartConfig} className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <ChartTooltip content={<ChartTooltipContent />} />
          <Line type="monotone" dataKey="reports" stroke="var(--color-reports)" strokeWidth={2} name="Reports" />
          <Line type="monotone" dataKey="completed" stroke="var(--color-completed)" strokeWidth={2} name="Completed" />
        </LineChart>
      </ResponsiveContainer>
    </ChartContainer>
  )
}
