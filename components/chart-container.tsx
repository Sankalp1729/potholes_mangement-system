import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"
import type React from "react"

interface ChartContainerProps {
  children: React.ReactNode
  config: any
  className?: string
}

export function ChartContainer({ children, config, className }: ChartContainerProps) {
  return <div className={cn("rounded-md border bg-card p-4 text-card-foreground shadow-sm", className)}>{children}</div>
}

interface ChartTooltipProps {
  children?: React.ReactNode
}

export function ChartTooltip({ children }: ChartTooltipProps) {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>{children}</TooltipTrigger>
        <TooltipContent className="bg-secondary border-secondary-foreground text-secondary-foreground">
          <p>Add chart description here</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}

interface ChartTooltipContentProps {
  payload?: any[]
  label?: string
}

export function ChartTooltipContent({ payload, label }: ChartTooltipContentProps) {
  if (!payload || payload.length === 0) {
    return null
  }

  return (
    <div className="px-2 py-1.5 text-sm font-medium">
      <p className="font-bold">{label}</p>
      {payload.map((item, index) => (
        <div key={index} className="flex items-center">
          <span className="mr-2 block h-2 w-2 rounded-full" style={{ backgroundColor: item.color }} />
          <span>
            {item.name}: {item.value}
          </span>
        </div>
      ))}
    </div>
  )
}
