"use client"

import { Download, FileText } from "lucide-react"

interface PreviewProps {
    content: string
    pdfUrl: string | null
    template: string
}

export default function Preview({ content, pdfUrl, template }: PreviewProps) {
    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h3 className="text-xl font-semibold text-gray-800">Your Tailored Resume</h3>
                {pdfUrl && (
                    <a
                        href={pdfUrl}
                        download="tailored-resume.pdf"
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                    >
                        <Download className="w-4 h-4" />
                        Download PDF
                    </a>
                )}
            </div>

            <div className="border rounded-lg overflow-hidden bg-white shadow-md">
                <div className="p-4 bg-gray-50 border-b flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <FileText className="w-5 h-5 text-gray-500" />
                        <span className="font-medium text-gray-700">Preview</span>
                    </div>
                    <span className="text-sm text-gray-500 capitalize">{template} Template</span>
                </div>

                <div className="p-6 max-h-[600px] overflow-y-auto">
                    <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: content }} />
                </div>
            </div>
        </div>
    )
}

