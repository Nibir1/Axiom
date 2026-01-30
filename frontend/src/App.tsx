import React, { useState } from 'react';
import axios from 'axios';
import { Upload, MessageSquare, ShieldCheck, Leaf, AlertTriangle, CheckCircle, Send } from 'lucide-react';

// Strictly typed response from our RAG API
interface ChatResponse {
  answer: string;
  context: Array<{
    text: string;
    score: number;
    metadata: { 
      filename: string; 
      owner: string; 
      quality_score: number 
    };
  }>;
}

interface ChatMessage {
  role: 'user' | 'ai';
  content: string;
  sources?: ChatResponse['context'];
}

function App() {
  // Ingest State
  const [file, setFile] = useState<File | null>(null);
  const [ingestStatus, setIngestStatus] = useState<any>(null);
  const [ingestError, setIngestError] = useState('');
  const [uploading, setUploading] = useState(false);

  // Chat State
  const [query, setQuery] = useState('');
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [thinking, setThinking] = useState(false);

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setIngestError('');
    setIngestStatus(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('owner', 'demo_user@upm.com');
    formData.append('tags', 'demo');

    try {
      const res = await axios.post('http://localhost:8000/api/v1/ingest/file', formData);
      setIngestStatus(res.data);
    } catch (err: any) {
      setIngestError(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    // Add User Message
    const newHistory: ChatMessage[] = [...chatHistory, { role: 'user', content: query }];
    setChatHistory(newHistory);
    setQuery('');
    setThinking(true);

    try {
      // <--- FIX: Applied ChatResponse interface here for type safety
      const res = await axios.post<ChatResponse>('http://localhost:8000/api/v1/chat', {
        query: newHistory[newHistory.length - 1].content,
        limit: 3
      });
      
      // Add AI Response
      setChatHistory([...newHistory, { 
        role: 'ai', 
        content: res.data.answer,
        sources: res.data.context 
      }]);
    } catch (err) {
      setChatHistory([...newHistory, { role: 'ai', content: "Error connecting to Knowledge Base." }]);
    } finally {
      setThinking(false);
    }
  };

  return (
    <div className="h-screen bg-gray-50 flex flex-col font-sans text-gray-800">
      {/* Header */}
      <header className="bg-white border-b px-6 py-3 flex items-center gap-3 shadow-sm z-10">
        <div className="bg-green-50 p-2 rounded text-green-600">
          <Leaf size={20} />
        </div>
        <div>
          <h1 className="font-bold text-lg leading-tight">Axiom <span className="text-gray-400 font-normal">| Knowledge Governance</span></h1>
          <p className="text-xs text-green-700 font-medium">Powered by Green AI & GPT-4o</p>
        </div>
      </header>

      <main className="flex-1 flex overflow-hidden">
        
        {/* LEFT PANEL: Ingestion */}
        <div className="w-1/3 min-w-[350px] bg-white border-r border-gray-200 flex flex-col">
          <div className="p-6 bg-gray-50 border-b">
            <h2 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4 flex items-center gap-2">
              <ShieldCheck size={16} /> Data Governance
            </h2>
            
            <form onSubmit={handleIngest} className="space-y-4">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:bg-white hover:border-green-500 transition cursor-pointer relative group">
                <input 
                  type="file" 
                  accept=".pdf"
                  onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
                  className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                />
                <div className="pointer-events-none">
                  <Upload className="mx-auto text-gray-400 mb-2 group-hover:text-green-500" size={24} />
                  <p className="text-sm font-medium text-gray-700 truncate">
                    {file ? file.name : "Drop PDF here to Ingest"}
                  </p>
                </div>
              </div>
              <button 
                type="submit" 
                disabled={!file || uploading}
                className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 rounded-lg text-sm transition disabled:opacity-50"
              >
                {uploading ? "Running Governance Checks..." : "Audit & Index Document"}
              </button>
            </form>
          </div>

          <div className="flex-1 p-6 overflow-y-auto">
            {ingestError && (
              <div className="bg-red-50 border border-red-100 rounded-lg p-4 animate-in fade-in slide-in-from-top-4">
                <div className="flex items-center gap-2 text-red-800 font-bold text-sm mb-1">
                  <AlertTriangle size={16} /> Governance Rejection
                </div>
                <p className="text-xs text-red-600 leading-relaxed">{ingestError}</p>
              </div>
            )}

            {ingestStatus && (
              <div className="bg-green-50 border border-green-100 rounded-lg p-4 animate-in fade-in slide-in-from-top-4">
                <div className="flex items-center gap-2 text-green-800 font-bold text-sm mb-2">
                  <CheckCircle size={16} /> Asset Secured
                </div>
                <div className="grid grid-cols-2 gap-2 mb-3">
                  <div className="bg-white p-2 rounded border border-green-100">
                    <p className="text-[10px] text-gray-500 uppercase">Density Score</p>
                    <p className="text-lg font-bold text-green-700">{(ingestStatus.quality_score * 100).toFixed(1)}%</p>
                  </div>
                  <div className="bg-white p-2 rounded border border-green-100">
                    <p className="text-[10px] text-gray-500 uppercase">Status</p>
                    <p className="text-xs font-bold text-green-700">Indexed</p>
                  </div>
                </div>
                <div className="text-xs text-green-700 space-y-1">
                  <p>• PII Redaction: {ingestStatus.pii_redacted ? "Applied" : "None Found"}</p>
                  <p>• Vector ID: {ingestStatus.id.slice(0, 8)}...</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* RIGHT PANEL: Chat */}
        <div className="flex-1 flex flex-col bg-gray-50/50">
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {chatHistory.length === 0 && (
              <div className="h-full flex flex-col items-center justify-center text-gray-400 opacity-60">
                <MessageSquare size={48} className="mb-4" />
                <p>Axiom RAG Assistant</p>
                <p className="text-sm">Upload a document to start chatting</p>
              </div>
            )}
            
            {chatHistory.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] rounded-2xl p-4 shadow-sm ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 text-white rounded-br-none' 
                    : 'bg-white border border-gray-100 text-gray-800 rounded-bl-none'
                }`}>
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                  
                  {/* Sources Footnote */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-gray-100">
                      <p className="text-[10px] font-bold text-gray-400 uppercase mb-2">Sources</p>
                      <div className="flex gap-2 overflow-x-auto pb-1">
                        {msg.sources.map((src, i) => (
                          <div key={i} className="flex-shrink-0 w-48 bg-gray-50 p-2 rounded border border-gray-200 text-xs">
                             <p className="font-semibold text-gray-700 truncate">{src.metadata.filename}</p>
                             <p className="text-gray-500 text-[10px]">Score: {src.score.toFixed(2)}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {thinking && (
              <div className="flex justify-start">
                 <div className="bg-white border border-gray-100 rounded-2xl p-4 flex gap-2 items-center">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150" />
                 </div>
              </div>
            )}
          </div>

          <div className="p-4 bg-white border-t">
            <form onSubmit={handleChat} className="relative">
              <input 
                type="text" 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask specific questions about the uploaded content..."
                className="w-full pl-4 pr-12 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-green-500 focus:bg-white transition outline-none"
              />
              <button 
                type="submit"
                disabled={!query.trim() || thinking} 
                className="absolute right-2 top-2 p-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50"
              >
                <Send size={18} />
              </button>
            </form>
          </div>
        </div>

      </main>
    </div>
  );
}

export default App;