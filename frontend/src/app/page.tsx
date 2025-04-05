"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Loader2, Upload, FileText, Download } from "lucide-react"

// Backend URL configuration
const BACKEND_URL = "http://137.184.12.12:5000" // Update this to your backend server address

export default function Home() {
  const [file, setFile] = useState<File | null>(null)
  const [jobDescription, setJobDescription] = useState("")
  const [template, setTemplate] = useState("professional")
  const [isLoading, setIsLoading] = useState(false)
  const [tailoredContent, setTailoredContent] = useState("")
  const [pdfUrl, setPdfUrl] = useState("")
  const [error, setError] = useState("")
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const showToast = (message: string, type: "success" | "error") => {
    setError(type === "error" ? message : "")
    // For a real toast, you would implement a toast component or use a library
    if (type === "success") {
      alert(message)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!file) {
      showToast("Please upload your resume PDF first.", "error")
      return
    }

    if (!jobDescription) {
      showToast("Please enter a job description to tailor your resume.", "error")
      return
    }

    setIsLoading(true)
    setTailoredContent("")
    setPdfUrl("")
    setError("")

    try {
      const formData = new FormData()
      formData.append("resume", file)
      formData.append("job_description", jobDescription)
      formData.append("template", template)

      const response = await fetch(`${BACKEND_URL}/api/tailor-resume`, {
        method: "POST",
        body: formData,
      })

      // Check if the response is OK before trying to parse JSON
      if (!response.ok) {
        const contentType = response.headers.get("content-type")
        if (contentType && contentType.includes("application/json")) {
          // If it's JSON, parse the error message
          const errorData = await response.json()
          throw new Error(errorData.error || `Server error: ${response.status}`)
        } else {
          // If it's not JSON, use the status text
          throw new Error(`Server error: ${response.status} ${response.statusText}`)
        }
      }

      // Now we know the response is OK, try to parse JSON
      let data
      try {
        data = await response.json()
      } catch (jsonError) {
        console.error("Error parsing JSON:", jsonError)
        throw new Error("Invalid response from server. Please try again later.")
      }

      setTailoredContent(data.content)
      setPdfUrl(data.pdf_url)

      showToast("Your resume has been tailored to the job description.", "success")
    } catch (error) {
      console.error("Error:", error)
      showToast(error instanceof Error ? error.message : "An unexpected error occurred", "error")
    } finally {
      setIsLoading(false)
    }
  }

  const handleDownload = () => {
    if (pdfUrl) {
      // Create a full URL to the backend endpoint
      const fullUrl = `${BACKEND_URL}${pdfUrl}`

      // Open the URL in a new tab/window
      window.open(fullUrl, "_blank")
    }
  }

  return (
      <main className="container mx-auto py-10 px-4">
        <h1 className="text-3xl font-bold text-center mb-8">Resume Tailoring Tool</h1>

        {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              <p>{error}</p>
            </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Upload Form Card */}
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="p-6 border-b">
              <h2 className="text-xl font-semibold">Upload Your Resume</h2>
              <p className="text-gray-500 text-sm mt-1">Upload your resume and enter the job description to tailor it.</p>
            </div>
            <div className="p-6">
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Upload Resume Area */}
                <div className="space-y-2">
                  <label htmlFor="resume" className="block text-sm font-medium text-gray-700">
                    Resume (PDF)
                  </label>
                  <div
                      className="border-2 border-dashed rounded-md p-6 text-center cursor-pointer hover:bg-gray-50"
                      onClick={() => fileInputRef.current?.click()}
                  >
                    <input
                        id="resume"
                        type="file"
                        accept=".pdf"
                        ref={fileInputRef}
                        onChange={handleFileChange}
                        className="hidden"
                    />
                    {file ? (
                        <div className="flex items-center justify-center space-x-2">
                          <FileText className="h-6 w-6 text-gray-500" />
                          <span className="text-sm text-gray-500">{file.name}</span>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center">
                          <Upload className="h-10 w-10 text-gray-300 mb-2" />
                          <span className="text-sm text-gray-500">Click to upload or drag and drop</span>
                          <span className="text-xs text-gray-400 mt-1">PDF files only</span>
                        </div>
                    )}
                  </div>
                </div>
                {/* Job Description Area */}
                <div className="space-y-2">
                  <label htmlFor="jobDescription" className="block text-sm font-medium text-gray-700">
                    Job Description
                  </label>
                  <textarea
                      id="jobDescription"
                      placeholder="Paste the job description here..."
                      value={jobDescription}
                      onChange={(e) => setJobDescription(e.target.value)}
                      rows={8}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                {/* Resume Template Area */}
                <div className="space-y-2">
                  <label htmlFor="template" className="block text-sm font-medium text-gray-700">
                    Resume Template
                  </label>
                  <select
                      id="template"
                      value={template}
                      onChange={(e) => setTemplate(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="professional">Professional</option>
                    <option value="creative">Creative</option>
                    <option value="minimal">Minimal</option>
                    <option value="executive">Executive</option>
                  </select>
                </div>

                <button
                    type="submit"
                    disabled={isLoading}
                    className={`w-full py-2 px-4 rounded-md text-white font-medium ${
                        isLoading ? "bg-blue-400 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"
                    }`}
                >
                  {isLoading ? (
                      <span className="flex items-center justify-center">
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Tailoring Resume...
                  </span>
                  ) : (
                      "Tailor Resume"
                  )}
                </button>
              </form>
            </div>
          </div>

          {/* Results Card */}
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="p-6 border-b">
              <h2 className="text-xl font-semibold">Tailored Resume</h2>
              <p className="text-gray-500 text-sm mt-1">Preview of your tailored resume content.</p>
            </div>
            <div className="p-6">
              {isLoading ? (
                  <div className="flex items-center justify-center h-64">
                    <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
                  </div>
              ) : tailoredContent ? (
                  <div
                      className="prose max-w-none h-64 overflow-y-auto border rounded-md p-4"
                      dangerouslySetInnerHTML={{ __html: tailoredContent }}
                  />
              ) : (
                  <div className="flex items-center justify-center h-64 text-gray-400 border rounded-md">
                    <p>Your tailored resume will appear here</p>
                  </div>
              )}
            </div>
            <div className="p-6 border-t">
              {pdfUrl && (
                  <button
                      className="w-full py-2 px-4 border border-gray-300 rounded-md text-gray-700 font-medium flex items-center justify-center hover:bg-gray-50"
                      onClick={handleDownload}
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Download PDF
                  </button>
              )}
            </div>
          </div>
        </div>
      </main>
  )
}

