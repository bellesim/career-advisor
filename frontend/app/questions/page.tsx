"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function QuestionsPage() {
  const router = useRouter();
  const [questions, setQuestions] = useState<string[]>([]);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sessionId = typeof window !== "undefined" ? sessionStorage.getItem("session_id") : null;
  const resumeId = typeof window !== "undefined" ? sessionStorage.getItem("resume_id") : null;
  const jdId = typeof window !== "undefined" ? sessionStorage.getItem("jd_id") : null;

  useEffect(() => {
    if (!sessionId || !resumeId || !jdId) {
      router.replace("/upload");
      return;
    }
    fetch("http://localhost:8000/api/v1/questions/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, resume_id: resumeId, jd_id: jdId }),
    })
      .then((r) => r.json())
      .then((data) => setQuestions(data.questions ?? []))
      .catch(() => setQuestions([]))
      .finally(() => setLoading(false));
  }, []);

  async function handleSubmit(skip = false) {
    setSubmitting(true);
    setError(null);
    try {
      const payload: Record<string, unknown> = {
        session_id: sessionId,
        resume_id: resumeId,
        jd_id: jdId,
      };
      if (!skip && questions.length > 0) {
        payload.answers = questions.map((q, i) => ({
          question: q,
          answer: answers[i] ?? "",
        }));
      }
      const res = await fetch("http://localhost:8000/api/v1/analyze/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        setError("Analysis failed. Please try again.");
        return;
      }
      const data = await res.json();
      router.push(`/report/${data.report_id}`);
    } catch {
      setError("Network error. Make sure the backend is running.");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-slate-500 text-lg animate-pulse">Preparing your analysis…</div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-2xl space-y-8">
        {questions.length === 0 ? (
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-slate-100 text-center space-y-4">
            <div className="text-4xl">🚀</div>
            <h1 className="text-2xl font-bold text-slate-900">Ready to analyse</h1>
            <p className="text-slate-500">No clarifying questions needed. We have everything we need.</p>
            <button
              onClick={() => handleSubmit(true)}
              disabled={submitting}
              className="px-8 py-3 rounded-xl bg-blue-600 text-white font-semibold hover:bg-blue-700 disabled:opacity-60 transition-colors"
            >
              {submitting ? "Analysing…" : "Generate report →"}
            </button>
          </div>
        ) : (
          <>
            <div>
              <h1 className="text-3xl font-bold text-slate-900">A few quick questions</h1>
              <p className="mt-1 text-slate-500">
                Your answers help us give a more accurate analysis. You can skip any question.
              </p>
            </div>
            <div className="space-y-5">
              {questions.map((q, i) => (
                <div key={i} className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 space-y-3">
                  <p className="font-medium text-slate-800">{q}</p>
                  <textarea
                    rows={3}
                    placeholder="Your answer (optional)…"
                    value={answers[i] ?? ""}
                    onChange={(e) => setAnswers((prev) => ({ ...prev, [i]: e.target.value }))}
                    className="w-full border border-slate-200 rounded-xl px-4 py-2 text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
                  />
                </div>
              ))}
            </div>
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-4 py-3">
                {error}
              </div>
            )}
            <div className="flex gap-3">
              <button
                onClick={() => handleSubmit(true)}
                disabled={submitting}
                className="flex-1 py-3 rounded-xl border border-slate-200 text-slate-600 font-medium hover:bg-slate-50 disabled:opacity-60 transition-colors"
              >
                Skip & analyse
              </button>
              <button
                onClick={() => handleSubmit(false)}
                disabled={submitting}
                className="flex-1 py-3 rounded-xl bg-blue-600 text-white font-semibold hover:bg-blue-700 disabled:opacity-60 transition-colors"
              >
                {submitting ? "Analysing…" : "Submit & analyse →"}
              </button>
            </div>
          </>
        )}
      </div>
    </main>
  );
}
