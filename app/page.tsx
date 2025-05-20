"use client"

import React, { useState } from "react"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { Progress } from "@/components/ui/progress"
import { Upload, FileImage, Loader2, BarChart3, Download } from "lucide-react"
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"

interface AnalysisResult {
  average_diameter: number
  mode_diameter: number
  histogram_data: Array<{
    diameter: number
    pdf: number
  }>
  threshold_image_url: string
  colormap_image_url: string
  histogram_image_url: string
  raw_data_url: string
  image_info: {
    dimensions: string
    magnification: string
    pixel_size: string
  }
}

// API endpoint
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/analyze"
const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL || "http://localhost:8000"

const parseAnalysisResults = (data: any): AnalysisResult => {
  const outputDir = data.output_directory.split("/").pop() || "" // Get the last part of the path
  return {
    average_diameter: parseFloat(data.results.statistics.average_diameter.split(' ')[0]),
    mode_diameter: parseFloat(data.results.statistics.mode_diameter.split(' ')[0]),
    histogram_data: data.results.diameter_distribution.centers.map((d: number, i: number) => ({
      diameter: d,
      pdf: data.results.diameter_distribution.pdf[i]
    })),
    threshold_image_url: `${BASE_URL}/results/${outputDir}/thresholded_image.png`,
    colormap_image_url: `${BASE_URL}/results/${outputDir}/filtered_image_colormap.png`,
    histogram_image_url: `${BASE_URL}/results/${outputDir}/pore_size_distribution.png`,
    raw_data_url: `${BASE_URL}/results/${outputDir}/pore_size_analysis.txt`,
    image_info: {
      dimensions: data.results.image_info.dimensions,
      magnification: data.results.image_info.magnification,
      pixel_size: data.results.image_info.pixel_size
    }
  }
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [magnification, setMagnification] = useState<number>(300)
  const [maxDiameter, setMaxDiameter] = useState<number>(80)
  const [threshMag, setThreshMag] = useState<number>(1.80)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setFile(file)
      setError(null)
      setPreviewUrl(URL.createObjectURL(file))
    }
  }

  // Function to handle analysis
  const runAnalysis = async () => {
    if (!file) return;
    
    setLoading(true);
    setError(null);
    setUploadProgress(0);

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('magnification', magnification.toString())
      formData.append('max_diam_nm', maxDiameter.toString())
      formData.append('thresh_mag', threshMag.toString())

      const response = await fetch(API_URL, {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(errorData.detail || 'Failed to analyze image')
      }

      const data = await response.json()
      if (data.status !== 'success') {
        throw new Error(data.detail || 'Analysis failed')
      }

      const result = parseAnalysisResults(data)
      setResult(result)
      setUploadProgress(100)
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unknown error occurred")
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = () => {
    if (result?.raw_data_url) {
      window.open(result.raw_data_url, '_blank')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) {
      setError("Please select an image file")
      return
    }
    await runAnalysis()
  }

  // Auto-run analysis when sliders change (debounced)
  React.useEffect(() => {
    if (!file) return;
    
    // Only run analysis if we have a valid result already (not initial load)
    if (!result) return;
    
    const timer = setTimeout(() => {
      runAnalysis();
    }, 1000); // 1 second debounce
    
    return () => clearTimeout(timer);
  }, [magnification, maxDiameter, threshMag]);
  
  // Add visual feedback when sliders are being adjusted
  const [isAdjusting, setIsAdjusting] = useState(false);
  
  const handleSliderChange = (setter: React.Dispatch<React.SetStateAction<number>>, value: number[]) => {
    setIsAdjusting(true);
    setter(value[0]);
    
    // Reset the adjusting state after a short delay
    setTimeout(() => {
      setIsAdjusting(false);
    }, 1000);
  };

  return (
    <main className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto py-8 px-4">
        <header className="text-center mb-10">
          <h1 className="text-4xl font-bold mb-2">Pore Size Analyzer</h1>
          <p className="text-gray-500 dark:text-gray-400 max-w-2xl mx-auto">
            Upload SEM images to analyze pore size distribution and get detailed statistics
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="h-5 w-5" />
                Upload SEM Image
              </CardTitle>
              <CardDescription>Select an image file to analyze pore size distribution</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div
                  className="border-2 border-dashed rounded-lg p-6 text-center cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={(e) => {
                    e.preventDefault()
                    const droppedFile = e.dataTransfer.files?.[0]
                    if (droppedFile && droppedFile.type.startsWith("image/")) {
                      setFile(droppedFile)
                      setError(null)
                      setPreviewUrl(URL.createObjectURL(droppedFile))
                    } else {
                      setError("Please drop an image file")
                    }
                  }}
                  onClick={() => document.getElementById("image-upload")?.click()}
                >
                  {previewUrl ? (
                    <div className="space-y-4">
                      <img
                        src={previewUrl}
                        alt="Preview"
                        className="max-h-48 mx-auto rounded-md object-contain"
                      />
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {file?.name} ({Math.round((file?.size || 0) / 1024)} KB)
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <FileImage className="h-16 w-16 mx-auto text-gray-400" />
                      <div>
                        <p className="font-medium">Drag and drop your image here or click to browse</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                          Supports JPG, PNG, and other image formats
                        </p>
                      </div>
                    </div>
                  )}
                  <Input
                    id="image-upload"
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </div>

                <div className="space-y-6 pt-4">
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <Label htmlFor="magnification">Magnification</Label>
                      <span className="text-sm font-medium">{magnification}×</span>
                    </div>
                    <div className="relative">
                      <Slider
                        id="magnification"
                        min={10}
                        max={500}
                        step={10}
                        value={[magnification]}
                        onValueChange={(value) => handleSliderChange(setMagnification, value)}
                      />
                      {isAdjusting && (
                        <div className="absolute -top-2 right-0 text-xs text-blue-500 animate-pulse">
                          Updating...
                        </div>
                      )}
                    </div>
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>10×</span>
                      <span>500×</span>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <Label htmlFor="max-diameter">Max Diameter</Label>
                      <span className="text-sm font-medium">{maxDiameter} nm</span>
                    </div>
                    <div className="relative">
                      <Slider
                        id="max-diameter"
                        min={10}
                        max={200}
                        step={5}
                        value={[maxDiameter]}
                        onValueChange={(value) => handleSliderChange(setMaxDiameter, value)}
                      />
                      {isAdjusting && (
                        <div className="absolute -top-2 right-0 text-xs text-blue-500 animate-pulse">
                          Updating...
                        </div>
                      )}
                    </div>
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>10 nm</span>
                      <span>200 nm</span>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <Label htmlFor="thresh-mag">Threshold Multiplier</Label>
                      <span className="text-sm font-medium">{threshMag.toFixed(2)}</span>
                    </div>
                    <div className="relative">
                      <Slider
                        id="thresh-mag"
                        min={0.5}
                        max={3}
                        step={0.05}
                        value={[threshMag]}
                        onValueChange={(value) => handleSliderChange(setThreshMag, value)}
                      />
                      {isAdjusting && (
                        <div className="absolute -top-2 right-0 text-xs text-blue-500 animate-pulse">
                          Updating...
                        </div>
                      )}
                    </div>
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>0.5</span>
                      <span>3.0</span>
                    </div>
                  </div>
                </div>

                {error && (
                  <Alert variant="destructive">
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                {loading && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Uploading and analyzing...</span>
                      <span>{uploadProgress}%</span>
                    </div>
                    <Progress value={uploadProgress} className="h-2" />
                  </div>
                )}

                <Button type="submit" className="w-full" disabled={loading} size="lg">
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    "Analyze Image"
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>

          {result && (
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Analysis Results
                </CardTitle>
                <CardDescription>Pore size distribution and statistics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="grid grid-cols-2 gap-4">
                    <Card>
                      <CardContent className="p-4">
                        <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Average Diameter</div>
                        <div className="text-2xl font-bold mt-1">{result.average_diameter.toFixed(2)} nm</div>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="p-4">
                        <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Mode Diameter</div>
                        <div className="text-2xl font-bold mt-1">{result.mode_diameter.toFixed(2)} nm</div>
                      </CardContent>
                    </Card>
                  </div>

                  <div className="space-y-4">
                    <Card>
                      <CardContent className="p-4">
                        <div className="text-sm font-medium text-gray-500 dark:text-gray-400">Image Information</div>
                        <div className="mt-2 space-y-1">
                          <div className="flex justify-between">
                            <span className="text-sm text-gray-500 dark:text-gray-400">Dimensions</span>
                            <span className="font-medium">{result.image_info.dimensions}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm text-gray-500 dark:text-gray-400">Magnification</span>
                            <span className="font-medium">{result.image_info.magnification}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm text-gray-500 dark:text-gray-400">Pixel Size</span>
                            <span className="font-medium">{result.image_info.pixel_size}</span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>

                  <Tabs defaultValue="histogram" className="w-full">
                    <TabsList className="grid w-full grid-cols-3">
                      <TabsTrigger value="histogram">Histogram</TabsTrigger>
                      <TabsTrigger value="threshold">Threshold</TabsTrigger>
                      <TabsTrigger value="colormap">Colormap</TabsTrigger>
                    </TabsList>

                    <TabsContent value="histogram" className="mt-4">
                      <div className="border rounded-lg overflow-hidden">
                        <img
                          src={result.histogram_image_url}
                          alt="Pore Size Distribution Histogram"
                          className="w-full h-auto"
                        />
                      </div>
                    </TabsContent>

                    <TabsContent value="threshold" className="mt-4">
                      <div className="border rounded-lg overflow-hidden">
                        <img
                          src={result.threshold_image_url}
                          alt="Thresholded Image"
                          className="w-full h-auto"
                        />
                      </div>
                    </TabsContent>

                    <TabsContent value="colormap" className="mt-4">
                      <div className="border rounded-lg overflow-hidden">
                        <img
                          src={result.colormap_image_url}
                          alt="Filtered Image Colormap"
                          className="w-full h-auto"
                        />
                      </div>
                    </TabsContent>
                  </Tabs>

                  <div className="mt-6">
                    <h3 className="text-lg font-medium mb-3">Histogram Data</h3>
                    <div className="border rounded-lg overflow-hidden">
                      <div className="max-h-48 overflow-y-auto">
                        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                          <thead className="bg-gray-50 dark:bg-gray-800 sticky top-0">
                            <tr>
                              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                                Diameter (nm)
                              </th>
                              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                                PDF
                              </th>
                            </tr>
                          </thead>
                          <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
                            {result?.histogram_data?.slice(0, 20)?.map((point, index) => (
                              <tr key={index} className={index % 2 === 0 ? "bg-gray-50 dark:bg-gray-800/50" : ""}>
                                <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                                  {point.diameter.toFixed(3)}
                                </td>
                                <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                                  {point.pdf.toFixed(6)}
                                </td>
                              </tr>
                            ))}
                            {result?.histogram_data?.length > 20 && (
                              <tr>
                                <td
                                  colSpan={2}
                                  className="px-4 py-2 text-center text-sm text-gray-500 dark:text-gray-400"
                                >
                                  ... {result?.histogram_data.length - 20} more rows
                                </td>
                              </tr>
                            )}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>

                  <div className="mt-6">
                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={handleDownload}
                    >
                      <Download className="mr-2 h-4 w-4" />
                      Download Raw Data
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </main>
  )
}


