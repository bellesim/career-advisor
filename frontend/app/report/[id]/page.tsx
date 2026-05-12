"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

type CategoryScore = { score: number; weight: number; reasoning: string };
type Gap = { severity: string; area: string; description: string; suggestions: string[] };
type Strength = { area: string; description: string; examples: string[] };
type ActionItem = { action: string; resources: string[] };
type Sprint = {
  sprint: number;
  focus: string;
  tracks: { skills: ActionItem[]; experience: ActionItem[]; credentials: ActionItem[] };
};
type Report = {
  id: string;
  candidate_name: string;
  target_role: string;
  overall_score: number;
  category_scores: Record<string, CategoryScore>;
  gaps: Gap[];
  strengths: Strength[];
  action_plan: { sprints: Sprint[] };
};

const CATEGORY_LABELS: Record<string, string> = {
  software_technical: "Technical Skills",
  domain_knowledge: "Domain Knowledge",
  experience_seniority: "Experience",
  credentials_education: "Education",
  soft_skills_leadership: "Soft Skills",
};

const SEVERITY_COLOUR: Record<string, string> = {
  Critical: "bg-red-100 text-red-700 border-red-200",
  Moderate: "bg-amber-100 text-amber-700 border-amber-200",
  "Nice-to-have": "bg-blue-100 text-blue-700 border-blue-200",
};

function ScoreBar({ score }: { score: number }) {
  const colour = score >= 75 ? "bg-green-500" : score >= 50 ? "bg-amber-500" : "bg-red-500";
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 bg-slate-100 rounded-full h-2">
        <div className={`${colour} h-2 rounded-full transition-all`} style={{ width: `${score}%` }} />
      </div>
      <span className="text-sm font-semibold text-slate-700 w-8 text-right">{score}</span>
    </div>
  );
}

export default function ReportPage() {
  const { id } = useParams<{ id: string }>();
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`http://localhost:8000/api/v1/report/${id}`)
      .then((r) => {
        if (!r.ok) throw new Error("Report not found");
        return r.json();
      })
      .then(setReport)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-slate-500 text-lg animate-pulse">Loading report…</div>
      </main>
    );
  }

  if (error || !report) {
    return (
      <main className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center space-y-4">
          <p className="text-red-600">{error ?? "Report not found"}</p>
          <Link href="/upload" className="text-blue-600 underline">Start again</Link>
        </div>
      </main>
    );
  }

  const scoreColour =
    report.overall_score >= 75 ? "text-green-600" :
    report.overall_score >= 50 ? "text-amber-600" : "text-red-600";

  const criticalGaps = report.gaps.filter((g) => g.severity === "Critical");
  const otherGaps = report.gaps.filter((g) => g.severity !== "Critical");

  return (
    <main className="min-h-screen bg-slate-50 py-10 px-4">
      <div className="max-w-3xl mx-auto space-y-8">

        {/* Header */}
        <div className="bg-white rounded-2xl p-8 shadow-sm border border-slate-100">
          <div className="flex items-start justify-between flex-wrap gap-4">
            <div>
              <p className="text-sm text-slate-400 uppercase tracking-wide">Career Fit Report</p>
              <h1 className="text-2xl font-bold text-slate-900 mt-1">{report.candidate_name}</h1>
              <p className="text-slate-500 mt-0.5">Applying for: <span className="font-medium text-slate-700">{report.target_role}</span></p>
            </div>
            <div className="text-right">
              <div className={`text-6xl font-bold ${scoreColour}`}>{report.overall_score}</div>
              <div className="text-sm text-slate-400">out of 100</div>
            </div>
          </div>
        </div>

        {/* Category scores */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 space-y-4">
          <h2 className="font-semibold text-slate-800 text-lg">Score breakdown</h2>
          {Object.entries(report.category_scores).map(([key, val]) => (
            <div key={key} className="space-y-1">
              <div className="flex justify-between text-sm">
                <span className="text-slate-600">{CATEGORY_LABELS[key] ?? key}</span>
                <span className="text-slate-400 text-xs">{Math.round(val.weight * 100)}% weight</span>
              </div>
              <ScoreBar score={val.score} />
              <p className="text-xs text-slate-400">{val.reasoning}</p>
            </div>
          ))}
        </div>

        {/* Gaps */}
        {report.gaps.length > 0 && (
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 space-y-4">
            <h2 className="font-semibold text-slate-800 text-lg">Gaps to address</h2>
            {[...criticalGaps, ...otherGaps].map((gap, i) => (
              <div key={i} className={`border rounded-xl p-4 space-y-2 ${SEVERITY_COLOUR[gap.severity] ?? "bg-slate-50 border-slate-200 text-slate-700"}`}>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold uppercase tracking-wide">{gap.severity}</span>
                  <span className="font-medium">{gap.area}</span>
                </div>
                <p className="text-sm">{gap.description}</p>
                {gap.suggestions.length > 0 && (
                  <ul className="text-sm list-disc list-inside space-y-0.5 opacity-80">
                    {gap.suggestions.map((s, j) => <li key={j}>{s}</li>)}
                  </ul>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Strengths */}
        {report.strengths.length > 0 && (
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 space-y-4">
            <h2 className="font-semibold text-slate-800 text-lg">Your strengths</h2>
            {report.strengths.map((s, i) => (
              <div key={i} className="border border-green-200 bg-green-50 rounded-xl p-4 space-y-1">
                <div className="font-medium text-green-800">{s.area}</div>
                <p className="text-sm text-green-700">{s.description}</p>
                {s.examples.length > 0 && (
                  <ul className="text-xs text-green-600 list-disc list-inside">
                    {s.examples.map((e, j) => <li key={j}>{e}</li>)}
                  </ul>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Action plan */}
        {report.action_plan?.sprints?.length > 0 && (
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 space-y-6">
            <h2 className="font-semibold text-slate-800 text-lg">90-day action plan</h2>
            {report.action_plan.sprints.map((sprint) => (
              <div key={sprint.sprint} className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-bold">
                    {sprint.sprint}
                  </div>
                  <div>
                    <span className="font-medium text-slate-800">Days {(sprint.sprint - 1) * 30 + 1}–{sprint.sprint * 30}</span>
                    <span className="text-slate-500 ml-2 text-sm">{sprint.focus}</span>
                  </div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pl-11">
                  {(["skills", "experience", "credentials"] as const).map((track) => {
                    const items = sprint.tracks[track];
                    if (!items?.length) return null;
                    return (
                      <div key={track} className="bg-slate-50 rounded-xl p-3 space-y-2">
                        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">{track}</p>
                        {items.map((item, j) => (
                          <div key={j} className="text-sm text-slate-700">
                            <p>{item.action}</p>
                            {item.resources?.length > 0 && (
                              <p className="text-xs text-blue-600 mt-0.5">{item.resources.join(", ")}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="text-center">
          <Link href="/upload" className="text-sm text-slate-400 hover:text-slate-600 underline">
            Analyse another role →
          </Link>
        </div>
      </div>
    </main>
  );
}
