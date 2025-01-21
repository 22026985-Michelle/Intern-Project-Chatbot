import React, { useState } from 'react';
import { FileText, Copy, Download } from 'lucide-react';

const JsonTable = () => {
  const [data, setData] = useState(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState('');

  const handlePaste = (e) => {
    try {
      // Get pasted content
      const pastedText = e.clipboardData.getData('text');
      
      // Try to parse as JSON
      try {
        const parsedJson = JSON.parse(pastedText);
        setData(parsedJson);
        setError('');
      } catch (jsonError) {
        // If not JSON, try to parse as key-value pairs
        const lines = pastedText.split('\n').filter(line => line.trim());
        const parsedData = {};
        
        lines.forEach(line => {
          const [key, ...valueParts] = line.split(':');
          if (key && valueParts.length > 0) {
            const value = valueParts.join(':').trim();
            parsedData[key.trim()] = value;
          }
        });
        
        if (Object.keys(parsedData).length > 0) {
          setData(parsedData);
          setError('');
        } else {
          setError('Invalid data format. Please paste valid JSON or key:value pairs.');
        }
      }
    } catch (e) {
      setError('Error processing pasted data. Please check the format.');
      console.error('Error processing paste:', e);
    }
  };

  const copyToClipboard = () => {
    if (!data) return;
    
    // Create header row
    const headers = Object.keys(data);
    // Create data row
    const values = Object.values(data);
    
    // Combine with tab separation for Excel compatibility
    const tableContent = headers.join('\t') + '\n' + values.join('\t');
    
    navigator.clipboard.writeText(tableContent).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const downloadCSV = () => {
    if (!data) return;
    
    const headers = Object.keys(data);
    const values = Object.values(data);
    
    const csvContent = 
      headers.join(',') + '\n' + 
      values.map(value => `"${value}"`).join(',');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'table_data.csv';
    link.click();
  };

  return (
    <div className="space-y-4 p-4">
      {/* Input Area */}
      <div className="mb-4">
        <textarea 
          className="w-full p-4 border rounded-lg min-h-32 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="Paste your JSON or key:value pairs here..."
          onPaste={handlePaste}
        />
        {error && (
          <div className="text-red-500 text-sm mt-2">{error}</div>
        )}
      </div>

      {/* Actions */}
      {data && (
        <div className="flex justify-end gap-2 mb-4">
          <button
            onClick={copyToClipboard}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            {copied ? 'Copied!' : (
              <>
                <Copy className="w-4 h-4" />
                Copy for Excel
              </>
            )}
          </button>
          <button
            onClick={downloadCSV}
            className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
          >
            <Download className="w-4 h-4" />
            Download CSV
          </button>
        </div>
      )}

      {/* Table */}
      {data && (
        <div className="w-full overflow-x-auto border rounded">
          <table className="min-w-full">
            <thead>
              <tr className="bg-gray-50">
                {Object.keys(data).map((key) => (
                  <th key={key} className="border-b border-r px-4 py-2 text-left text-sm font-medium text-gray-900">
                    {key}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr>
                {Object.values(data).map((value, index) => (
                  <td key={index} className="border-r px-4 py-2 text-sm text-gray-500">
                    {value}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default JsonTable;