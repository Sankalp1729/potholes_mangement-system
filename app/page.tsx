"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { MapPin, AlertTriangle, Users, CheckCircle } from "lucide-react"
import { DashboardMap } from "@/components/dashboard-map"
import { PotholeChart } from "@/components/pothole-chart"
import { ReportForm } from "@/components/report-form"
import { PredictionPanel } from "@/components/prediction-panel"

interface Pothole {
  id: string
  latitude: number
  longitude: number
  severity: "low" | "medium" | "high" | "critical"
  status: "reported" | "verified" | "in_progress" | "completed"
  reportSource: "mobile" | "iot" | "manual"
  timestamp: string
  imageUrl?: string
  description?: string
}

export default function Dashboard() {
  const [potholes, setPotholes] = useState<Pothole[]>([])
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    inProgress: 0,
    completed: 0,
  })

  useEffect(() => {
    // Simulate fetching data from API
    const mockPotholes: Pothole[] = [
      {
        id: "1",
        latitude: 40.7128,
        longitude: -74.006,
        severity: "high",
        status: "reported",
        reportSource: "mobile",
        timestamp: new Date().toISOString(),
        description: "Large pothole on Main Street",
      },
      {
        id: "2",
        latitude: 40.7589,
        longitude: -73.9851,
        severity: "medium",
        status: "in_progress",
        reportSource: "iot",
        timestamp: new Date(Date.now() - 86400000).toISOString(),
        description: "Detected via sensor network",
      },
      {
        id: "3",
        latitude: 40.7505,
        longitude: -73.9934,
        severity: "critical",
        status: "verified",
        reportSource: "mobile",
        timestamp: new Date(Date.now() - 172800000).toISOString(),
        description: "Deep pothole causing vehicle damage",
      },
    ]

    setPotholes(mockPotholes)
    setStats({
      total: mockPotholes.length,
      pending: mockPotholes.filter((p) => p.status === "reported").length,
      inProgress: mockPotholes.filter((p) => p.status === "in_progress").length,
      completed: mockPotholes.filter((p) => p.status === "completed").length,
    })
  }, [])

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "low":
        return "bg-green-100 text-green-800"
      case "medium":
        return "bg-yellow-100 text-yellow-800"
      case "high":
        return "bg-orange-100 text-orange-800"
      case "critical":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "reported":
        return "bg-blue-100 text-blue-800"
      case "verified":
        return "bg-purple-100 text-purple-800"
      case "in_progress":
        return "bg-yellow-100 text-yellow-800"
      case "completed":
        return "bg-green-100 text-green-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Pothole Detection & Management System</h1>
          <p className="text-gray-600">Monitor, track, and manage pothole reports across the city</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Reports</CardTitle>
              <MapPin className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
              <p className="text-xs text-muted-foreground">+12% from last month</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.pending}</div>
              <p className="text-xs text-muted-foreground">Awaiting verification</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">In Progress</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.inProgress}</div>
              <p className="text-xs text-muted-foreground">Being repaired</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Completed</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.completed}</div>
              <p className="text-xs text-muted-foreground">This month</p>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="map" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="map">Interactive Map</TabsTrigger>
            <TabsTrigger value="reports">Reports</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="predictions">Predictions</TabsTrigger>
            <TabsTrigger value="submit">Submit Report</TabsTrigger>
          </TabsList>

          <TabsContent value="map" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Pothole Locations</CardTitle>
                <CardDescription>Interactive map showing all reported potholes</CardDescription>
              </CardHeader>
              <CardContent>
                <DashboardMap potholes={potholes} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="reports" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Recent Reports</CardTitle>
                <CardDescription>Latest pothole reports from various sources</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {potholes.map((pothole) => (
                    <div key={pothole.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className="flex flex-col">
                          <div className="flex items-center space-x-2">
                            <Badge className={getSeverityColor(pothole.severity)}>
                              {pothole.severity.toUpperCase()}
                            </Badge>
                            <Badge className={getStatusColor(pothole.status)}>
                              {pothole.status.replace("_", " ").toUpperCase()}
                            </Badge>
                            <Badge variant="outline">{pothole.reportSource.toUpperCase()}</Badge>
                          </div>
                          <p className="text-sm text-gray-600 mt-1">{pothole.description}</p>
                          <p className="text-xs text-gray-400">{new Date(pothole.timestamp).toLocaleString()}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" size="sm">
                          View Details
                        </Button>
                        <Button size="sm">Update Status</Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Pothole Trends</CardTitle>
                  <CardDescription>Monthly pothole reports over time</CardDescription>
                </CardHeader>
                <CardContent>
                  <PotholeChart />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Severity Distribution</CardTitle>
                  <CardDescription>Breakdown by severity level</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Critical</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div className="bg-red-500 h-2 rounded-full" style={{ width: "25%" }}></div>
                        </div>
                        <span className="text-sm text-gray-600">25%</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">High</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div className="bg-orange-500 h-2 rounded-full" style={{ width: "35%" }}></div>
                        </div>
                        <span className="text-sm text-gray-600">35%</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Medium</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div className="bg-yellow-500 h-2 rounded-full" style={{ width: "30%" }}></div>
                        </div>
                        <span className="text-sm text-gray-600">30%</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Low</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div className="bg-green-500 h-2 rounded-full" style={{ width: "10%" }}></div>
                        </div>
                        <span className="text-sm text-gray-600">10%</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="predictions" className="space-y-6">
            <PredictionPanel />
          </TabsContent>

          <TabsContent value="submit" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Submit New Report</CardTitle>
                <CardDescription>Report a new pothole with location and image</CardDescription>
              </CardHeader>
              <CardContent>
                <ReportForm />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
