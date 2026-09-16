from dataclasses import dataclass
from hashlib import sha256
import re

from pydantic import BaseModel

from .config import settings


SKILL_ALIASES: dict[str, tuple[str, ...]] = {
    "Python": ("python",),
    "JavaScript": ("javascript", "js"),
    "TypeScript": ("typescript", "ts"),
    "React": ("react", "react.js", "reactjs"),
    "Node.js": ("node.js", "nodejs", "node"),
    "FastAPI": ("fastapi",),
    "Django": ("django",),
    "Flask": ("flask",),
    "Java": ("java",),
    "Spring": ("spring boot", "spring"),
    "C#": ("c#", "c sharp"),
    ".NET": (".net", "dotnet"),
    "C++": ("c++",),
    "Go": ("golang", "go"),
    "Rust": ("rust",),
    "PHP": ("php",),
    "Laravel": ("laravel",),
    "Ruby": ("ruby",),
    "Rails": ("ruby on rails", "rails"),
    "SQL": ("sql",),
    "PostgreSQL": ("postgresql", "postgres"),
    "MySQL": ("mysql",),
    "MongoDB": ("mongodb", "mongo"),
    "Redis": ("redis",),
    "HTML": ("html", "html5"),
    "CSS": ("css", "css3"),
    "Tailwind CSS": ("tailwind css", "tailwind"),
    "REST APIs": ("rest api", "restful", "rest"),
    "GraphQL": ("graphql",),
    "Docker": ("docker",),
    "Kubernetes": ("kubernetes", "k8s"),
    "AWS": ("amazon web services", "aws"),
    "Azure": ("microsoft azure", "azure"),
    "Google Cloud": ("google cloud platform", "google cloud", "gcp"),
    "Git": ("git",),
    "GitHub Actions": ("github actions",),
    "CI/CD": ("ci/cd", "continuous integration", "continuous delivery"),
    "Linux": ("linux",),
    "Terraform": ("terraform",),
    "Machine Learning": ("machine learning", "ml"),
    "Deep Learning": ("deep learning",),
    "NLP": ("natural language processing", "nlp"),
    "LLMs": ("large language models", "large language model", "llms", "llm"),
    "OpenAI API": ("openai api", "openai"),
    "Pandas": ("pandas",),
    "NumPy": ("numpy",),
    "scikit-learn": ("scikit-learn", "sklearn"),
    "TensorFlow": ("tensorflow",),
    "PyTorch": ("pytorch",),
    "Data Analysis": ("data analysis", "data analytics"),
    "Data Visualization": ("data visualization", "data visualisation"),
    "Power BI": ("power bi", "powerbi"),
    "Tableau": ("tableau",),
    "Excel": ("microsoft excel", "excel"),
    "Agile": ("agile",),
    "Scrum": ("scrum",),
    "Jira": ("jira",),
    "Figma": ("figma",),
    "UX Design": ("user experience", "ux design", "ux"),
    "UI Design": ("user interface", "ui design"),
    "Communication": ("communication",),
    "Leadership": ("leadership",),
    "Problem Solving": ("problem solving", "problem-solving"),
    "Teamwork": ("teamwork", "team player", "collaboration"),
    "Project Management": ("project management",),
    "Product Management": ("product management",),
    "Testing": ("software testing", "unit testing", "testing"),
    "Pytest": ("pytest",),
    "Jest": ("jest",),
    "Playwright": ("playwright",),
    "Cypress": ("cypress",),
    "Microservices": ("microservices", "microservice"),
    "Kafka": ("apache kafka", "kafka"),
    "RabbitMQ": ("rabbitmq",),
    "Celery": ("celery",),
    "Selenium": ("selenium",),
    "Spark": ("apache spark", "spark"),
    "Databricks": ("databricks",),
    "Snowflake": ("snowflake",),
}


class StructuredSkillAnalysis(BaseModel):
    job_skills: list[str]
    cv_skills: list[str]
    strengths: list[str]
    recommendations: list[str]
    summary: str


@dataclass
class AnalysisResult:
    match_score: int
    skill_coverage: int
    matching_skills: list[str]
    missing_skills: list[str]
    cv_skills: list[str]
    job_skills: list[str]
    strengths: list[str]
    recommendations: list[str]
    summary: str
    provider: str
    model: str | None


def description_hash(text: str) -> str:
    return sha256(text.strip().encode("utf-8")).hexdigest()


def contains_alias(text: str, alias: str) -> bool:
    return bool(re.search(rf"(?<![\w+#.]){re.escape(alias)}(?![\w+#.])", text, re.IGNORECASE))


def extract_known_skills(text: str) -> list[str]:
    return [
        skill
        for skill, aliases in SKILL_ALIASES.items()
        if any(contains_alias(text, alias) for alias in aliases)
    ]


def canonical_skill(value: str) -> str:
    cleaned = re.sub(r"\s+", " ", value).strip()
    for skill, aliases in SKILL_ALIASES.items():
        if cleaned.casefold() == skill.casefold() or any(cleaned.casefold() == alias.casefold() for alias in aliases):
            return skill
    return cleaned


def unique_skills(skills: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in skills:
        skill = canonical_skill(value)
        key = skill.casefold()
        if skill and key not in seen:
            seen.add(key)
            result.append(skill)
    return result


def local_extraction(cv_text: str, job_description: str) -> StructuredSkillAnalysis:
    job_skills = extract_known_skills(job_description)
    cv_skills = extract_known_skills(cv_text)
    cv_keys = {skill.casefold() for skill in cv_skills}
    matching = [skill for skill in job_skills if skill.casefold() in cv_keys]
    missing = [skill for skill in job_skills if skill.casefold() not in cv_keys]
    strengths = (
        [f"Your CV demonstrates relevant experience with {skill}." for skill in matching[:3]]
        or ["Your CV contains transferable experience, but the role's named tools need clearer evidence."]
    )
    recommendations = [
        f"If you have used {skill}, add a concrete project or achievement that proves it."
        for skill in missing[:4]
    ]
    if not recommendations:
        recommendations = ["Add measurable outcomes to your strongest role-relevant achievements."]
    coverage = round(len(matching) / len(job_skills) * 100) if job_skills else 0
    summary = (
        f"The CV currently demonstrates {len(matching)} of {len(job_skills)} skills identified in the job description."
        if job_skills
        else "No recognised skills were found in the job description; add a more detailed description and run the analysis again."
    )
    return StructuredSkillAnalysis(
        job_skills=job_skills,
        cv_skills=cv_skills,
        strengths=strengths,
        recommendations=recommendations,
        summary=summary,
    )


def openai_extraction(cv_text: str, job_description: str) -> StructuredSkillAnalysis:
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.parse(
        model=settings.openai_model,
        input=[
            {
                "role": "system",
                "content": (
                    "You are a precise recruitment analyst. Extract explicit technical and professional skills "
                    "from a CV and job description. Give concise evidence-based strengths and actionable CV "
                    "recommendations. Use the same concise canonical label for the same skill in both lists. "
                    "Do not invent experience and do not calculate a match percentage."
                ),
            },
            {
                "role": "user",
                "content": f"JOB DESCRIPTION:\n{job_description[:18000]}\n\nCV:\n{cv_text[:18000]}",
            },
        ],
        text_format=StructuredSkillAnalysis,
    )
    if response.output_parsed is None:
        raise RuntimeError("OpenAI returned no structured analysis")
    return response.output_parsed


def analyse_match(cv_text: str, job_description: str) -> AnalysisResult:
    provider = "local"
    model: str | None = None
    if settings.openai_api_key:
        try:
            extracted = openai_extraction(cv_text, job_description)
            provider = "openai"
            model = settings.openai_model
        except Exception:
            extracted = local_extraction(cv_text, job_description)
            provider = "local_fallback"
    else:
        extracted = local_extraction(cv_text, job_description)

    job_skills = unique_skills(extracted.job_skills)
    cv_skills = unique_skills(extracted.cv_skills)
    cv_keys = {skill.casefold() for skill in cv_skills}
    matching = [skill for skill in job_skills if skill.casefold() in cv_keys]
    missing = [skill for skill in job_skills if skill.casefold() not in cv_keys]
    coverage = round(len(matching) / len(job_skills) * 100) if job_skills else 0

    return AnalysisResult(
        match_score=coverage,
        skill_coverage=coverage,
        matching_skills=matching,
        missing_skills=missing,
        cv_skills=cv_skills,
        job_skills=job_skills,
        strengths=extracted.strengths[:5],
        recommendations=extracted.recommendations[:5],
        summary=extracted.summary,
        provider=provider,
        model=model,
    )
