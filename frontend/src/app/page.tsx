"use client"

import { useState } from "react"
import UploadForm from "@/components/upload-form"
import TemplateSelector from "@/components/template-selector"
import Preview from "@/components/preview"
import { Loader2 } from "lucide-react"

export default function Home() {
  const [step, setStep] = useState(1)
  const [resumeFile, setResumeFile] = useState<File | null>(null)
  const [jobDescription, setJobDescription] = useState("")
  const [selectedTemplate, setSelectedTemplate] = useState("professional")
  const [tailoredResume, setTailoredResume] = useState<string | null>(null)
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleResumeUpload = (file: File) => {
    setResumeFile(file)
    setStep(2)
  }

  const handleJobDescriptionSubmit = (description: string) => {
    setJobDescription(description)
    setStep(3)
  }

  const handleTemplateSelect = (template: string) => {
    setSelectedTemplate(template)
    setStep(4)
  }

  const handleGenerateResume = async () => {
    if (!resumeFile || !jobDescription) {
      setError("Please upload a resume and provide a job description")
      return
    }

    setLoading(true)
    setError(null)

    const formData = new FormData()
    formData.append("resume", resumeFile)
    formData.append("job_description", jobDescription)
    formData.append("template", selectedTemplate)

    try {
      const response = await fetch("http://localhost:5000/api/tailor-resume", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error("Failed to generate resume")
      }

      const data = await response.json()
      setTailoredResume(data.content)
      setPdfUrl(data.pdf_url)
    } catch (err) {
      setError("An error occurred while generating your resume. Please try again.")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setResumeFile(null)
    setJobDescription("")
    setSelectedTemplate("professional")
    setTailoredResume(null)
    setPdfUrl(null)
    setStep(1)
  }

  return (
      <main className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-12">
          <h1 className="text-4xl font-bold text-center mb-8 text-gray-800">Resume Tailor</h1>
          <p className="text-center text-gray-600 mb-12 max-w-2xl mx-auto">
            Upload your resume, add a job description, and select a template to get a tailored resume that matches the job
            requirements.
          </p>

          <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="p-6">
              <div className="flex justify-between mb-8">
                {[1, 2, 3, 4].map((i) => (
                    <div key={i} className={`flex flex-col items-center ${i <= step ? "text-blue-600" : "text-gray-400"}`}>
                      <div
                          className={`w-10 h-10 rounded-full flex items-center justify-center mb-2 ${i <= step ? "bg-blue-100 text-blue-600" : "bg-gray-100 text-gray-400"}`}
                      >
                        {i}
                      </div>
                      <span className="text-sm">
                    {i === 1 && "Upload Resume"}
                        {i === 2 && "Job Description"}
                        {i === 3 && "Select Template"}
                        {i === 4 && "Preview & Download"}
                  </span>
                    </div>
                ))}
              </div>

              {step === 1 && <UploadForm onUpload={handleResumeUpload} />}

              {step === 2 && (
                  <div className="space-y-4">
                    <h2 className="text-2xl font-semibold text-gray-800">Enter Job Description</h2>
                    <p className="text-gray-600">
                      Paste the job description to tailor your resume for this specific position.
                    </p>
                    <textarea
                        className="w-full h-64 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Paste job description here..."
                        value={jobDescription}
                        onChange={(e) => setJobDescription(e.target.value)}
                    ></textarea>
                    <div className="flex justify-between">
                      <button
                          onClick={() => setStep(1)}
                          className="px-6 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition"
                      >
                        Back
                      </button>
                      <button
                          onClick={() => handleJobDescriptionSubmit(jobDescription)}
                          disabled={!jobDescription.trim()}
                          className={`px-6 py-2 rounded-lg transition ${
                              !jobDescription.trim()
                                  ? "bg-gray-200 text-gray-400 cursor-not-allowed"
                                  : "bg-blue-600 text-white hover:bg-blue-700"
                          }`}
                      >
                        Continue
                      </button>
                    </div>
                  </div>
              )}

              {step === 3 && (
                  <TemplateSelector
                      onSelect={handleTemplateSelect}
                      selectedTemplate={selectedTemplate}
                      onBack={() => setStep(2)}
                  />
              )}

              {step === 4 && (
                  <div className="space-y-6">
                    <h2 className="text-2xl font-semibold text-gray-800">Preview & Generate</h2>

                    {!tailoredResume && !loading && (
                        <div className="text-center p-8 bg-gray-50 rounded-lg">
                          <p className="text-gray-600 mb-4">Ready to generate your tailored resume?</p>
                          <button
                              onClick={handleGenerateResume}
                              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                          >
                            Generate Resume
                          </button>
                        </div>
                    )}

                    {loading && (
                        <div className="flex flex-col items-center justify-center p-12">
                          <Loader2 className="w-12 h-12 text-blue-600 animate-spin mb-4" />
                          <p className="text-gray-600">Generating your tailored resume...</p>
                          <p className="text-gray-500 text-sm mt-2">This may take a minute or two.</p>
                        </div>
                    )}

                    {error && <div className="p-4 bg-red-100 text-red-700 rounded-lg">{error}</div>}

                    {tailoredResume && <Preview content={tailoredResume} pdfUrl={pdfUrl} template={selectedTemplate} />}

                    <div className="flex justify-between">
                      <button
                          onClick={() => setStep(3)}
                          className="px-6 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition"
                      >
                        Back
                      </button>
                      {tailoredResume && (
                          <button
                              onClick={resetForm}
                              className="px-6 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition"
                          >
                            Start Over
                          </button>
                      )}
                    </div>
                  </div>
              )}
            </div>
          </div>
        </div>
      </main>
  )
}

