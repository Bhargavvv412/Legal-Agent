// src/App.jsx
import { useState } from "react";

export default function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const askAgent = async () => {
    setLoading(true);
    setAnswer("");
    const res = await fetch("http://localhost:8000/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
    setAnswer(data.answer || data.error);
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center p-8">
      <h1 className="text-3xl font-bold mb-6">⚖️ Indian Legal Advisor AI</h1>
      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask your legal question here..."
        className="w-full max-w-2xl p-3 rounded bg-gray-800 border border-gray-600"
        rows={4}
      />
      <button
        onClick={askAgent}
        disabled={loading || !question}
        className="mt-4 px-6 py-2 bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? "Thinking..." : "Ask"}
      </button>

      {answer && (
        <div className="mt-6 w-full max-w-2xl bg-gray-800 p-4 rounded border border-gray-700">
          <h2 className="text-xl font-semibold mb-2">🧾 Answer:</h2>
          <p className="whitespace-pre-line">{answer}</p>
        </div>
      )}
    </div>
  );
}
