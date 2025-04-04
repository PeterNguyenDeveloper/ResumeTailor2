"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Upload, FileText, X } from "lucide-react"

interface UploadFormProps {
    onUpload: (file: File) => void
}

export default function UploadForm({ onUpload }: UploadFormProps) {
    const [dragActive, setDragActive] = useState(false)
    const [selectedFile, setSelectedFile] = useState<File | null>(null)
    const [error, setError] = useState<string | null>(null)
    const fileInputRef = useRef<HTMLInputElement>(null)

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()

        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true)
        } else if (e.type === "dragleave") {
            setDragActive(false)
        }
    }

    const validateFile = (file: File): boolean => {
        if (!file.name.endsWith(".pdf")) {
            setError("Please upload a PDF file")
            return false
        }

        if (file.size > 5 * 1024 * 1024) {
            // 5MB
            setError("File size should be less than 5MB")
            return false
        }

        return true
    }

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        setDragActive(false)

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            const file = e.dataTransfer.files[0]
            if (validateFile(file)) {
                setSelectedFile(file)
                setError(null)
            }
        }
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        e.preventDefault()

        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0]
            if (validateFile(file)) {
                setSelectedFile(file)
                setError(null)
            }
        }
    }

    const handleClick = () => {
        fileInputRef.current?.click()
    }

    const removeFile = () => {
        setSelectedFile(null)
        if (fileInputRef.current) {
            fileInputRef.current.value = ""
        }
    }

    const handleSubmit = () => {
        if (selectedFile) {
            onUpload(selectedFile)
        }
    }

    return (
        <div className="space-y-6">
            <h2 className="text-2xl font-semibold text-gray-800">Upload Your Resume</h2>
            <p className="text-gray-600">Upload your current resume in PDF format to get started.</p>

            <div
                className={`border-2 border-dashed rounded-lg p-8 text-center ${
                    dragActive ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-blue-400"
                } transition-colors duration-200 cursor-pointer`}
                onClick={handleClick}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                <input ref={fileInputRef} type="file" className="hidden" accept=".pdf" onChange={handleChange} />

                <div className="flex flex-col items-center justify-center space-y-4">
                    <Upload className="w-12 h-12 text-gray-400" />
                    <div className="space-y-1">
                        <p className="text-gray-700 font-medium">Drag and drop your resume here</p>
                        <p className="text-gray-500 text-sm">or click to browse files</p>
                    </div>
                    <p className="text-gray-400 text-xs">PDF files only, max 5MB</p>
                </div>
            </div>

            {error && <div className="p-4 bg-red-100 text-red-700 rounded-lg">{error}</div>}

            {selectedFile && (
                <div className="flex items-center justify-between p-4 bg-gray-100 rounded-lg">
                    <div className="flex items-center space-x-3">
                        <FileText className="w-6 h-6 text-blue-600" />
                        <div>
                            <p className="font-medium text-gray-800">{selectedFile.name}</p>
                            <p className="text-xs text-gray-500">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                        </div>
                    </div>
                    <button
                        onClick={(e) => {
                            e.stopPropagation()
                            removeFile()
                        }}
                        className="p-1 rounded-full hover:bg-gray-200"
                    >
                        <X className="w-5 h-5 text-gray-500" />
                    </button>
                </div>
            )}

            <div className="flex justify-end">
                <button
                    onClick={handleSubmit}
                    disabled={!selectedFile}
                    className={`px-6 py-2 rounded-lg transition ${
                        !selectedFile ? "bg-gray-200 text-gray-400 cursor-not-allowed" : "bg-blue-600 text-white hover:bg-blue-700"
                    }`}
                >
                    Continue
                </button>
            </div>
        </div>
    )
}

