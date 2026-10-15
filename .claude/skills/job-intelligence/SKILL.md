---
name: job-intelligence
description: Search, scrape, score, and rank job listings across multiple job boards. Use this skill whenever someone wants to find jobs, search for positions, get job recommendations, scrape job postings, match jobs to their profile, or needs to compile a list of relevant opportunities. Also trigger when setting up automated job hunting, building a job pipeline, or researching available positions in a field. Use even if they say "find me jobs", "what's available for X role", or "search for engineering positions".
---

# Job Intelligence

Multi-source job search, intelligent scoring, and application method classification system.

## When to Use

- User asks to find jobs, search positions, or discover opportunities
- User has a profile and needs matching job listings
- Setting up automated job application pipelines
- User wants ranked/scored job recommendations
- Researching job market for a specific role or industry
- User says "what jobs are out there for me", "find openings", "search for positions"

## Core Workflow

### Phase 1: Multi-Source Search

**Input: Master Profile**
```python
import json
with open("master_profile.json") as f:
    profile = json.load(f)
```

**Build Search Queries**
Generate targeted searches from profile:
```python
# Primary queries from target roles
queries = []
for role in profile["preferences"]["target_roles"]:
    for keyword in profile["search_signal"]["keywords"]:
        queries.append(f"{role} {keyword} {location}")

# Example queries:
# - "Staff Engineer platform engineering remote"
# - "Engineering Manager backend distributed systems SF"
# - "Tech Lead python cloud NYC"
```

**Parallel Search Across Platforms**

Search each platform simultaneously:

1. **LinkedIn Jobs**
   ```python
   # Use web_search or Playwright to scrape
   url = "https://www.linkedin.com/jobs/search/?keywords=..."
   # Extract: job URLs, titles, companies, locations
   ```

2. **Indeed**
   ```python
   url = "https://www.indeed.com/jobs?q=..."
   # Extract: job cards, descriptions, salary if listed
   ```

3. **Wellfound (AngelList)**
   ```python
   url = "https://wellfound.com/role/..."
   # Extract: startup jobs, equity info, company stage
   ```

4. **Other Boards** (optional)
   - Hacker News "Who's Hiring"
   - Company career pages if specific companies listed
   - Remote job boards (We Work Remotely, Remote.co)
   - Industry-specific boards

**Tool Selection**
- **web_search**: Quick discovery of job URLs
- **web_fetch**: Get full page content
- **Playwright MCP**: JavaScript-heavy sites, login required
- **Brave Search/Serper MCP**: Programmatic search

**Rate Limiting & Politeness**
```python
import time
for platform in platforms:
    results = search_platform(platform, query)
    time.sleep(2)  # Be polite to job boards
```

### Phase 2: Deduplication

Jobs often appear on multiple boards. Deduplicate before deep scraping.

**Deduplication Key**
```python
def job_key(job):
    company = normalize(job["company"])
    title = normalize(job["title"])
    return f"{company}::{title}"

# Group by key
unique_jobs = {}
for job in all_results:
    key = job_key(job)
    if key not in unique_jobs:
        unique_jobs[key] = job
    else:
        # Merge: prefer source with more data
        unique_jobs[key] = merge_job_data(unique_jobs[key], job)
```

**Normalization Rules**
- Remove "Inc", "LLC", "Ltd" from company names
- Lowercase everything
- "Sr" → "Senior", "Eng" → "Engineer"
- Strip special characters

### Phase 3: Deep Scrape Each Listing

For each unique job, fetch the FULL job description:

```python
for job in unique_jobs:
    full_page = web_fetch(job["url"])
    jd = extract_job_description(full_page)
    
    job["full_jd"] = jd["text"]
    job["requirements"] = jd["requirements"]
    job["nice_to_haves"] = jd["nice_to_haves"]
    job["salary_range"] = jd["salary"]
    job["team_info"] = jd["team"]
    job["apply_method"] = detect_apply_method(full_page)
```

**Extraction Patterns**

Look for sections like:
- "Requirements", "Qualifications", "You Have"
- "Responsibilities", "You Will", "What You'll Do"
- "Nice to Have", "Bonus Points", "Plus"
- "Compensation", "Salary Range", "$XXX - $YYY"
- "Apply", "How to Apply", email addresses

**Salary Extraction**
```python
import re
salary_patterns = [
    r'\$(\d{1,3}(?:,?\d{3})*)\s*-\s*\$(\d{1,3}(?:,?\d{3})*)',
    r'(\d{1,3})k\s*-\s*(\d{1,3})k',
]
```

### Phase 4: Apply Method Classification

For each job, determine HOW to apply:

```python
def classify_apply_method(job, page_content):
    """
    Returns: "email" | "form" | "easy_apply" | "manual"
    """
    
    # Priority 1: Direct recruiter email
    if recruiter_email := extract_email(page_content):
        return {
            "method": "email",
            "contact": recruiter_email
        }
    
    # Priority 2: LinkedIn Easy Apply
    if "Easy Apply" in page_content or "easy-apply" in job["url"]:
        return {
            "method": "easy_apply",
            "apply_url": job["url"]
        }
    
    # Priority 3: Application form
    if apply_form_url := find_apply_button(page_content):
        return {
            "method": "form",
            "apply_url": apply_form_url
        }
    
    # Priority 4: Manual / external link
    if "external" in page_content or "company website" in page_content:
        return {
            "method": "manual",
            "notes": "Apply through company website"
        }
    
    # Fallback: Unable to determine
    return {
        "method": "unknown",
        "notes": "Manual review needed"
    }
```

**Detection Rules**
- Email: `(recruiting|hiring|jobs|careers)@company\.com`
- Easy Apply: LinkedIn-specific button
- Form: `<form>` with action URL, or "Apply Now" button
- Unknown: Flag for human review

### Phase 5: Intelligent Scoring

Score each job on 0-100 scale across multiple dimensions:

```python
def score_job(job, profile):
    scores = {
        "skills_match": 0,      # 30% weight
        "seniority_match": 0,   # 25% weight
        "location_fit": 0,      # 20% weight
        "salary_fit": 0,        # 15% weight
        "company_size_fit": 0   # 10% weight
    }
    
    # Skills matching
    jd_skills = extract_skills_from_jd(job["requirements"])
    profile_skills = set(profile["professional"]["skills"]["technical"])
    
    matched_skills = jd_skills & profile_skills
    scores["skills_match"] = len(matched_skills) / len(jd_skills) * 100
    
    # Seniority matching
    seniority_map = {
        "junior": 1, "mid": 2, "senior": 3, 
        "staff": 4, "principal": 5, "director": 6
    }
    jd_level = detect_seniority(job["title"])
    profile_level = detect_seniority(profile["professional"]["current_title"])
    
    level_diff = abs(seniority_map[jd_level] - seniority_map[profile_level])
    scores["seniority_match"] = max(0, 100 - (level_diff * 25))
    
    # Location fit
    if "remote" in job["location"].lower() and "remote" in profile["preferences"]["location_preference"].lower():
        scores["location_fit"] = 100
    elif job["location"] in profile["preferences"]["location_preference"]:
        scores["location_fit"] = 100
    else:
        scores["location_fit"] = 50  # Possible but not ideal
    
    # Salary fit
    if job["salary_range"]:
        min_sal, max_sal = job["salary_range"]
        pref_min = profile["preferences"]["salary_min"]
        
        if max_sal >= pref_min:
            scores["salary_fit"] = 100
        else:
            scores["salary_fit"] = (max_sal / pref_min) * 100
    else:
        scores["salary_fit"] = 70  # Unknown, assume reasonable
    
    # Company size fit
    company_size = detect_company_size(job["company"])
    if company_size in profile["preferences"]["company_size"]:
        scores["company_size_fit"] = 100
    else:
        scores["company_size_fit"] = 60
    
    # Weighted total
    total_score = (
        scores["skills_match"] * 0.30 +
        scores["seniority_match"] * 0.25 +
        scores["location_fit"] * 0.20 +
        scores["salary_fit"] * 0.15 +
        scores["company_size_fit"] * 0.10
    )
    
    return round(total_score, 1)
```

**Bonus/Penalty Adjustments**
- **+10 points**: Keywords from `search_signal.required_terms` all present
- **-20 points**: Any term from `search_signal.exclude_terms` present
- **+5 points**: Mentions specific technologies from profile
- **-15 points**: Requires clearance/citizenship if profile doesn't have it

### Phase 6: Ranking & Output

**Sort by Score**
```python
job_queue = sorted(scored_jobs, key=lambda x: x["match_score"], reverse=True)
```

**Generate Job Queue JSON**
```json
[
  {
    "job_id": "j001",
    "title": "Staff Backend Engineer",
    "company": "Acme Corp",
    "location": "Remote (US)",
    "url": "https://jobs.acme.com/...",
    "match_score": 91.3,
    "score_breakdown": {
      "skills_match": 95,
      "seniority_match": 100,
      "location_fit": 100,
      "salary_fit": 85,
      "company_size_fit": 80
    },
    "apply_method": "email",
    "recruiter_email": "hiring@acme.com",
    "apply_url": null,
    "salary_range": [170000, 210000],
    "full_jd": "We are looking for a Staff Backend Engineer...",
    "requirements": [
      "5+ years backend development",
      "Python/Go experience",
      "Distributed systems knowledge",
      "Cloud infrastructure (AWS/GCP)"
    ],
    "nice_to_haves": [
      "Kubernetes experience",
      "Open source contributions"
    ],
    "flags": [],
    "scraped_at": "2024-02-23T14:30:00Z"
  },
  {
    "job_id": "j002",
    "title": "Senior Platform Engineer",
    "company": "Beta Inc",
    "location": "San Francisco, CA",
    "url": "https://beta.com/careers/...",
    "match_score": 84.2,
    "apply_method": "form",
    "apply_url": "https://beta.com/apply/456",
    ...
  }
]
```

**Save Output**
```python
import json
output_path = "/home/claude/job_queue.json"
with open(output_path, 'w') as f:
    json.dump(job_queue, f, indent=2)
```

### Phase 7: User Checkpoint

**Present Results**
```
🎯 Found 47 matching jobs across 5 platforms

Top 10 Matches:

1. ⭐ 91.3 - Staff Backend Engineer @ Acme Corp
   📍 Remote (US) | 💰 $170K-$210K | 📧 Email apply
   ✓ Python, AWS, Kubernetes | ✓ Remote | ✓ 5+ years
   
2. ⭐ 87.5 - Engineering Manager @ Beta Inc
   📍 San Francisco, CA | 💰 $190K-$240K | 📝 Form apply
   ✓ Leadership, Backend, Infrastructure
   
3. ⭐ 84.2 - Senior Platform Engineer @ Gamma Tech
   📍 Remote (US) | 💰 Not listed | ⚡ Easy Apply
   ✓ Platform, DevOps, Kubernetes

[View all 47 jobs]

Which jobs would you like to apply to?
☐ Apply to top 10 (score > 80)
☐ Apply to top 5 (score > 85)  
☐ Let me review each one
☐ Custom selection

You can also veto any job by clicking the ❌ next to it.
```

**Filtering Options**
Allow user to:
- Set minimum score threshold
- Filter by apply method (only email, exclude forms)
- Filter by location
- Filter by salary range
- Exclude specific companies

## Edge Cases

**No Jobs Found**
```
I couldn't find any jobs matching your criteria.

Suggestions:
• Broaden location (add "Remote")
• Lower salary minimum
• Add more target roles
• Expand to adjacent seniorities
• Try different keyword combinations

Would you like me to try a broader search?
```

**Too Many Results (100+)**
```
Found 247 potential matches. This is a lot to process.

Recommendations:
• I'll focus on the top 50 by score
• You can raise the score threshold
• Or filter by specific companies/locations

Proceed with top 50?
```

**Scraping Failures**
If some jobs fail to scrape:
- Log the error
- Continue with others
- Report failures at the end
- Offer to retry manually

**Rate Limiting**
If a job board blocks requests:
- Back off exponentially
- Rotate to other sources
- Inform user of the limitation

**Stale Listings**
Check posting date. Flag jobs older than 30 days:
```
⚠️ This job was posted 45 days ago. It may be filled.
```

## Tools Required

- **web_search**: Initial job discovery
- **web_fetch**: Fetch full job pages  
- **Playwright MCP** (optional): JavaScript-heavy sites
- **Code Execution**: Scoring algorithms, deduplication
- **Filesystem**: Save job_queue.json

## Performance Notes

- Expect 2-5 minutes for 50 jobs (with rate limiting)
- Parallel requests where possible
- Cache scraped pages to avoid re-fetching
- Consider pagination limits (most boards show 25-50 per page)

## Success Criteria

✅ At least 10 unique jobs found
✅ All jobs have match_score calculated
✅ Apply method classified for each job
✅ User reviews and approves selection
✅ `job_queue.json` ready for Application Engine

## Integration Point

**Handoff to Orchestrator**
```json
{
  "agent": "job-intelligence",
  "status": "complete",
  "output": {
    "job_queue_path": "/home/claude/job_queue.json",
    "total_found": 47,
    "unique_jobs": 47,
    "top_score": 91.3,
    "user_selected": 15,
    "ready_to_apply": true
  }
}
```

Orchestrator will spawn Application Engine instances for each approved job.
