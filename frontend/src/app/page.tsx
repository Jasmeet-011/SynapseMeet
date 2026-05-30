import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="max-w-3xl w-full text-center space-y-6">
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="w-10 h-10 bg-brand-600 rounded-xl flex items-center justify-center">
            <span className="text-white font-bold text-lg">S</span>
          </div>
          <h1 className="text-4xl font-bold text-white">SynapseMeet</h1>
        </div>

        <p className="text-xl text-gray-400 max-w-xl mx-auto">
          Real-time AI meeting intelligence. Transcribe, summarize, and extract action items
          — automatically, across 40+ languages.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-12 text-left">
          {features.map((f) => (
            <div key={f.title} className="card">
              <div className="text-2xl mb-2">{f.icon}</div>
              <h3 className="font-semibold text-white mb-1">{f.title}</h3>
              <p className="text-sm text-gray-400">{f.description}</p>
            </div>
          ))}
        </div>

        <div className="flex gap-4 justify-center mt-8">
          <Link href="/auth/register" className="btn-primary">
            Get Started Free
          </Link>
          <Link href="/auth/login" className="btn-secondary">
            Sign In
          </Link>
        </div>
      </div>
    </main>
  );
}

const features = [
  {
    icon: "🎙️",
    title: "Live Transcription",
    description: "Real-time speech-to-text with speaker identification across 40+ languages.",
  },
  {
    icon: "🤖",
    title: "AI Summaries",
    description: "GPT-4o generates rolling summaries every 30 seconds during your meeting.",
  },
  {
    icon: "✅",
    title: "Action Items",
    description: "Automatically extract tasks with assignees and deadlines, synced to Jira/Notion.",
  },
  {
    icon: "🔍",
    title: "Semantic Search",
    description: "Search across all past meetings using natural language — powered by vector AI.",
  },
  {
    icon: "🕸️",
    title: "Knowledge Graph",
    description: "Visualize connections between meetings, people, and decisions over time.",
  },
  {
    icon: "📊",
    title: "Team Dynamics",
    description: "Sentiment analysis and participation metrics for every speaker.",
  },
];
