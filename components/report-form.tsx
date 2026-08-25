"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent } from "@/components/ui/card"
import { Camera, MapPin, Upload } from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export function ReportForm() {
  const [formData, setFormData] = useState({
    description: "",
    severity: "",
    latitude: "",
    longitude: "",
    image: null as File | null,
  })
  const [submitting, setSubmitting] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [detection, setDetection] = useState<any>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setMessage(null)
    setDetection(null)

    try {
      if (!formData.latitude || !formData.longitude) {
        throw new Error("Please provide your location or use Get Current Location.")
      }
      if (!formData.severity) {
        throw new Error("Please select a severity level.")
      }

      const body = new FormData()
      body.append("latitude", formData.latitude)
      body.append("longitude", formData.longitude)
      body.append("severity", formData.severity)
      body.append("description", formData.description)
      body.append("report_source", "web")
      if (formData.image) body.append("image", formData.image)

      const response = await fetch(`${API_URL}/upload-report`, {
        method: "POST",
        body,
      })

      const data = await response.json().catch(() => ({}))
      if (!response.ok) {
        throw new Error(data.detail || `Request failed with status ${response.status}`)
      }

      setDetection(data.detection_result)
      setMessage("Report submitted successfully.")
      setFormData((prev) => ({ ...prev, description: "", image: null }))
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to submit report.")
    } finally {
      setSubmitting(false)
    }
  }

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData((prev) => ({
            ...prev,
            latitude: position.coords.latitude.toString(),
            longitude: position.coords.longitude.toString(),
          }))
        },
        (error) => {
          console.error("Error getting location:", error)
          setMessage("Unable to get current location.")
        },
      )
    } else {
      setMessage("Geolocation is not supported by this browser.")
    }
  }

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) setFormData((prev) => ({ ...prev, image: file }))
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div>
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              placeholder="Describe the pothole (size, location details, etc.)"
              value={formData.description}
              onChange={(e) => setFormData((prev) => ({ ...prev, description: e.target.value }))}
              className="mt-1"
            />
          </div>

          <div>
            <Label htmlFor="severity">Severity Level</Label>
            <Select value={formData.severity} onValueChange={(value) => setFormData((prev) => ({ ...prev, severity: value }))}>
              <SelectTrigger className="mt-1">
                <SelectValue placeholder="Select severity level" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="low">Low - Minor surface damage</SelectItem>
                <SelectItem value="medium">Medium - Noticeable hole</SelectItem>
                <SelectItem value="high">High - Large pothole</SelectItem>
                <SelectItem value="critical">Critical - Dangerous to vehicles</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="latitude">Latitude</Label>
              <Input id="latitude" type="number" step="any" placeholder="19.0760" value={formData.latitude} onChange={(e) => setFormData((prev) => ({ ...prev, latitude: e.target.value }))} className="mt-1" />
            </div>
            <div>
              <Label htmlFor="longitude">Longitude</Label>
              <Input id="longitude" type="number" step="any" placeholder="72.8777" value={formData.longitude} onChange={(e) => setFormData((prev) => ({ ...prev, longitude: e.target.value }))} className="mt-1" />
            </div>
          </div>

          <Button type="button" variant="outline" onClick={getCurrentLocation} className="w-full bg-transparent">
            <MapPin className="w-4 h-4 mr-2" />
            Get Current Location
          </Button>
        </div>

        <div className="space-y-4">
          <div>
            <Label htmlFor="image">Upload Image</Label>
            <Card className="mt-1">
              <CardContent className="p-6">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                  <input id="image" type="file" accept="image/*" onChange={handleImageUpload} className="hidden" />
                  <label htmlFor="image" className="cursor-pointer">
                    <Camera className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                    <p className="text-sm text-gray-600 mb-2">
                      {formData.image ? formData.image.name : "Click to upload an image"}
                    </p>
                    <p className="text-xs text-gray-400">PNG, JPG up to 10MB</p>
                  </label>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-semibold text-blue-900 mb-2">AI Detection</h4>
            <p className="text-sm text-blue-700">
              The trained YOLOv8 model analyzes the uploaded image and returns real road-damage detections and bounding boxes.
            </p>
          </div>

          {detection && (
            <div className="rounded-lg border p-4 text-sm">
              <p className="font-semibold">AI result</p>
              <p>{detection.detected ? "Pothole detected" : "No pothole detected"}</p>
              <p>Confidence: {(Number(detection.confidence) * 100).toFixed(1)}%</p>
              <p>Severity heuristic: {detection.severity}</p>
              <p>Detected objects: {detection.bounding_boxes?.length ?? 0}</p>
            </div>
          )}
        </div>
      </div>

      {message && <p className="text-sm rounded-lg bg-gray-50 p-3">{message}</p>}

      <div className="flex justify-end space-x-4">
        <Button type="button" variant="outline" disabled={submitting}>
          Save as Draft
        </Button>
        <Button type="submit" disabled={submitting}>
          <Upload className="w-4 h-4 mr-2" />
          {submitting ? "Submitting..." : "Submit Report"}
        </Button>
      </div>
    </form>
  )
}
