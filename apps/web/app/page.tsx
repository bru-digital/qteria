export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 flex items-center justify-center">
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <h1 className="text-6xl font-bold text-gray-900 mb-6">
          Qteria
        </h1>
        <p className="text-2xl text-gray-600 mb-4">
          AI-Driven Document Pre-Assessment Platform
        </p>
        <p className="text-lg text-gray-500 mb-8">
          Transform manual compliance checks into AI-powered assessments with evidence-based results in &lt;10 minutes.
        </p>
        <div className="bg-white rounded-lg shadow-lg p-8 text-left">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            Key Features
          </h2>
          <ul className="space-y-3 text-gray-600">
            <li className="flex items-start">
              <span className="text-green-500 mr-2">✓</span>
              <span><strong>Evidence-based validation:</strong> AI links to exact page/section in documents</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-500 mr-2">✓</span>
              <span><strong>Radical simplicity:</strong> workflow → buckets → criteria → validate</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-500 mr-2">✓</span>
              <span><strong>Enterprise data privacy:</strong> Zero-retention AI, SOC2/ISO 27001 compliance</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-500 mr-2">✓</span>
              <span><strong>400x faster:</strong> From 1-2 days to &lt;10 minutes per assessment</span>
            </li>
          </ul>
        </div>
        <div className="mt-8 text-sm text-gray-400">
          <p>MVP in Development | Database Schema ✅ | Next: API Endpoints</p>
        </div>
      </div>
    </div>
  );
}
