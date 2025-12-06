import { useState } from 'react'
import axios from 'axios'
import { Upload, FileText, CheckCircle2, XCircle, AlertCircle, Loader2, ChevronDown, ChevronUp, Trash2, RefreshCw } from 'lucide-react'

function App() {
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const [selectedFiles, setSelectedFiles] = useState([])

  const handleFiles = (files) => {
    setSelectedFiles(Array.from(files))
    const form = new FormData()
    Array.from(files).forEach(f => form.append("files", f))

    setLoading(true)
    axios.post("http://localhost:8000/extract-and-validate", form)
      .then(res => setResults(res.data))
      .catch(() => alert("Upload failed — server not running?"))
      .finally(() => setLoading(false))
  }

  const handleUpload = (e) => handleFiles(e.target.files)
  const handleDrop = (e) => {
    e.preventDefault()
    setDragActive(false)
    if (e.dataTransfer.files?.length) handleFiles(e.dataTransfer.files)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-5 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <FileText className="w-9 h-9 text-blue-600" />
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">Invoice QC Console</h1>
              <p className="text-sm text-gray-500">SUPEDIO Bestellung • Quality Control Dashboard</p>
            </div>
          </div>
          {results && (
            <div className="text-sm font-medium text-gray-600">
              {results.valid}/{results.total} invoices valid
            </div>
          )}
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-10">
        {/* Upload Zone */}
        <div className="mb-10">
          <div
            onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
            onDragLeave={(e) => { e.preventDefault(); setDragActive(false) }}
            onDrop={handleDrop}
            className={`bg-white rounded-xl shadow-sm border-2 ${dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'} transition-all p-12 text-center`}
          >
            <input type="file" multiple accept=".pdf" onChange={handleUpload} id="upload" className="hidden" />
            <label htmlFor="upload" className="cursor-pointer">
              <div className="max-w-md mx-auto">
                <div className="mx-auto w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mb-6">
                  <Upload className="w-10 h-10 text-blue-600" />
                </div>
                <h3 className="text-xl font-medium text-gray-900 mb-2">
                  {loading ? "Processing invoices..." : "Drop PDF invoices here"}
                </h3>
                <p className="text-gray-500">or click to select files</p>
              </div>
            </label>

            {/* Selected files preview */}
            {selectedFiles.length > 0 && !loading && (
              <div className="mt-6 text-sm text-gray-600">
                {selectedFiles.length} file{selectedFiles.length > 1 ? 's' : ''} selected
              </div>
            )}

            {loading && (
  <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mt-8" />
)}

          </div>
        </div>

        {/* Results */}
        {results && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            {/* Action bar */}
            <div className="bg-gray-50 border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">
                Validation Results • {results.total} processed
              </h2>
              <div className="flex items-center space-x-4">
                <button onClick={() => { setResults(null); setSelectedFiles([]) }} className="cursor-pointer text-sm text-gray-600 hover:text-gray-900 flex items-center gap-2">
                  <RefreshCw className="w-4 h-4" /> Re-process
                </button>
                <button onClick={() => { setResults(null); setSelectedFiles([]) }} className="cursor-pointer text-sm text-red-600 hover:text-red-700 flex items-center gap-2">
                  <Trash2 className="w-4 h-4" /> Clear
                </button>
              </div>
            </div>

            {/* Summary */}
            <div className="px-6 py-4 bg-gray-50 border-b border-gray-200 flex items-center justify-end space-x-8">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-600" />
                <span className="font-medium text-green-700">{results.valid} Passed</span>
              </div>
              <div className="flex items-center gap-2">
                <XCircle className="w-5 h-5 text-red-600" />
                <span className="font-medium text-red-700">{results.total - results.valid} Failed</span>
              </div>
            </div>

            {/* Table */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">File</th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Invoice Number</th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Buyer</th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Seller</th>
                    <th className="px-6 py-4 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                    <th className="px-6 py-4 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {results.invoices.map((inv, i) => {
                    const res = results.results[i]
                    const isValid = res.is_valid
                    const hasErrors = res.errors?.length > 0

                    return (
                      <tr key={i} className="hover:bg-gray-50 transition-colors cursor-pointer">
                        <td className="px-6 py-5 text-sm text-gray-900 font-medium">{inv.source_file}</td>
                        <td className="px-6 py-5 text-sm font-mono text-gray-700">{inv.invoice_number}</td>
                        <td className="px-6 py-5 text-sm text-gray-900">{inv.buyer_name}</td>
                        <td className="px-6 py-5 text-sm text-gray-600">{inv.seller_name}</td>
                        <td className="px-6 py-5 text-sm text-right font-medium text-gray-900">
                          €{Number(inv.gross_total).toFixed(2)}
                        </td>
                        <td className="px-6 py-5 text-center">
                          {isValid ? (
                            <span className="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-semibold bg-green-100 text-green-800">
                              <CheckCircle2 className="w-4 h-4 mr-1" /> PASS
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-semibold bg-red-100 text-red-800">
                              <AlertCircle className="w-4 h-4 mr-1" /> FAIL ({res.errors.length})
                            </span>
                          )}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App