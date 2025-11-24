JOB_EXTRACTION_PROMPT = """
Extract structured information from this job posting.

**Job Title:** {title}
**Company:** {company}
**Description:**
{description}

Extract the following (return JSON only):
{{
  "skills": ["skill1", "skill2", ...],
  "years_experience_min": integer or null,
  "years_experience_max": integer or null,
  "education_required": "Bachelor" or "Master" or "PhD" or null,
  "salary_min": integer or null,
  "salary_max": integer or null,
  "visa_sponsorship": boolean,
  "requires_citizenship": boolean,
  "work_authorization": ["H1B", "Green Card", "US Citizen"]
}}

Rules:
- Extract ALL technical skills mentioned (programming languages, frameworks, tools)
- Infer experience from phrases like "3+ years", "5-7 years experience"
- Detect visa keywords: "sponsorship", "H1B", "work authorization", "visa available"
- Citizenship: Look for "US Citizen required", "must be authorized to work"
- Salary: Extract from "$100k-$150k", "100-150K", etc.
- If not found, return null (not "null" string, actual JSON null)

Return ONLY the JSON object, no additional text.
"""
