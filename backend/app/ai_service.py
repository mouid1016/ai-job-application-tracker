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


class InterviewQuestion(BaseModel):
    question: str
    why_asked: str
    answer_framework: str
    talking_points: list[str]


class StructuredApplicationKit(BaseModel):
    cover_letter: str
    elevator_pitch: str
    interview_questions: list[InterviewQuestion]
    questions_to_ask: list[str]


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


@dataclass
class ApplicationKitResult:
    cover_letter: str
    elevator_pitch: str
    interview_questions: list[dict[str, object]]
    questions_to_ask: list[str]
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


def local_application_kit(
    candidate_name: str,
    company: str,
    role: str,
    matching_skills: list[str],
    missing_skills: list[str],
) -> StructuredApplicationKit:
    skills = matching_skills[:4]
    skills_text = ", ".join(skills) if skills else "relevant transferable experience"
    first_skill = skills[0] if skills else "problem solving"
    development_skill = missing_skills[0] if missing_skills else "a new technology"
    cover_letter = (
        "Dear Hiring Team,\n\n"
        f"I am writing to apply for the {role} position at {company}. The opportunity stands out to me "
        "because it combines practical delivery with the chance to contribute to a strong engineering team.\n\n"
        f"My CV demonstrates experience with {skills_text}. I would bring this foundation to the role while "
        "continuing to learn the tools and domain knowledge that matter most to your team. I take a structured "
        "approach to solving problems, communicate clearly, and focus on producing reliable work.\n\n"
        f"I would welcome the opportunity to discuss how my experience and motivation could support {company}. "
        "Thank you for considering my application.\n\n"
        f"Kind regards,\n{candidate_name}"
    )
    elevator_pitch = (
        f"I'm {candidate_name}, and I'm applying for the {role} role at {company}. My background includes "
        f"{skills_text}, and I enjoy turning requirements into clear, reliable solutions. I'm particularly "
        "interested in this opportunity because it would let me contribute those strengths while growing with the team."
    )
    questions = [
        InterviewQuestion(
            question="Tell me about yourself and why this role interests you.",
            why_asked="Tests whether you can connect your experience, motivation, and career direction to the role.",
            answer_framework="Present → Past → Future: current focus, relevant evidence, then why this role is the logical next step.",
            talking_points=[f"Interest in the {role} position", f"Relevant strengths: {skills_text}", f"Why {company} fits your goals"],
        ),
        InterviewQuestion(
            question=f"Describe a project where you used {first_skill} to solve a meaningful problem.",
            why_asked=f"Looks for practical evidence behind the {first_skill} skill shown on your CV.",
            answer_framework="Use STAR: situation, your specific task, actions you personally took, and a measurable result.",
            talking_points=["Clarify your individual contribution", "Explain one technical decision", "Quantify the outcome where possible"],
        ),
        InterviewQuestion(
            question="Tell me about a difficult technical or project challenge you overcame.",
            why_asked="Assesses problem solving, ownership, and how you respond when the first approach does not work.",
            answer_framework="Set the context briefly, explain the obstacle, compare the options you considered, and finish with the result and lesson.",
            talking_points=["Show your reasoning", "Mention collaboration when relevant", "State what you would repeat or improve"],
        ),
        InterviewQuestion(
            question="How do you make sure your work is reliable and maintainable?",
            why_asked="Explores engineering discipline, quality standards, and awareness of future teammates.",
            answer_framework="Give a concrete workflow covering planning, small changes, testing, review, documentation, and monitoring.",
            talking_points=["Testing strategy", "Readable code and documentation", "Feedback and code review"],
        ),
        InterviewQuestion(
            question=f"How would you get productive with {development_skill} if the role required it?",
            why_asked="Checks learning speed and honesty about a skill that is not currently evidenced on the CV.",
            answer_framework="Acknowledge the gap, relate it to something you already know, and give a time-boxed learning and practice plan.",
            talking_points=["Be honest about current level", "Describe a hands-on learning project", "Explain how you would ask for feedback"],
        ),
        InterviewQuestion(
            question="Describe a time you worked with others to deliver under a deadline.",
            why_asked="Assesses communication, prioritisation, and dependable teamwork.",
            answer_framework="Use STAR and focus on how you coordinated work, raised risks early, and protected the most important outcome.",
            talking_points=["Your role in the team", "How priorities were agreed", "The final outcome and lesson"],
        ),
    ]
    return StructuredApplicationKit(
        cover_letter=cover_letter,
        elevator_pitch=elevator_pitch,
        interview_questions=questions,
        questions_to_ask=[
            f"What would success look like in the first three months for the {role} position?",
            "What are the most important technical or product challenges the team is working on now?",
            "How does the team support feedback, learning, and career development?",
            "What distinguishes people who perform especially well on this team?",
        ],
    )


def openai_application_kit(
    candidate_name: str,
    company: str,
    role: str,
    cv_text: str,
    job_description: str,
    matching_skills: list[str],
    missing_skills: list[str],
) -> StructuredApplicationKit:
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.parse(
        model=settings.openai_model,
        input=[
            {
                "role": "system",
                "content": (
                    "You are an expert career coach. Produce a truthful, concise application toolkit grounded only "
                    "in the supplied CV and job description. Never invent experience, qualifications, metrics, names, "
                    "or enthusiasm about facts not provided. The cover letter should be 250-350 words and use UK "
                    "English. Create exactly six diverse interview questions with useful answer frameworks and exactly "
                    "four thoughtful questions for the candidate to ask the employer."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"CANDIDATE: {candidate_name}\nCOMPANY: {company}\nROLE: {role}\n"
                    f"MATCHING SKILLS: {', '.join(matching_skills)}\nMISSING SKILLS: {', '.join(missing_skills)}\n\n"
                    f"JOB DESCRIPTION:\n{job_description[:16000]}\n\nCV:\n{cv_text[:16000]}"
                ),
            },
        ],
        text_format=StructuredApplicationKit,
    )
    if response.output_parsed is None:
        raise RuntimeError("OpenAI returned no structured application toolkit")
    return response.output_parsed


def generate_application_kit(
    candidate_name: str,
    company: str,
    role: str,
    cv_text: str,
    job_description: str,
    matching_skills: list[str],
    missing_skills: list[str],
) -> ApplicationKitResult:
    provider = "local"
    model: str | None = None
    if settings.openai_api_key:
        try:
            generated = openai_application_kit(
                candidate_name,
                company,
                role,
                cv_text,
                job_description,
                matching_skills,
                missing_skills,
            )
            provider = "openai"
            model = settings.openai_model
        except Exception:
            generated = local_application_kit(candidate_name, company, role, matching_skills, missing_skills)
            provider = "local_fallback"
    else:
        generated = local_application_kit(candidate_name, company, role, matching_skills, missing_skills)

    return ApplicationKitResult(
        cover_letter=generated.cover_letter.strip(),
        elevator_pitch=generated.elevator_pitch.strip(),
        interview_questions=[question.model_dump(mode="json") for question in generated.interview_questions[:6]],
        questions_to_ask=generated.questions_to_ask[:4],
        provider=provider,
        model=model,
    )
