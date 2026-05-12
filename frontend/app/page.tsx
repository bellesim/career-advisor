import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50 px-4">
      <div className="max-w-2xl w-full text-center space-y-8">
        <div className="space-y-3">
          <h1 className="text-5xl font-bold text-slate-900 tracking-tight">
            Career Advisor
          </h1>
          <p className="text-xl text-slate-600">
            Upload your resume and a job description to get an AI-powered gap
            analysis and 90-day action plan.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/upload"
            className="inline-flex items-center justify-center px-8 py-3 rounded-xl bg-blue-600 text-white font-semibold text-lg hover:bg-blue-700 transition-colors shadow-sm"
          >
            Get started →
          </Link>
        </div>

        <div className="grid grid-cols-3 gap-6 pt-8 text-left">
          {[
            { icon: "📄", title: "Upload", body: "Resume + job description" },
            { icon: "🤖", title: "Analyze", body: "AI scores your fit across 5 categories" },
            { icon: "🗺️", title: "Plan", body: "90-day personalised action plan" },
          ].map(({ icon, title, body }) => (
            <div key={title} className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100">
              <div className="text-3xl mb-2">{icon}</div>
              <div className="font-semibold text-slate-800">{title}</div>
              <div className="text-sm text-slate-500 mt-1">{body}</div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
