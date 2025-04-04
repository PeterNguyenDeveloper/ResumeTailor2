"use client"
import { Check } from "lucide-react"

interface TemplateSelectorProps {
    onSelect: (template: string) => void
    selectedTemplate: string
    onBack: () => void
}

const templates = [
    {
        id: "professional",
        name: "Professional",
        description: "Clean and modern design suitable for most industries",
        image: "/placeholder.svg?height=200&width=150",
    },
    {
        id: "creative",
        name: "Creative",
        description: "Bold design for creative industries and roles",
        image: "/placeholder.svg?height=200&width=150",
    },
    {
        id: "minimal",
        name: "Minimal",
        description: "Simple and elegant design with focus on content",
        image: "/placeholder.svg?height=200&width=150",
    },
    {
        id: "executive",
        name: "Executive",
        description: "Sophisticated design for senior positions",
        image: "/placeholder.svg?height=200&width=150",
    },
]

export default function TemplateSelector({ onSelect, selectedTemplate, onBack }: TemplateSelectorProps) {
    return (
        <div className="space-y-6">
            <h2 className="text-2xl font-semibold text-gray-800">Select a Template</h2>
            <p className="text-gray-600">Choose a template for your tailored resume.</p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                {templates.map((template) => (
                    <div
                        key={template.id}
                        onClick={() => onSelect(template.id)}
                        className={`relative border rounded-lg overflow-hidden cursor-pointer transition ${
                            selectedTemplate === template.id
                                ? "border-blue-500 ring-2 ring-blue-200"
                                : "border-gray-200 hover:border-blue-300"
                        }`}
                    >
                        {selectedTemplate === template.id && (
                            <div className="absolute top-2 right-2 bg-blue-500 text-white p-1 rounded-full">
                                <Check className="w-4 h-4" />
                            </div>
                        )}
                        <div className="p-4">
                            <img
                                src={template.image || "/placeholder.svg"}
                                alt={template.name}
                                className="w-full h-48 object-cover object-top mb-4 bg-gray-100"
                            />
                            <h3 className="font-medium text-lg text-gray-800">{template.name}</h3>
                            <p className="text-gray-600 text-sm">{template.description}</p>
                        </div>
                    </div>
                ))}
            </div>

            <div className="flex justify-between">
                <button
                    onClick={onBack}
                    className="px-6 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition"
                >
                    Back
                </button>
                <button
                    onClick={() => onSelect(selectedTemplate)}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                    Continue
                </button>
            </div>
        </div>
    )
}

