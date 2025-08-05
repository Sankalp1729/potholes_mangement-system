"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, AlertTriangle, Calendar, MapPin } from "lucide-react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/chart-container"

const predictionData = [
  { region: "Downtown", predicted: 15, historical: 12, risk: "high" },
  { region: "Suburbs", predicted: 8, historical: 10, risk: "medium" },
  { region: "Industrial", predicted: 22, historical: 18, risk: "high" },
  { region: "Residential", predicted: 6, historical: 7, risk: "low" },
  { region: "Highway", predicted: 12, historical: 9, risk: "medium" },
]

const weatherImpact = [
  { factor: "Heavy Rain", impact: "+25%", description: "Increases pothole formation" },
  { factor: "Freeze-Thaw", impact: "+40%", description: "Major contributor in winter" },
  { factor: "Traffic Load", impact: "+15%", description: "High traffic areas" },
  { factor: "Road Age", impact: "+30%", description: "Roads over 10 years old" },
]

const chartConfig = {
  historical: {
    label: "Historical",
    color: "hsl(var(--chart-1))",
  },
  predicted: {
    label: "Predicted",
    color: "hsl(var(--chart-2))",
  },
}

export function PredictionPanel() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="w-5 h-5 mr-2" />
              Regional Predictions
            </CardTitle>
            <CardDescription>Next 30 days pothole forecast by region (XGBoost + Prophet models)</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer config={chartConfig} className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={predictionData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="region" />
                  <YAxis />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Bar dataKey="historical" fill="var(--color-historical)" name="Historical" />
                  <Bar dataKey="predicted" fill="var(--color-predicted)" name="Predicted" />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2" />
              High-Risk Areas
            </CardTitle>
            <CardDescription>Areas with highest predicted pothole formation</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {predictionData
                .filter((region) => region.risk === "high")
                .map((region) => (
                  <div key={region.region} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <MapPin className="w-4 h-4 text-red-500" />
                      <div>
                        <div className="font-medium">{region.region}</div>
                        <div className="text-sm text-gray-500">{region.predicted} predicted potholes</div>
                      </div>
                    </div>
                    <Badge variant="destructive">High Risk</Badge>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Calendar className="w-5 h-5 mr-2" />
              Weather Impact Factors
            </CardTitle>
            <CardDescription>Environmental factors affecting pothole formation</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {weatherImpact.map((factor) => (
                <div key={factor.factor} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <div className="font-medium">{factor.factor}</div>
                    <div className="text-sm text-gray-500">{factor.description}</div>
                  </div>
                  <Badge variant="outline" className="text-orange-600 border-orange-600">
                    {factor.impact}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Model Performance</CardTitle>
            <CardDescription>AI model accuracy and performance metrics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">YOLOv8 Detection Accuracy</span>
                <div className="flex items-center space-x-2">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div className="bg-green-500 h-2 rounded-full" style={{ width: "94%" }}></div>
                  </div>
                  <span className="text-sm text-gray-600">94%</span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">XGBoost Prediction Accuracy</span>
                <div className="flex items-center space-x-2">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: "87%" }}></div>
                  </div>
                  <span className="text-sm text-gray-600">87%</span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Prophet Time Series</span>
                <div className="flex items-center space-x-2">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div className="bg-purple-500 h-2 rounded-full" style={{ width: "91%" }}></div>
                  </div>
                  <span className="text-sm text-gray-600">91%</span>
                </div>
              </div>

              <div className="mt-4 p-3 bg-green-50 rounded-lg">
                <div className="text-sm font-medium text-green-800">Model Status: Active</div>
                <div className="text-xs text-green-600 mt-1">
                  Last updated: 2 hours ago | Next training: Tomorrow 2:00 AM
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
