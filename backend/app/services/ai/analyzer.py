import json
import re

from openai import OpenAI

from app.core.config import settings

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
        )
    return _client


def _parse_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group())
    return json.loads(text)


QUESTIONS_PROMPT = """\
You are a career advisor. Given a resume and job description, identify up to 3 short clarifying questions that would meaningfully improve a gap analysis. Only ask if something is genuinely ambiguous or missing.

Resume:
{resume_text}

Job Description:
{jd_text}

Return ONLY a JSON object: {{"questions": ["question1", "question2"]}}
Return {{"questions": []}} if no clarification is needed."""


ANALYSIS_PROMPT = """\
You are an expert career advisor. Analyse the fit between this resume and job description and return a structured JSON report.

Resume:
{resume_text}

Job Description:
{jd_text}

{answers_block}

Return ONLY a valid JSON object with this exact structure (no markdown, no explanation):
{{
  "candidate_name": "<full name from resume or 'Unknown'>",
  "target_role": "<job title from JD>",
  "overall_score": <integer 0-100, weighted sum of category scores>,
  "category_scores": {{
    "software_technical":      {{"score": <0-100>, "weight": 0.35, "reasoning": "<2-3 sentences>"}},
    "domain_knowledge":        {{"score": <0-100>, "weight": 0.25, "reasoning": "<2-3 sentences>"}},
    "experience_seniority":    {{"score": <0-100>, "weight": 0.20, "reasoning": "<2-3 sentences>"}},
    "credentials_education":   {{"score": <0-100>, "weight": 0.10, "reasoning": "<2-3 sentences>"}},
    "soft_skills_leadership":  {{"score": <0-100>, "weight": 0.10, "reasoning": "<2-3 sentences>"}}
  }},
  "gaps": [
    {{"severity": "Critical|Moderate|Nice-to-have", "area": "<skill/area>", "description": "<what is missing>", "suggestions": ["<actionable suggestion>"]}}
  ],
  "strengths": [
    {{"area": "<skill/area>", "description": "<why it is a strength>", "examples": ["<specific example from resume>"]}}
  ],
  "action_plan": {{
    "sprints": [
      {{
        "sprint": 1,
        "duration_days": 30,
        "focus": "<theme for this sprint>",
        "tracks": {{
          "skills":      [{{"action": "<what to do>", "resources": ["<course or resource name>"]}}],
          "experience":  [{{"action": "<what to do>", "resources": ["<suggestion>"]}}],
          "credentials": [{{"action": "<what to do>", "resources": ["<certification or course>"]}}]
        }}
      }},
      {{"sprint": 2, "duration_days": 30, "focus": "<theme>", "tracks": {{"skills": [], "experience": [], "credentials": []}}}},
      {{"sprint": 3, "duration_days": 30, "focus": "<theme>", "tracks": {{"skills": [], "experience": [], "credentials": []}}}}
    ]
  }}
}}"""


def generate_questions(resume_text: str, jd_text: str) -> list[str]:
    prompt = QUESTIONS_PROMPT.format(
        resume_text=resume_text[:6000],
        jd_text=jd_text[:3000],
    )
    try:
        resp = _get_client().chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        data = _parse_json(resp.choices[0].message.content)
        return data.get("questions", [])[:3]
    except Exception:
        return []


def analyze(resume_text: str, jd_text: str, answers: list[dict] | None = None) -> dict:
    answers_block = ""
    if answers:
        lines = "\n".join(
            f"Q: {a['question']}\nA: {a['answer']}" for a in answers
        )
        answers_block = f"Additional context from candidate:\n{lines}\n"

    prompt = ANALYSIS_PROMPT.format(
        resume_text=resume_text[:6000],
        jd_text=jd_text[:3000],
        answers_block=answers_block,
    )
    resp = _get_client().chat.completions.create(
        model=settings.OPENROUTER_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return _parse_json(resp.choices[0].message.content)
