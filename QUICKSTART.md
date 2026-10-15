# Quick Start Guide

## 5-Minute Setup

### Step 1: Install Skills

Optionally copy the included skills to your Claude Code skills directory:

```bash
mkdir -p ~/.claude/skills
cp -r .claude/skills/* ~/.claude/skills/
```

### Step 2: Install Dependencies

Requires [uv](https://docs.astral.sh/uv/). From the project root:

```bash
uv sync
```

Configure the Anthropic API key before starting:

```bash
cp .env.example .env
# Edit .env and replace the placeholder with your API key.
```

### Step 3: Configure MCP Servers (Optional)

For full functionality, enable these MCP servers in Claude:
- **Gmail MCP** - For email applications
- **Playwright MCP** - For form automation

### Step 4: Upload Resume & Start

```
Upload your resume (PDF or DOCX) and say:

"Help me find and apply to jobs"
```

That's it! Claude will guide you through the rest.

To run the bundled terminal agent, use `uv run agent` from the project root.

---

## First Run Checklist

Before your first job application campaign:

### ✅ Preparation
- [ ] Resume is up-to-date and complete
- [ ] Resume includes email and phone number
- [ ] You know your target roles
- [ ] You know your salary range
- [ ] You have location preferences decided
- [ ] Gmail/email access configured (for email applications)

### ✅ During Campaign
- [ ] Review parsed profile carefully
- [ ] Edit preferences if needed
- [ ] Filter jobs to manageable number (start with 5-10)
- [ ] Review each tailored resume
- [ ] Check email/form previews before submitting
- [ ] Confirm each application

### ✅ After Campaign
- [ ] Save session ID for tracking
- [ ] Download all tailored resumes
- [ ] Set follow-up reminders (2 weeks)
- [ ] Track responses in session state
- [ ] Update profile based on feedback

---

## Example Session

```
You: [uploads resume.pdf] Help me find and apply to jobs

Claude: I'll help you automate your job search! Let me start by parsing your resume.

[Profile Architect runs]

Claude: ✓ Profile created! Here's what I extracted:
• Name: Sarah Chen
• Email: sarah@email.com
• Experience: 6 years
• Top skills: Python, AWS, React, Docker, Kubernetes
• Target roles: Senior Engineer, Staff Engineer
• Location: Remote / SF Bay Area
• Salary: $180K - $250K

Is this correct?

You: Yes, looks good!

Claude: Great! Now searching for matching jobs...

[Job Intelligence runs - searches LinkedIn, Indeed, Wellfound]

Claude: 🎯 Found 47 jobs! Top 15:

1. ⭐ 91.3 - Staff Backend Engineer @ Acme Corp
   📍 Remote | 💰 $170K-$210K | 📧 Email
   
2. ⭐ 87.5 - Engineering Manager @ Beta Inc
   📍 SF | 💰 $190K-$240K | 📝 Form
   
[... shows top 15 ...]

Which jobs should I apply to?

You: Apply to the top 10

Claude: Got it! I'll apply to 10 jobs. For each one, I'll:
1. Tailor your resume to match the job description
2. Create a personalized cover letter
3. Show you a preview
4. Wait for your approval
5. Submit the application

Starting with Acme Corp...

[Application Engine runs for each job]

Claude: 📧 Email ready for Acme Corp - Staff Backend Engineer

To: hiring@acme.com
Subject: Application for Staff Backend Engineer

[Shows email preview]

Attachments:
✓ Sarah_Chen_Staff_Engineer_Acme.pdf

You: Looks good, send it

Claude: ✓ Sent! (1/10 complete)

[Repeats for remaining 9 jobs]

Claude: 📊 Campaign Complete!

✅ 10 applications submitted
• 7 via email
• 2 via form
• 1 via LinkedIn Easy Apply

All tailored resumes saved to:
sessions/job_search_20240223_143000/

Next: Set reminders for 2 weeks from now to follow up.

Good luck! 🎉
```

---

## Common Commands

### Resume Parsing Only
```
"Parse my resume into a profile"
```

### Job Search Only
```
"Find jobs matching my profile"
"Search for senior engineer positions in SF"
```

### Apply to Specific Jobs
```
"Apply to these 5 jobs: [paste URLs]"
"Apply to all jobs with score > 85"
```

### Update Settings
```
"Increase my salary minimum to $200K"
"Change location to NYC only"
"Add 'Tech Lead' to my target roles"
```

### Resume Session
```
"Continue my job search from yesterday"
"Show me applications from session job_search_20240223"
```

### View Status
```
"Show my application dashboard"
"How many applications are pending?"
"Which companies have I applied to?"
```

---

## Tips for Best Results

### 🎯 Profile Quality
- **Be specific**: "React, Redux, TypeScript" not just "JavaScript"
- **Quantify**: "6 years" not "experienced"
- **Update**: Keep profile current as you learn new skills

### 🔍 Job Search
- **Start broad**: Search returns ~50 jobs, then filter
- **Check scores**: Jobs >85 are excellent matches
- **Review JDs**: Sometimes score doesn't tell full story
- **Veto freely**: Better to skip than apply to bad match

### ✍️ Resume Tailoring
- **Review carefully**: Tailored resumes should still be accurate
- **Check numbers**: Verify any quantified achievements
- **ATS format**: Use DOCX if PDF has issues
- **Consistency**: Keep date formats, location formats consistent

### 📧 Applications
- **Personalize**: Add company-specific details when reviewing
- **Professional tone**: Formal for corporate, casual for startups
- **Timing**: Apply early in week (Tue-Thu best)
- **Track everything**: Update session state with responses

### 📈 Iteration
- **Analyze**: Which applications got responses?
- **Optimize**: Adjust preferences based on results
- **A/B test**: Try different resume approaches
- **Learn**: Each campaign improves the next

---

## Troubleshooting

### "Skills not loading"
```bash
# Verify skills directory
ls ~/.config/claude/skills/user/

# Should show: profile-architect, job-intelligence, application-engine, job-application-orchestrator
```

### "Can't parse resume"
- Try different format (PDF → DOCX or vice versa)
- Check file isn't corrupted
- Ensure file has actual text (not scanned image)

### "No jobs found"
- Broaden search criteria
- Lower minimum score threshold
- Add more target roles
- Try different keywords

### "Application failed"
- Check error message
- Verify email/form credentials
- Try manual submission for that job
- Continue with other jobs

---

## Need Help?

For issues specific to:
- **Profile Architect**: Check resume format, required fields
- **Job Intelligence**: Verify search parameters, job board access
- **Application Engine**: Check MCP servers, file permissions
- **Orchestrator**: Review session state, checkpoint approvals

Read the full README.md for detailed documentation.

---

**Ready? Upload your resume and start with: "Help me find and apply to jobs"**
