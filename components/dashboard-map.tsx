"use client"

import { useEffect, useRef } from "react"

interface Pothole {
  id: string
  latitude: number
  longitude: number
  severity: "low" | "medium" | "high" | "critical"
  status: string
  description?: string
}

interface DashboardMapProps {
  potholes: Pothole[]
}

export function DashboardMap({ potholes }: DashboardMapProps) {
  const mapRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // In a real implementation, you would initialize a map library like Leaflet or Mapbox here
    // For now, we'll show a placeholder with pothole markers
  }, [potholes])

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "low":
        return "#10b981"
      case "medium":
        return "#f59e0b"
      case "high":
        return "#f97316"
      case "critical":
        return "#ef4444"
      default:
        return "#6b7280"
    }
  }

  return (
    <div className="relative">
      <div
        ref={mapRef}
        className="w-full h-96 bg-gray-100 rounded-lg flex items-center justify-center relative overflow-hidden"
      >
        {/* Grid pattern background */}
        <div className="absolute inset-0 opacity-20">
          <div
            className="w-full h-full"
            style={{
              backgroundImage: "radial-gradient(circle, #e5e7eb 1px, transparent 1px)",
              backgroundSize: "20px 20px",
            }}
          ></div>
        </div>

        {/* Simulated map with pothole markers */}
        <div className="absolute inset-0">
          {potholes.map((pothole, index) => {
            const leftPos = 20 + index * 25
            const topPos = 30 + (index % 2 === 0 ? 10 : -10)

            return (
              <div
                key={pothole.id}
                className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer group"
                style={{
                  left: `${Math.min(leftPos, 90)}%`,
                  top: `${Math.max(Math.min(topPos, 90), 10)}%`,
                }}
              >
                <div
                  className="w-4 h-4 rounded-full border-2 border-white shadow-lg"
                  style={{ backgroundColor: getSeverityColor(pothole.severity) }}
                />
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-black text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                  {pothole.severity.toUpperCase()} - {pothole.description}
                </div>
              </div>
            )
          })}
        </div>

        <div className="text-center text-gray-500 z-10">
          <div className="text-lg font-semibold mb-2">Interactive Map View</div>
          <div className="text-sm">In production, this would show a real map with Leaflet/Mapbox</div>
          <div className="text-xs mt-2">Markers represent pothole locations with severity-based colors</div>
        </div>
      </div>

      {/* Map Legend */}
      <div className="mt-4 flex items-center justify-center space-x-6">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded-full bg-green-500"></div>
          <span className="text-sm">Low</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
          <span className="text-sm">Medium</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded-full bg-orange-500"></div>
          <span className="text-sm">High</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 rounded-full bg-red-500"></div>
          <span className="text-sm">Critical</span>
        </div>
      </div>
    </div>
  )
}
