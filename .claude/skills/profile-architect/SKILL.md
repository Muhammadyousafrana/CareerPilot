---
name: profile-architect
description: Extract and structure resume data into a master job seeker profile. Use this skill whenever someone uploads a resume (PDF/DOCX/TXT), wants to parse their CV, needs to create a structured profile for job applications, mentions updating their job search profile, or asks to analyze their resume for job hunting. Also trigger when building a job application system, automating applications, or setting up career search tools.
---

# Profile Architect

Transforms raw resume files into structured, machine-readable profiles optimized for automated job applications and matching.

## When to Use

- User uploads a resume file (any format: PDF, DOCX, TXT)
- User says "parse my resume", "extract my info", "build my profile"
- Setting up automated job application workflows
- User wants to analyze their resume for job searching
- Building a structured candidate profile

## Core Workflow

### Phase 1: Resume Extraction

**Input Detection**
```python
# Check for uploaded resume
resume_path = find_resume_in_uploads()
# Supports: .pdf, .docx, .doc, .txt, .rtf
```

**Text Extraction by Format**
- **PDF**: Use `pdfplumber` for text extraction
  ```python
  import pdfplumber
  with pdfplumber.open(resume_path) as pdf:
      text = "\\n".join(page.extract_text() for page in pdf.pages)
  ```
- **DOCX**: Use `python-docx`
  ```python
  from docx import Document
  doc = Document(resume_path)
  text = "\\n".join(para.text for para in doc.paragraphs)
  ```
- **TXT**: Direct read with encoding detection

### Phase 2: Intelligent Parsing

Parse the extracted text into structured sections. Use pattern matching and NLP to identify:

**Personal Information**
- Full name (typically at top of resume)
- Email address (regex: `[\w\.-]+@[\w\.-]+\.\w+`)
- Phone number (various formats)
- LinkedIn URL (`linkedin.com/in/[username]`)
- GitHub, portfolio, or personal website
- Location/Address

**Professional Summary**
- Extract opening paragraph or "Summary" section
- Identify current/most recent title
- Calculate total years of experience

**Experience Section**
- For each job entry extract:
  - Job title
  - Company name
  - Dates (start/end, convert to months)
  - Location
  - Bullet points of responsibilities/achievements
- Calculate: `experience_years = total_months / 12`

**Skills**
- Extract from dedicated "Skills" section
- Also mine from job descriptions (action verbs + tech terms)
- Categorize: technical, soft, tools, languages, frameworks
- Clean and deduplicate (case-insensitive)

**Education**
- Degree(s) and major(s)
- Institution name
- Graduation year
- GPA (if present)

**Certifications & Awards** (if present)

### Phase 3: Profile Structuring

Build the master profile JSON with this exact schema:

```json
{
  "personal": {
    "name": "Sarah Chen",
    "email": "sarah.chen@email.com",
    "phone": "+1-555-0100",
    "linkedin": "linkedin.com/in/sarahchen",
    "github": "github.com/sarahchen",
    "location": "San Francisco, CA",
    "portfolio": "sarahchen.dev"
  },
  "professional": {
    "current_title": "Senior Software Engineer",
    "experience_years": 6.5,
    "summary": "Full-stack engineer with 6+ years building scalable systems...",
    "skills": {
      "technical": ["Python", "JavaScript", "React", "Node.js", "AWS", "Docker"],
      "frameworks": ["Django", "Flask", "Express.js", "Next.js"],
      "databases": ["PostgreSQL", "MongoDB", "Redis"],
      "soft_skills": ["Team leadership", "Agile", "Cross-functional collaboration"]
    },
    "industries": ["fintech", "saas", "healthcare"],
    "companies": [
      {
        "name": "Tech Corp",
        "title": "Senior Software Engineer",
        "start_date": "2021-03",
        "end_date": "present",
        "duration_months": 36,
        "achievements": [
          "Led migration to microservices architecture serving 2M users",
          "Reduced API latency by 40% through optimization",
          "Mentored team of 4 junior engineers"
        ]
      }
    ]
  },
  "education": [
    {
      "degree": "B.S. Computer Science",
      "institution": "University of California, Berkeley",
      "graduation_year": 2018,
      "gpa": "3.8"
    }
  ],
  "preferences": {
    "target_roles": ["Staff Engineer", "Engineering Manager", "Tech Lead"],
    "location_preference": "Remote / San Francisco Bay Area",
    "salary_min": 180000,
    "salary_max": 250000,
    "company_size": ["startup", "mid-size"],
    "company_stage": ["Series B+", "growth"],
    "industries": ["fintech", "developer tools", "infrastructure"]
  },
  "search_signal": {
    "keywords": ["staff engineer", "platform engineering", "distributed systems", "backend"],
    "required_terms": ["python", "cloud", "api"],
    "exclude_terms": ["frontend-only", "wordpress", "embedded systems"],
    "seniority": ["senior", "staff", "principal"]
  }
}
```

### Phase 4: Validation & Gap Filling

**Critical Field Validation**
```python
REQUIRED_FIELDS = [
    "personal.name",
    "personal.email",
    "professional.experience_years",
    "professional.skills.technical"
]

missing = validate_profile(profile, REQUIRED_FIELDS)
```

**Human-in-the-Loop for Missing Fields**
If critical fields are missing, PAUSE and ask the user:
```
I couldn't find your email address in the resume. 
What email should I use for job applications?

[ ] sarah@gmail.com
[ ] sarah.chen@pm.me
[ ] Other: ___________
```

**Preference Inference**
If `preferences` section is not in resume, infer reasonable defaults:
- `target_roles`: Same as current title + one level up
- `location_preference`: Same as current location + "Remote"
- `salary_min`: Industry standard for current title + 10%
- `company_size`: Infer from current company

Then ASK user to confirm/edit preferences:
```
Based on your profile, I've set these job search preferences:
• Target roles: Senior Engineer, Staff Engineer
• Location: Remote or NYC
• Salary range: $180K - $250K
• Company size: Startup to mid-size

Would you like to adjust any of these? [Edit Preferences]
```

### Phase 5: Output Generation

**Save Master Profile**
```python
import json
profile_path = "/home/claude/master_profile.json"
with open(profile_path, 'w') as f:
    json.dump(profile, f, indent=2)
```

**Generate Summary Stats**
```
✓ Profile Created Successfully

📊 Profile Summary:
• Name: Sarah Chen
• Experience: 6.5 years
• Skills: 24 technical skills extracted
• Previous roles: 3 companies
• Education: B.S. Computer Science, UC Berkeley

🎯 Job Search Configuration:
• Target: Staff Engineer, Engineering Manager
• Location: Remote / SF Bay Area
• Salary: $180K - $250K

📁 Files created:
• master_profile.json

Next step: Run Job Intelligence agent to find matching positions
```

## Edge Cases & Handling

**No Resume File Found**
```
I don't see a resume file uploaded. Please upload your resume as:
• PDF (.pdf)
• Word document (.docx)
• Plain text (.txt)

Or you can paste your resume text directly.
```

**Multiple Resume Files**
Ask user which one to use, or use the most recently uploaded.

**Corrupted/Unreadable File**
```
I had trouble reading your resume file. The text extraction failed.
Could you:
1. Re-upload the file
2. Try a different format (PDF → DOCX or vice versa)
3. Or paste the text directly
```

**Very Short Resume (< 100 words)**
Flag as incomplete and ask if this is the full resume.

**Non-English Resume**
Detect language, inform user. Ask if they want to proceed or translate first.

**Unusual Formatting**
If structure doesn't match typical resume format:
- Extract what's possible
- Flag uncertain fields
- Show user the parsed result for confirmation

## Tools Required

- **Filesystem**: Read uploaded files from `/mnt/user-data/uploads`
- **Python Libraries**:
  - `pdfplumber` - PDF text extraction
  - `python-docx` - DOCX parsing
  - `re` - Regex for contact info
  - `json` - Profile serialization
- **Code Execution**: Run Python parsing scripts

## Success Criteria

✅ All critical fields extracted (name, email, skills, experience)
✅ Profile JSON validates against schema
✅ User confirms preferences are accurate
✅ `master_profile.json` saved and ready for next agent

## Integration Point

**Handoff to Orchestrator**
```json
{
  "agent": "profile-architect",
  "status": "complete",
  "output": {
    "profile_path": "/home/claude/master_profile.json",
    "completeness": 0.95,
    "missing_fields": [],
    "user_confirmed": true
  }
}
```

The orchestrator will then pass this profile to the Job Intelligence agent.
