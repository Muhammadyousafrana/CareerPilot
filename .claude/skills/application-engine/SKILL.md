---
name: application-engine
description: Tailor resumes to specific job descriptions and execute job applications through email, forms, or easy-apply. Use this skill whenever someone needs to customize their resume for a job, apply to positions, submit applications, send application emails, fill out job forms, or automate the application process. Also trigger when building application workflows, submitting to multiple jobs, or when the user says "apply to this job", "send my application", or "tailor my resume for this position".
---

# Application Engine

Intelligent resume tailoring and multi-method application submission system. Operates per-job with human checkpoints.

## When to Use

- User wants to apply to a job or multiple jobs
- User needs resume customized for a specific position
- Submitting applications via email, form, or LinkedIn Easy Apply
- Automating application workflows
- User says "apply to these jobs", "send my resume", "fill out the application"

## Core Workflow

This agent runs as **one instance per job** - can be parallelized for multiple applications.

### Input Requirements

```python
# Required inputs
master_profile = json.load("master_profile.json")
job = {
    "job_id": "j001",
    "title": "Staff Backend Engineer",
    "company": "Acme Corp",
    "full_jd": "...",  # Complete job description
    "requirements": [...],
    "apply_method": "email",  # or "form" or "easy_apply"
    "recruiter_email": "hiring@acme.com",  # if email method
    "apply_url": "...",  # if form/easy_apply method
}
```

---

## PHASE 1: Resume Intelligence

### Step 1: Gap Analysis

Compare profile against job requirements to identify:

```python
def analyze_gaps(profile, job_requirements):
    profile_skills = set(profile["professional"]["skills"]["technical"])
    
    # Extract required skills from JD
    jd_skills = extract_skills(job_requirements)
    
    return {
        "missing_hard": jd_skills - profile_skills,
        "missing_soft": extract_soft_skills(job) - extract_soft_skills(profile),
        "strengths_to_surface": profile_skills & jd_skills,
        "buried_experience": find_relevant_but_buried(profile, job)
    }
```

**Missing Skills Strategy**
- Don't fabricate experience
- If profile has related experience, reframe it
- Example: JD wants "Kubernetes" → profile has "Docker containerization" → surface container experience more prominently

### Step 2: Strategic Rewrite

**Resume Tailoring Rules**

1. **Mirror JD Language** (Most Important)
   - If JD says "distributed systems", use "distributed systems" (not "microservices")
   - Match their exact tech stack terms
   - Use their action verbs ("architected", "scaled", "led")

2. **Reorder Sections**
   - Most relevant experience first
   - If JD emphasizes leadership, lead with management bullet points
   - If technical, lead with architecture/systems work

3. **Update Summary**
   ```python
   # Original: "Software Engineer with 6 years of experience..."
   # Tailored: "Staff Backend Engineer with 6 years building distributed systems..."
   ```
   
   Match the target title EXACTLY.

4. **Surface Buried Experience**
   - Profile might have relevant work in older roles
   - Promote it to a more prominent position
   - Example: Kubernetes mentioned in 2020 job → add to current role too

5. **Quantify Everything**
   - "Improved performance" → "Reduced latency by 40%"
   - "Led team" → "Led team of 4 engineers"
   - If numbers aren't in original resume, don't invent them

6. **Constraints**
   - Max 30% change from original resume
   - Never fabricate job titles, companies, or dates
   - Can only rephrase actual experience
   - Must pass "truth test" - user should recognize all claims

**Rewrite Strategy Decision Tree**
```
IF jd_requires_skill NOT in profile:
    IF profile has related_experience:
        → Reframe related experience to highlight it
    ELSE:
        → Skip this bullet, focus on other strengths
        
IF jd_emphasizes_leadership AND profile.has_management_exp:
    → Promote leadership bullets to top
    
IF jd_emphasizes_technical AND profile.has_deep_tech:
    → Promote architecture/systems bullets to top
```

### Step 3: Generate Tailored Resume

**Output Formats**
Generate BOTH formats (some ATS require specific formats):
1. `tailored_resume_j001.pdf` - Main submission format
2. `tailored_resume_j001.docx` - ATS-friendly fallback

**Resume Generation Code**

```python
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_docx(profile, job, tailoring_strategy):
    doc = Document()
    
    # Header with contact info
    header = doc.add_paragraph()
    header.add_run(profile["personal"]["name"]).bold = True
    # ... add email, phone, linkedin
    
    # Professional Summary (tailored)
    summary = generate_tailored_summary(profile, job)
    doc.add_heading("Professional Summary", level=2)
    doc.add_paragraph(summary)
    
    # Experience (reordered + rewritten)
    doc.add_heading("Experience", level=2)
    for role in reorder_experience(profile, job):
        doc.add_heading(f"{role['title']} - {role['company']}", level=3)
        doc.add_paragraph(f"{role['start_date']} - {role['end_date']}")
        
        # Rewritten bullets
        for bullet in tailor_bullets(role, job):
            p = doc.add_paragraph(bullet, style='List Bullet')
    
    # Skills (prioritized for this JD)
    doc.add_heading("Skills", level=2)
    prioritized_skills = prioritize_skills(profile, job)
    doc.add_paragraph(", ".join(prioritized_skills))
    
    # Education
    doc.add_heading("Education", level=2)
    for edu in profile["education"]:
        doc.add_paragraph(f"{edu['degree']} - {edu['institution']}")
    
    # Save
    doc.save(f"/home/claude/tailored_resume_{job['job_id']}.docx")
```

**PDF Generation**
Convert DOCX to PDF or generate directly with reportlab.

**ATS Optimization**
- Use standard section headers
- Avoid tables, columns, graphics (except in header)
- Use standard fonts (Arial, Calibri, Times)
- Include keywords from JD naturally
- Save with descriptive filename: `Sarah_Chen_Staff_Engineer_Acme.pdf`

### Step 4: Cover Letter Generation

**Personalized Cover Letter Template**

```
Dear Hiring Manager at {company},

I am writing to express my interest in the {title} position. With {experience_years} years of experience in {relevant_areas}, I am excited about the opportunity to contribute to {company}'s mission of {mission_from_research}.

{Paragraph 2: Specific connection to JD}
Your requirements for {key_requirement_1} and {key_requirement_2} align perfectly with my background. At {recent_company}, I {specific_achievement_that_matches_JD}. This experience has prepared me to {desired_outcome_from_JD}.

{Paragraph 3: Why this company}
I am particularly drawn to {company} because {specific_reason_from_research}. I noticed {something_specific_about_company} and believe my expertise in {strength} would be valuable to your team.

{Paragraph 4: Call to action}
I would welcome the opportunity to discuss how my background in {key_skills} can contribute to {company}'s goals. Thank you for considering my application.

Best regards,
{name}
```

**Research for Personalization**
```python
# Quick web search for company info
company_info = web_search(f"{job['company']} mission recent news")
# Extract: mission statement, recent launches, culture values
```

**Save Cover Letter**
```python
with open(f"/home/claude/cover_letter_{job['job_id']}.txt", 'w') as f:
    f.write(cover_letter)
```

---

## PHASE 2: Application Execution

Route to appropriate method based on `job["apply_method"]`

### ROUTE A: Email Application

**When to Use**: `apply_method == "email"`

**Step 1: Compose Email**

```python
email_body = f"""
Subject: Application for {job['title']} Position

Dear {hiring_manager_name or 'Hiring Manager'},

I am excited to apply for the {job['title']} position at {job['company']}. 

{brief_connection_to_company}

Key highlights that match your requirements:
• {highlight_1_matching_jd}
• {highlight_2_matching_jd}  
• {highlight_3_matching_jd}

I have attached my resume for your review. I would welcome the opportunity to discuss how my background in {key_skills} aligns with {company}'s goals.

Thank you for your consideration.

Best regards,
{profile['personal']['name']}
{profile['personal']['phone']}
{profile['personal']['linkedin']}
"""
```

**Step 2: Attach Resume**
```python
attachments = [
    f"/home/claude/tailored_resume_{job['job_id']}.pdf",
    f"/home/claude/cover_letter_{job['job_id']}.txt"  # optional
]
```

**Step 3: HUMAN CHECKPOINT**
```
📧 Email Application Ready for Review

To: hiring@acme.com
Subject: Application for Staff Backend Engineer Position

[Show full email body]

Attachments:
✓ Sarah_Chen_Staff_Engineer_Acme.pdf (142 KB)
✓ cover_letter_j001.txt (1.2 KB)

Review the email above. You can:
• ✅ Send as-is
• ✏️ Edit email body
• 📎 Remove cover letter attachment
• ❌ Cancel application

[Send] [Edit] [Cancel]
```

**Step 4: Send via Gmail MCP**
```python
# Requires Gmail MCP integration
gmail.send_email(
    to=job["recruiter_email"],
    subject=f"Application for {job['title']} Position",
    body=email_body,
    attachments=attachments
)
```

**Step 5: Log Result**
```python
log_application({
    "job_id": job["job_id"],
    "method": "email",
    "status": "sent",
    "sent_at": datetime.now().isoformat(),
    "sent_to": job["recruiter_email"],
    "attachments": attachments
})
```

### ROUTE B: Form Fill Application

**When to Use**: `apply_method == "form"`

**Step 1: Navigate to Form**
```python
# Use Playwright MCP
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Show for user
    page = browser.new_page()
    page.goto(job["apply_url"])
```

**Step 2: Analyze Form Fields**
```python
# Take DOM snapshot
fields = page.evaluate("""
    () => {
        const inputs = document.querySelectorAll('input, textarea, select');
        return Array.from(inputs).map(el => ({
            id: el.id,
            name: el.name,
            type: el.type,
            label: el.labels?.[0]?.textContent || el.placeholder,
            required: el.required,
            options: el.tagName === 'SELECT' 
                ? Array.from(el.options).map(o => o.text)
                : null
        }));
    }
""")
```

**Step 3: Build Field Mapping**
```python
def map_fields_to_profile(fields, profile):
    mapping = {}
    
    for field in fields:
        label = field["label"].lower()
        
        if "first name" in label or "fname" in label:
            mapping[field["id"]] = profile["personal"]["name"].split()[0]
            
        elif "last name" in label or "lname" in label:
            mapping[field["id"]] = profile["personal"]["name"].split()[-1]
            
        elif "email" in label:
            mapping[field["id"]] = profile["personal"]["email"]
            
        elif "phone" in label:
            mapping[field["id"]] = profile["personal"]["phone"]
            
        elif "linkedin" in label or "profile" in label:
            mapping[field["id"]] = profile["personal"]["linkedin"]
            
        elif "years" in label and "experience" in label:
            mapping[field["id"]] = str(int(profile["professional"]["experience_years"]))
            
        elif "resume" in label or "cv" in label:
            mapping[field["id"]] = f"tailored_resume_{job['job_id']}.pdf"
            
        elif "cover letter" in label:
            mapping[field["id"]] = f"cover_letter_{job['job_id']}.txt"
            
        elif "salary" in label:
            mapping[field["id"]] = str(profile["preferences"]["salary_min"])
            
        else:
            # Unknown field - flag for human
            mapping[field["id"]] = "⚠️ NEEDS_USER_INPUT"
    
    return mapping
```

**Step 4: Fill Mapped Fields**
```python
for field_id, value in mapping.items():
    if value == "⚠️ NEEDS_USER_INPUT":
        continue  # Skip for now
        
    if field_id.endswith("_file"):  # File upload
        page.set_input_files(f"#{field_id}", value)
    else:
        page.fill(f"#{field_id}", value)
```

**Step 5: Screenshot for Review**
```python
page.screenshot(path=f"/home/claude/form_preview_{job['job_id']}.png")
```

**Step 6: HUMAN CHECKPOINT**
```
📝 Application Form Ready for Review

[Show screenshot of filled form]

✅ Filled Fields:
• First Name: Sarah
• Last Name: Chen  
• Email: sarah.chen@email.com
• Phone: +1-555-0100
• LinkedIn: linkedin.com/in/sarahchen
• Years Experience: 6
• Resume: ✓ Uploaded
• Cover Letter: ✓ Uploaded

⚠️ Fields Needing Your Input:
• Desired Start Date: [___________]
• Are you authorized to work in the US?: [ ] Yes [ ] No
• Referral Source: [___________]

Please fill in the fields above, then:
[Submit Application] [Edit] [Cancel]
```

**Step 7: Submit Form**
```python
# After user confirms/fills unknown fields
page.click("button[type='submit']")

# Wait for confirmation
page.wait_for_selector(".confirmation-message, .success")

# Capture confirmation
confirmation = page.text_content(".confirmation-message")
page.screenshot(path=f"/home/claude/confirmation_{job['job_id']}.png")
```

**Step 8: Log Result**
```python
log_application({
    "job_id": job["job_id"],
    "method": "form",
    "status": "submitted",
    "submitted_at": datetime.now().isoformat(),
    "form_url": job["apply_url"],
    "confirmation": confirmation
})
```

### ROUTE C: LinkedIn Easy Apply

**When to Use**: `apply_method == "easy_apply"`

**Requirements**
- LinkedIn account logged in (cookie/session)
- Playwright MCP for automation

**Process**
```python
page.goto(job["url"])
page.click("button:has-text('Easy Apply')")

# LinkedIn modal appears
# Fill fields (similar to form fill)
page.fill("#first-name", profile["personal"]["name"].split()[0])
page.fill("#last-name", profile["personal"]["name"].split()[-1])
page.fill("#phone", profile["personal"]["phone"])

# Upload resume if field exists
if page.query_selector("input[type='file']"):
    page.set_input_files("input[type='file']", 
                        f"tailored_resume_{job['job_id']}.pdf")

# Take screenshot for user review
page.screenshot(path=f"/home/claude/linkedin_preview_{job['job_id']}.png")
```

**HUMAN CHECKPOINT** (same as form method)

**Submit**
```python
page.click("button:has-text('Submit application')")
```

---

## Phase 3: Post-Application

### Track Application Status

```python
application_record = {
    "job_id": job["job_id"],
    "company": job["company"],
    "title": job["title"],
    "status": "submitted",  # or "sent" for email
    "method_used": job["apply_method"],
    "submitted_at": datetime.now().isoformat(),
    "resume_version": f"tailored_resume_{job['job_id']}.pdf",
    "artifacts": [
        f"tailored_resume_{job['job_id']}.pdf",
        f"tailored_resume_{job['job_id']}.docx",
        f"cover_letter_{job['job_id']}.txt"
    ],
    "ats_score": calculate_ats_score(resume, job),
    "notes": "Application submitted successfully via form"
}
```

### ATS Score Calculation

Estimate how well the resume matches ATS systems:

```python
def calculate_ats_score(resume_text, job_requirements):
    score = 0
    
    # Keyword matching
    jd_keywords = extract_keywords(job_requirements)
    resume_keywords = extract_keywords(resume_text)
    
    matched = jd_keywords & resume_keywords
    score += (len(matched) / len(jd_keywords)) * 60
    
    # Formatting check
    if is_ats_friendly_format(resume_text):
        score += 20
    
    # Section headers present
    required_sections = ["experience", "education", "skills"]
    present_sections = count_present_sections(resume_text, required_sections)
    score += (present_sections / len(required_sections)) * 20
    
    return min(100, round(score))
```

### Save Application Record

```python
# Update state database
with open("/home/claude/applications_log.json", "r+") as f:
    applications = json.load(f)
    applications.append(application_record)
    f.seek(0)
    json.dump(applications, f, indent=2)
```

---

## Error Handling

### Email Failures
```python
try:
    gmail.send_email(...)
except EmailSendError as e:
    return {
        "status": "failed",
        "error": str(e),
        "retry_suggestion": "Check email credentials or try manual send"
    }
```

### Form Submission Failures
- CAPTCHA detected → Pause, ask user to solve
- Required field missing → Flag for user input
- Timeout → Retry once, then manual
- Network error → Save progress, retry

### File Upload Failures
- File too large → Compress PDF
- Wrong format → Convert format
- Upload button not found → Manual upload needed

---

## Output Per Job

```json
{
  "job_id": "j001",
  "status": "sent" | "submitted" | "failed" | "skipped",
  "method_used": "email",
  "timestamp": "2024-02-23T14:30:00Z",
  "artifacts": [
    "tailored_resume_j001.pdf",
    "tailored_resume_j001.docx",
    "cover_letter_j001.txt"
  ],
  "ats_score": 88,
  "notes": "Email sent to hiring@acme.com",
  "error": null,
  "confirmation_screenshot": "confirmation_j001.png"
}
```

## Tools Required

- **Code Execution**: Python for resume generation, logic
- **python-docx**: DOCX file creation
- **reportlab**: PDF generation
- **Playwright MCP**: Form automation (optional but recommended)
- **Gmail MCP**: Email sending (required for email method)
- **Filesystem**: Read profile, save artifacts

## Success Criteria

✅ Resume tailored to JD (verified by user)
✅ Application submitted successfully
✅ Confirmation received (email sent or form submitted)
✅ All artifacts saved
✅ Application logged in state database

## Integration Point

**Return to Orchestrator**
```json
{
  "agent": "application-engine",
  "job_id": "j001",
  "status": "complete",
  "output": {
    "application_status": "submitted",
    "method": "email",
    "timestamp": "2024-02-23T14:30:00Z",
    "artifacts": ["resume_j001.pdf", "cover_j001.txt"]
  }
}
```

Orchestrator collects results from all parallel instances and updates dashboard.
