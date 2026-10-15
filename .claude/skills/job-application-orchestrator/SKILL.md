---
name: job-application-orchestrator
description: Coordinate automated job search and application workflows using specialized AI agents. Use this skill whenever someone wants to automate their job search, apply to multiple jobs at once, set up a job hunting system, or says things like "help me find and apply to jobs", "automate my job applications", "I need to apply to jobs efficiently", or "set up a job search pipeline". This is the main entry point for the multi-agent job application system.
---

# Job Application Orchestrator

Master coordinator for the multi-agent job application system. Manages state, routes tasks, enforces checkpoints, and presents results.

## When to Use

- User wants end-to-end automated job application assistance
- User uploads resume and wants to find+apply to jobs
- User asks to "set up my job hunt", "automate applications", "help me apply to jobs"
- User needs to manage multiple job applications efficiently
- User wants to track application status across multiple positions

## System Overview

This orchestrator coordinates three specialized agents:

1. **Profile Architect** - Parses resume → structured profile
2. **Job Intelligence** - Searches jobs → scored matches
3. **Application Engine** - Tailors resume → submits application

```
User → Orchestrator → Profile Architect → [Checkpoint] →
                    → Job Intelligence → [Checkpoint] →
                    → Application Engine (parallel) → Dashboard
```

## Core Workflow

### Step 1: Initialize Session

```python
import json
import os
from datetime import datetime

# Create session directory
session_id = f"job_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
os.makedirs(f"/home/claude/sessions/{session_id}", exist_ok=True)

session_state = {
    "session_id": session_id,
    "created_at": datetime.now().isoformat(),
    "status": "initialized",
    "agents": {
        "profile_architect": {"status": "pending"},
        "job_intelligence": {"status": "pending"},
        "application_engine": {"status": "pending"}
    },
    "checkpoints": [],
    "applications": []
}
```

### Step 2: Invoke Profile Architect

**Trigger Conditions**
- Resume file detected in `/mnt/user-data/uploads`
- User says "here's my resume"
- No existing `master_profile.json`

**Invocation**
```python
# Hand off to Profile Architect skill
profile_result = invoke_agent("profile-architect", {
    "resume_path": "/mnt/user-data/uploads/resume.pdf"
})

# Profile Architect will:
# 1. Extract text from resume
# 2. Parse into structured JSON
# 3. Validate critical fields
# 4. Fill gaps with user input
# 5. Return master_profile.json
```

**Update State**
```python
session_state["agents"]["profile_architect"] = {
    "status": "complete",
    "output": profile_result["profile_path"],
    "completed_at": datetime.now().isoformat()
}
```

### Step 3: CHECKPOINT - Profile Review

**Present Profile to User**
```python
with open(profile_result["profile_path"]) as f:
    profile = json.load(f)

# Display formatted profile
print(f"""
📋 Profile Created from Resume

Personal Information:
• Name: {profile['personal']['name']}
• Email: {profile['personal']['email']}
• Phone: {profile['personal']['phone']}
• LinkedIn: {profile['personal']['linkedin']}

Professional Summary:
• Current Title: {profile['professional']['current_title']}
• Experience: {profile['professional']['experience_years']} years
• Top Skills: {', '.join(profile['professional']['skills']['technical'][:5])}

Job Search Preferences:
• Target Roles: {', '.join(profile['preferences']['target_roles'])}
• Location: {profile['preferences']['location_preference']}
• Salary Range: ${profile['preferences']['salary_min']:,} - ${profile['preferences']['salary_max']:,}
• Company Size: {', '.join(profile['preferences']['company_size'])}

Is this profile correct? 
☐ Yes, continue to job search
☐ No, let me edit [specific field]
""")
```

**Handle Edits**
```python
if user_requests_edit:
    # Allow field-by-field editing
    field_to_edit = get_user_selection()
    new_value = get_user_input()
    
    # Update profile
    update_profile_field(profile, field_to_edit, new_value)
    
    # Save updated profile
    with open(profile_result["profile_path"], 'w') as f:
        json.dump(profile, f, indent=2)
```

**Log Checkpoint**
```python
session_state["checkpoints"].append({
    "checkpoint": "profile_review",
    "timestamp": datetime.now().isoformat(),
    "approved": True,
    "edits_made": []  # List of fields edited
})
```

### Step 4: Invoke Job Intelligence

**Trigger Conditions**
- Profile approved by user
- User says "find me jobs", "search for positions"

**Invocation**
```python
job_result = invoke_agent("job-intelligence", {
    "profile_path": profile_result["profile_path"],
    "search_params": {
        "num_results": 50,
        "platforms": ["linkedin", "indeed", "wellfound"],
        "min_score": 70
    }
})

# Job Intelligence will:
# 1. Search multiple job boards
# 2. Deduplicate listings
# 3. Deep scrape each job
# 4. Score against profile
# 5. Classify apply methods
# 6. Return ranked job_queue.json
```

**Update State**
```python
session_state["agents"]["job_intelligence"] = {
    "status": "complete",
    "output": job_result["job_queue_path"],
    "completed_at": datetime.now().isoformat(),
    "stats": {
        "total_found": job_result["total_found"],
        "unique_jobs": job_result["unique_jobs"],
        "top_score": job_result["top_score"]
    }
}
```

### Step 5: CHECKPOINT - Job Selection

**Present Ranked Jobs**
```python
with open(job_result["job_queue_path"]) as f:
    jobs = json.load(f)

# Show top N jobs
print(f"""
🎯 Found {len(jobs)} Matching Jobs

Top 15 by Score:
""")

for i, job in enumerate(jobs[:15], 1):
    print(f"""
{i}. ⭐ {job['match_score']:.1f} - {job['title']} @ {job['company']}
   📍 {job['location']} | 💰 {format_salary(job['salary_range'])}
   📧 Apply via: {job['apply_method']}
   ✓ Matches: {', '.join(job['requirements'][:3])}
   
   [✓ Apply] [❌ Skip] [👁️ View Full JD]
""")
```

**Selection Interface**
```python
def get_job_selection():
    """
    Allow user to:
    - Select all jobs above score threshold
    - Select specific jobs individually
    - Veto any job
    - Adjust filters
    """
    
    options = [
        "Apply to all jobs with score > 85",
        "Apply to all jobs with score > 80",
        "Apply to top 10 only",
        "Let me select individually",
        "Adjust filters (location, salary, etc.)"
    ]
    
    choice = present_options(options)
    
    if choice == "individually":
        selected = []
        for job in jobs:
            if ask_user(f"Apply to {job['title']} at {job['company']}?"):
                selected.append(job)
        return selected
    elif "score >" in choice:
        threshold = extract_threshold(choice)
        return [j for j in jobs if j['match_score'] >= threshold]
    # ... handle other cases
```

**Filter Jobs**
```python
selected_jobs = get_job_selection()

# Apply user filters
if user_filters:
    selected_jobs = apply_filters(selected_jobs, user_filters)

# Remove vetoed jobs
selected_jobs = [j for j in selected_jobs if not j.get('vetoed')]
```

**Log Checkpoint**
```python
session_state["checkpoints"].append({
    "checkpoint": "job_selection",
    "timestamp": datetime.now().isoformat(),
    "approved": True,
    "selected_count": len(selected_jobs),
    "vetoed_count": len([j for j in jobs if j.get('vetoed')])
})
```

### Step 6: Invoke Application Engine (Parallel)

**Spawn Instances**
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def apply_to_job(job, profile):
    """One instance per job"""
    return invoke_agent("application-engine", {
        "profile_path": profile_result["profile_path"],
        "job": job
    })

# Run in parallel (max 5 at a time to avoid overwhelming user)
application_results = []

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {
        executor.submit(apply_to_job, job, profile): job
        for job in selected_jobs
    }
    
    for future in as_completed(futures):
        job = futures[future]
        try:
            result = future.result()
            application_results.append(result)
            
            # Update user on progress
            print(f"✓ Applied to {job['title']} at {job['company']} via {result['method']}")
            
        except Exception as e:
            print(f"✗ Failed to apply to {job['title']}: {str(e)}")
            application_results.append({
                "job_id": job["job_id"],
                "status": "failed",
                "error": str(e)
            })
```

**Progress Updates**
```python
print(f"""
🔄 Applications in Progress...

Completed: {len(completed)}/{len(selected_jobs)}
Pending: {len(pending)}
Failed: {len(failed)}

Current: Applying to Senior Engineer at Tech Corp via email...
""")
```

### Step 7: Collect Results & Update State

```python
# Update state with all results
for result in application_results:
    application_record = {
        "job_id": result["job_id"],
        "company": result.get("company"),
        "title": result.get("title"),
        "status": result["status"],
        "method": result["method_used"],
        "timestamp": result["timestamp"],
        "artifacts": result.get("artifacts", []),
        "error": result.get("error")
    }
    
    session_state["applications"].append(application_record)

# Save session state
with open(f"/home/claude/sessions/{session_id}/session_state.json", 'w') as f:
    json.dump(session_state, f, indent=2)
```

### Step 8: Present Final Dashboard

```python
print(f"""
📊 Job Application Campaign Complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 Summary Statistics:
• Total applications: {len(application_results)}
• Successfully submitted: {len([r for r in application_results if r['status'] in ['sent', 'submitted']])}
• Failed: {len([r for r in application_results if r['status'] == 'failed'])}
• Success rate: {success_rate:.1f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Application Details:

✅ Submitted Applications:
""")

# Show each successful application
for app in [a for a in application_results if a['status'] in ['sent', 'submitted']]:
    print(f"""
• {app['company']} - {app['title']}
  Method: {app['method']} | Score: {app.get('match_score', 'N/A')}
  Status: {app['status']} | Time: {app['timestamp']}
""")

print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🗂️ Generated Files:
• Master profile: master_profile.json
• Job queue: job_queue.json
• Session state: sessions/{session_id}/session_state.json

📁 Resume Variants Created:
""")

for app in application_results:
    if app.get('artifacts'):
        for artifact in app['artifacts']:
            print(f"  • {artifact}")

print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 Next Steps:
1. Set follow-up reminders (2 weeks from now)
2. Track responses in session state
3. Update profile based on feedback
4. Run again for new listings

Good luck with your job search! 🎉
""")
```

## State Management

**Session State Schema**
```json
{
  "session_id": "job_search_20240223_143000",
  "created_at": "2024-02-23T14:30:00Z",
  "status": "complete",
  "agents": {
    "profile_architect": {
      "status": "complete",
      "output": "/home/claude/master_profile.json",
      "completed_at": "2024-02-23T14:31:00Z"
    },
    "job_intelligence": {
      "status": "complete",
      "output": "/home/claude/job_queue.json",
      "completed_at": "2024-02-23T14:45:00Z",
      "stats": {
        "total_found": 47,
        "unique_jobs": 47,
        "top_score": 91.3
      }
    },
    "application_engine": {
      "status": "complete",
      "instances": 15,
      "completed_at": "2024-02-23T15:10:00Z"
    }
  },
  "checkpoints": [
    {
      "checkpoint": "profile_review",
      "timestamp": "2024-02-23T14:32:00Z",
      "approved": true
    },
    {
      "checkpoint": "job_selection",
      "timestamp": "2024-02-23T14:46:00Z",
      "approved": true,
      "selected_count": 15
    }
  ],
  "applications": [
    {
      "job_id": "j001",
      "company": "Acme Corp",
      "title": "Staff Backend Engineer",
      "status": "sent",
      "method": "email",
      "timestamp": "2024-02-23T14:55:00Z",
      "outcome": "pending"
    }
  ]
}
```

## Human Checkpoints

All checkpoints **MUST** wait for user approval before proceeding:

1. **Profile Review** - After Profile Architect
   - User confirms profile accuracy
   - User can edit any field
   - Cannot proceed until approved

2. **Job Selection** - After Job Intelligence
   - User reviews ranked jobs
   - User selects which to apply
   - User can veto any job
   - Cannot proceed until selection made

3. **Application Review** - Per job in Application Engine
   - User reviews email/form before sending
   - User can edit content
   - User can fill unknown fields
   - Each application requires individual approval

## Error Handling & Recovery

**Agent Failure**
```python
def handle_agent_failure(agent_name, error):
    print(f"""
    ⚠️ {agent_name} encountered an error:
    {str(error)}
    
    Options:
    1. Retry with same inputs
    2. Skip this step
    3. Abort campaign
    """)
    
    choice = get_user_choice()
    
    if choice == "retry":
        return invoke_agent(agent_name, last_params)
    elif choice == "skip":
        session_state["agents"][agent_name]["status"] = "skipped"
        return None
    else:
        session_state["status"] = "aborted"
        raise CampaignAbortedError()
```

**Partial Success**
If 10/15 applications succeed:
- Log failures separately
- Offer to retry failed applications
- Don't block successful ones

**Session Resume**
```python
def resume_session(session_id):
    """Resume interrupted session"""
    state = load_session_state(session_id)
    
    # Find last completed checkpoint
    if state["agents"]["profile_architect"]["status"] != "complete":
        # Restart from profile creation
        return run_profile_architect()
    elif state["agents"]["job_intelligence"]["status"] != "complete":
        # Restart from job search
        return run_job_intelligence(state["agents"]["profile_architect"]["output"])
    else:
        # Resume applications
        pending = get_pending_applications(state)
        return run_application_engine(pending)
```

## Follow-up Management

**Schedule Reminders**
```python
def schedule_followups(applications):
    """Set reminders for applications without response"""
    for app in applications:
        if app["status"] in ["sent", "submitted"]:
            followup_date = datetime.now() + timedelta(days=14)
            
            reminders.add({
                "job_id": app["job_id"],
                "company": app["company"],
                "date": followup_date,
                "message": f"Check status of {app['company']} application"
            })
```

## Analytics & Reporting

**Success Metrics**
```python
def generate_analytics(session_state):
    apps = session_state["applications"]
    
    return {
        "total_applications": len(apps),
        "success_rate": len([a for a in apps if a["status"] in ["sent", "submitted"]]) / len(apps),
        "average_score": sum(a.get("match_score", 0) for a in apps) / len(apps),
        "methods_breakdown": {
            "email": len([a for a in apps if a["method"] == "email"]),
            "form": len([a for a in apps if a["method"] == "form"]),
            "easy_apply": len([a for a in apps if a["method"] == "easy_apply"])
        },
        "top_companies": most_common([a["company"] for a in apps], 5)
    }
```

## Integration with Agents

**Invoke Agent Pattern**
```python
def invoke_agent(agent_name, params):
    """
    Trigger a skill by reading its SKILL.md and following instructions
    """
    skill_path = f"/mnt/skills/user/{agent_name}/SKILL.md"
    
    # Read skill instructions
    skill_content = read_file(skill_path)
    
    # Execute skill logic
    # The skill SKILL.md contains the full implementation
    result = execute_skill(skill_content, params)
    
    return result
```

## Success Criteria

✅ All agents complete successfully
✅ User approves at all checkpoints
✅ At least 1 application submitted
✅ Session state saved
✅ Dashboard presented to user

## Tools Required

- **All tools from child agents**
- **Code Execution**: Session management, state tracking
- **Filesystem**: Save state, coordinate agents
- **Threading**: Parallel application submission

## Notes

- This orchestrator is stateful - can be paused and resumed
- Each checkpoint is mandatory - cannot skip
- Failed applications don't block others
- Session history enables learning and optimization
- Users can run multiple campaigns with different profiles

---

Use this skill as the main entry point for the entire job application system.
