"use client";

import { useCallback, useRef, useState } from "react";
import { useRouter } from "next/navigation";

type JDTab = "text" | "file" | "url";

export default function UploadPage() {
  const router = useRouter();

  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [resumeDragging, setResumeDragging] = useState(false);
  const [jdTab, setJDTab] = useState<JDTab>("text");
  const [jdText, setJDText] = useState("");
  const [jdFile, setJDFile] = useState<File | null>(null);
  const [jdUrl, setJDUrl] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const resumeInputRef = useRef<HTMLInputElement>(null);
  const jdFileInputRef = useRef<HTMLInputElement>(null);

  const ALLOWED = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"];
  const MAX_MB = 10;

  function validateFile(file: File): string | null {
    if (!ALLOWED.includes(file.type)) return "Only PDF and DOCX files are supported.";
    if (file.size > MAX_MB * 1024 * 1024) return `File must be under ${MAX_MB}MB.`;
    return null;
  }

  const onResumeDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setResumeDragging(false);
    const file = e.dataTransfer.files[0];
    if (!file) return;
    const err = validateFile(file);
    if (err) { setError(err); return; }
    setError(null);
    setResumeFile(file);
  }, []);

  function onResumeChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const err = validateFile(file);
    if (err) { setError(err); return; }
    setError(null);
    setResumeFile(file);
  }

  function onJDFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const err = validateFile(file);
    if (err) { setError(err); return; }
    setError(null);
    setJDFile(file);
  }

  function hasJD(): boolean {
    if (jdTab === "text") return jdText.trim().length > 0;
    if (jdTab === "file") return jdFile !== null;
    return jdUrl.trim().length > 0;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!resumeFile) { setError("Please upload your resume."); return; }
    if (!hasJD()) { setError("Please provide a job description."); return; }

    setSubmitting(true);
    try {
      const form = new FormData();
      form.append("resume_file", resumeFile);
      if (jdTab === "text") form.append("jd_text", jdText);
      else if (jdTab === "file" && jdFile) form.append("jd_file", jdFile);
      else if (jdTab === "url") form.append("jd_url", jdUrl);

      const res = await fetch("http://localhost:8000/api/v1/upload/", {
        method: "POST",
        body: form,
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        const msg = body?.detail?.message ?? body?.detail ?? "Upload failed. Please try again.";
        setError(typeof msg === "string" ? msg : JSON.stringify(msg));
        return;
      }

      const data = await res.json();
      sessionStorage.setItem("session_id", data.session_id);
      sessionStorage.setItem("resume_id", data.resume_id);
      sessionStorage.setItem("jd_id", data.jd_id);
      router.push("/questions");
    } catch {
      setError("Network error. Make sure the backend is running.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-2xl space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Upload your documents</h1>
          <p className="mt-1 text-slate-500">We&apos;ll analyse the fit and generate a personalised action plan.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Resume upload */}
          <section className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 space-y-3">
            <h2 className="font-semibold text-slate-800">Resume</h2>
            <div
              role="button"
              tabIndex={0}
              onClick={() => resumeInputRef.current?.click()}
              onKeyDown={(e) => e.key === "Enter" && resumeInputRef.current?.click()}
              onDragOver={(e) => { e.preventDefault(); setResumeDragging(true); }}
              onDragLeave={() => setResumeDragging(false)}
              onDrop={onResumeDrop}
              className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
                resumeDragging
                  ? "border-blue-400 bg-blue-50"
                  : resumeFile
                  ? "border-green-400 bg-green-50"
                  : "border-slate-200 hover:border-blue-300 hover:bg-slate-50"
              }`}
            >
              {resumeFile ? (
                <div className="space-y-1">
                  <div className="text-green-600 font-medium">{resumeFile.name}</div>
                  <div className="text-sm text-slate-400">{(resumeFile.size / 1024).toFixed(0)} KB — click to replace</div>
                </div>
              ) : (
                <div className="space-y-2">
                  <div className="text-4xl">📄</div>
                  <div className="text-slate-600">Drag & drop or click to upload</div>
                  <div className="text-sm text-slate-400">PDF or DOCX, max 10MB</div>
                </div>
              )}
            </div>
            <input
              ref={resumeInputRef}
              type="file"
              accept=".pdf,.docx"
              className="hidden"
              onChange={onResumeChange}
            />
          </section>

          {/* Job description */}
          <section className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 space-y-4">
            <h2 className="font-semibold text-slate-800">Job description</h2>

            {/* Tabs */}
            <div className="flex gap-1 bg-slate-100 p-1 rounded-lg w-fit">
              {(["text", "file", "url"] as JDTab[]).map((tab) => (
                <button
                  key={tab}
                  type="button"
                  onClick={() => { setJDTab(tab); setError(null); }}
                  className={`px-4 py-1.5 rounded-md text-sm font-medium capitalize transition-colors ${
                    jdTab === tab
                      ? "bg-white text-slate-900 shadow-sm"
                      : "text-slate-500 hover:text-slate-700"
                  }`}
                >
                  {tab === "url" ? "URL" : tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>

            {/* Tab content */}
            {jdTab === "text" && (
              <textarea
                rows={6}
                placeholder="Paste the job description here…"
                value={jdText}
                onChange={(e) => setJDText(e.target.value)}
                className="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
              />
            )}

            {jdTab === "file" && (
              <div>
                <button
                  type="button"
                  onClick={() => jdFileInputRef.current?.click()}
                  className={`w-full border-2 border-dashed rounded-xl p-6 text-center transition-colors ${
                    jdFile
                      ? "border-green-400 bg-green-50"
                      : "border-slate-200 hover:border-blue-300 hover:bg-slate-50"
                  }`}
                >
                  {jdFile ? (
                    <div className="space-y-1">
                      <div className="text-green-600 font-medium">{jdFile.name}</div>
                      <div className="text-sm text-slate-400">click to replace</div>
                    </div>
                  ) : (
                    <div className="space-y-1">
                      <div className="text-slate-600">Click to upload JD file</div>
                      <div className="text-sm text-slate-400">PDF or DOCX, max 10MB</div>
                    </div>
                  )}
                </button>
                <input
                  ref={jdFileInputRef}
                  type="file"
                  accept=".pdf,.docx"
                  className="hidden"
                  onChange={onJDFileChange}
                />
              </div>
            )}

            {jdTab === "url" && (
              <input
                type="url"
                placeholder="https://example.com/job-posting"
                value={jdUrl}
                onChange={(e) => setJDUrl(e.target.value)}
                className="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            )}
          </section>

          {/* Error */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-4 py-3">
              {error}
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={submitting}
            className="w-full py-3 rounded-xl bg-blue-600 text-white font-semibold text-base hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed transition-colors shadow-sm"
          >
            {submitting ? "Uploading…" : "Analyse my fit →"}
          </button>
        </form>
      </div>
    </main>
  );
}
