# ─────────────────────────────────────────────────────────────
# post.py — LinkedIn AI Auto Poster using Google Gemini (FREE)
# Rotates through ALL 12 content types before repeating any!
# Tracks used types in last_posts.json
# ─────────────────────────────────────────────────────────────
import requests, random, os, sys, json
from datetime import datetime

# ── CREDENTIALS ───────────────────────────────────────────────
LINKEDIN_TOKEN = os.environ.get("LINKEDIN_TOKEN", "AQW2-1Yw3CJY6xJGGvEQfkexebwpywN9D6S8XPiXIwDy1em2qTjwHVDrKRqMadURrFkcJSMJr0qeyhn1qP0NDjCsycMsBpwoBGK69EFpDnr4zgO5osPLnIA2DmxAsNxm57oK9bzwPxQu8uN_jc-fft7zkF5nxBPSzXDEVbSb9eyosn9zjF-wyTx0PJLLd8uR3lj4nACs26CqXgQswpOTUJoU4EVHkSirCTFqj8VZBzZeHWCYSX8nlK4vtc6S4H9eQu2sKMT6mBAdxfgzHWBmBxp0Zfm9i3_W3c2wEojdWu55Y2kGYaUUTLsl8zZpeRkpVWn9vcnOmqFw-XWrBdNh7vrA9L_NIw")
PERSON_URN     = os.environ.get("PERSON_URN",     "urn:li:person:0THMb1Oyen")
GEMINI_KEY     = os.environ.get("GEMINI_KEY",     "AIzaSyCSVuDtPWXA87A4RAFL3uFWihNzehSXE3g")

# ── ROTATION TRACKER FILE ─────────────────────────────────────
TRACKER_FILE = "last_posts.json"

print(f"LinkedIn AI Poster starting - {datetime.now():%A, %d %B %Y %H:%M}")
print("-" * 50)

# ── CONTENT TYPES ─────────────────────────────────────────────
CONTENT_TYPES = [
    {
        "label": "SQL Code Tip",
        "prompt": """Write a LinkedIn post with a REAL SQL code example for data engineers.
MUST include actual SQL code showing WRONG approach vs RIGHT approach.
Pick one specific topic from: window functions, CTEs, query optimization,
EXISTS vs IN, NULL handling, partitioning in Synapse/Redshift, MERGE statements,
EXPLAIN plans, index usage, or GROUP BY optimisation.

Format:
[Hook line with emoji]

Most engineers write this:
[wrong SQL code — 3-5 lines]

This is better:
[correct SQL code — 3-5 lines]

Why it matters: [1-2 lines]
[question for comments]
[hashtags]"""
    },
    {
        "label": "PySpark Code Tip",
        "prompt": """Write a LinkedIn post with a REAL PySpark code example for data engineers.
MUST include actual working PySpark code showing a performance improvement.
Pick one topic: broadcast joins, avoiding .count() in loops, caching strategy,
repartition vs coalesce, avoiding UDFs, window functions in Spark,
Delta Lake MERGE, handling skew, AQE config.

Format:
[Hook line with emoji]

Wrong way (slow):
[bad PySpark code — 3-5 lines]

Right way (fast):
[good PySpark code — 3-5 lines]

Result: [what improvement this gives]
[question for comments]
[hashtags]"""
    },
    {
        "label": "Python Code Tip",
        "prompt": """Write a LinkedIn post with a REAL Python code example for data engineers.
MUST include actual Python code showing a practical improvement.
Pick one topic: generators for large files, dataclasses for pipeline config,
context managers for DB connections, type hints in ETL functions,
logging setup, error handling with retries, pathlib for file handling,
pydantic for data validation, pandas memory optimisation.

Format:
[Hook line with emoji]

Before (messy):
[bad Python code — 4-6 lines]

After (clean):
[good Python code — 4-6 lines]

Why this matters for data engineers: [1-2 lines]
[question for comments]
[hashtags]"""
    },
    {
        "label": "Azure Code Tip",
        "prompt": """Write a LinkedIn post with a REAL code or config example for Azure data engineers.
MUST include actual code, JSON config, ADF expression, or CLI commands.
Pick one topic: ADF dynamic pipelines, Databricks mount ADLS Gen2,
Synapse external tables, Delta Lake on ADLS, Azure Functions for ETL triggers,
Key Vault secrets in Databricks, Event Hubs + Spark streaming,
COPY INTO in Synapse, or Databricks job cluster config.

Format:
[Hook with emoji]

Here is the actual code/config:
[real code example — 5-8 lines]

What this does: [explanation]
Pro tip: [one extra insight]
[question for comments]
[hashtags: #Azure #DataEngineering #Databricks etc]"""
    },
    {
        "label": "AWS Code Tip",
        "prompt": """Write a LinkedIn post with a REAL code or config example for AWS data engineers.
MUST include actual code, Glue script, Athena SQL, boto3, or CLI commands.
Pick one topic: Glue DynamicFrame vs DataFrame, S3 partition pruning in Athena,
boto3 S3 operations, EMR Spark submit config, Redshift COPY command,
Lambda trigger for S3 events, Step Functions for pipelines,
Lake Formation permissions, or Kinesis + Spark streaming.

Format:
[Hook with emoji]

Here is the actual code/config:
[real code example — 5-8 lines]

Why this matters: [explanation]
Pro tip: [one extra insight]
[question for comments]
[hashtags: #AWS #DataEngineering #Glue etc]"""
    },
    {
        "label": "Databricks Code Tip",
        "prompt": """Write a LinkedIn post with a REAL Databricks code example.
MUST include actual PySpark or SQL code that runs on Databricks.
Pick one topic: Delta Lake MERGE for upserts, Auto Loader for incremental ingestion,
Delta time travel queries, OPTIMIZE and ZORDER commands,
Databricks Widgets for parameterised notebooks, Unity Catalog usage,
Structured Streaming with Delta, or Change Data Feed.

Format:
[Hook with emoji]

Here is working Databricks code:
[real code — 6-10 lines]

What this solves: [explanation]
[question for comments]
[hashtags: #Databricks #DeltaLake #DataEngineering etc]"""
    },
    {
        "label": "Interview Q&A with Code",
        "prompt": """Write a LinkedIn post as a data engineering interview Q&A with actual code.
MUST have a real code example in the answer.

Format:
Interview Question: [technical question]

Most candidates say: [vague theoretical answer — 1 line]

Strong answer with code:
[explanation + actual code example — 5-8 lines]

Why this impresses interviewers: [1-2 lines]
[question asking followers what they would answer]
[hashtags: #DataEngineering #Interview etc]

Topics: window functions, Spark joins, SCD Type 2,
idempotent pipeline design, incremental load, partition strategy."""
    },
    {
        "label": "ADF Pipeline Tip",
        "prompt": """Write a LinkedIn post sharing a practical Azure Data Factory tip with actual example.
MUST include a real ADF pattern, expression, or JSON snippet.
Pick one topic: dynamic file paths with parameters, ForEach with parallelism,
error handling with If Condition, Lookup + ForEach pattern,
ADF expressions for date partitioning, tumbling window triggers,
parameterised linked services, or copy activity with schema mapping.

Format:
[Hook with emoji]

ADF tip: [what the tip is]

Here is the actual expression/config:
[real ADF expression or JSON — 4-6 lines]

This saves: [time/effort it saves]
[question for comments]
[hashtags: #ADF #Azure #DataEngineering etc]"""
    },
    {
        "label": "Data Pipeline Design",
        "prompt": """Write a LinkedIn post about a data pipeline design pattern with real code.
MUST include actual code showing the pattern implementation.
Pick one topic: idempotent pipeline with DELETE+INSERT,
incremental load using watermark pattern, dead letter queue handling,
retry logic with exponential backoff, schema validation before load,
checkpointing in Spark streaming, or SCD Type 2 with PySpark MERGE.

Format:
[Hook with emoji]

The pattern: [name and 1-line description]

Here is how to implement it:
[actual code — 8-12 lines]

Why every pipeline needs this: [explanation]
[question for comments]
[hashtags]"""
    },
    {
        "label": "Performance Optimisation",
        "prompt": """Write a LinkedIn post about a performance optimisation with real before/after code.
MUST show actual before/after code with the performance improvement.
Pick one topic: SQL query plan optimisation, Spark partition tuning,
Pandas vs Polars for large files, vectorised operations vs loops,
Redshift distribution keys, Synapse result set caching,
or Delta Lake ZORDER for faster queries.

Format:
[Hook with emoji]

Before optimisation:
[slow code — 3-5 lines]

After optimisation:
[fast code — 3-5 lines]

Performance gain: [specific improvement like 10x faster or 80% less shuffle]
[question for comments]
[hashtags]"""
    },
    {
        "label": "Mistake and Fix with Code",
        "prompt": """Write a LinkedIn post about a common data engineering mistake with code showing the fix.
MUST show the wrong code AND the correct code.
Pick one topic: SELECT * in production, missing idempotency,
collecting large DataFrames to driver, wrong join causing cartesian product,
not handling NULLs in aggregations, hardcoded dates in queries,
or not using pushdown predicates.

Format:
[Hook with emoji]

I see this mistake every week:
[wrong code — 3-5 lines]

Here is the fix:
[correct code — 3-5 lines]

The real impact: [what goes wrong in production without the fix]
[question for comments]
[hashtags]"""
    },
    {
        "label": "Cheat Sheet with Code",
        "prompt": """Write a LinkedIn post as a practical code cheat sheet for data engineers.
MUST include multiple short real code examples.
Pick one topic: PySpark DataFrame operations cheat sheet,
SQL window functions with examples, Python one-liners for data cleaning,
Delta Lake commands cheat sheet, or Spark config settings that matter.

Format:
[Hook with emoji]

[Topic] Cheat Sheet for Data Engineers:

1. [operation name]:
   [code — 1-2 lines]

2. [operation name]:
   [code — 1-2 lines]

3. [operation name]:
   [code — 1-2 lines]

4. [operation name]:
   [code — 1-2 lines]

Save this for your next project!
[question for comments]
[hashtags]"""
    },
]

# ── ROTATION LOGIC ────────────────────────────────────────────
def load_tracker():
    """Load the list of recently used content type labels."""
    if os.path.exists(TRACKER_FILE):
        try:
            with open(TRACKER_FILE, "r") as f:
                return json.load(f).get("used", [])
        except:
            return []
    return []

def save_tracker(used: list):
    """Save updated used list to tracker file."""
    with open(TRACKER_FILE, "w") as f:
        json.dump({"used": used, "updated": str(datetime.now())}, f, indent=2)

def pick_content_type() -> dict:
    """Pick a content type that hasn't been used recently.
    Cycles through all 12 before repeating any."""
    all_labels  = [c["label"] for c in CONTENT_TYPES]
    used_labels = load_tracker()

    # Find types NOT yet used in current cycle
    unused = [c for c in CONTENT_TYPES if c["label"] not in used_labels]

    # If all 12 used — reset and start fresh cycle
    if not unused:
        print("All 12 content types used! Starting fresh rotation cycle.")
        used_labels = []
        unused = CONTENT_TYPES
        save_tracker([])

    # Pick randomly from unused types
    chosen = random.choice(unused)

    # Mark as used
    used_labels.append(chosen["label"])
    save_tracker(used_labels)

    # Show rotation status
    print(f"Rotation: {len(used_labels)}/12 types used this cycle")
    remaining = [l for l in all_labels if l not in used_labels]
    if remaining:
        print(f"Remaining types: {', '.join(remaining)}")

    return chosen

# ── GENERATE POST WITH GEMINI ─────────────────────────────────
def generate_post(content_type: dict) -> str:
    print(f"Asking Gemini to generate: [{content_type['label']}]")

    base_rules = """
STRICT LinkedIn post rules:
- Opening line: 1 emoji + strong punchy hook (NOT generic like 'As a data engineer...')
- ALWAYS include real working code — this is non-negotiable
- Code must be indented with spaces (no markdown backticks)
- Keep total length 180-280 words
- Short paragraphs — maximum 2 lines each
- End with ONE specific question to get comments
- Very last line: 4-5 hashtags only
- Write from personal experience — use 'I', 'we', 'our team'
- No fluff, no generic advice — every line must be useful"""

    full_prompt = f"{content_type['prompt']}\n\n{base_rules}\n\nWrite ONLY the post. No intro, no explanation."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={GEMINI_KEY}"

    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 800,
            "temperature": 0.85
        }
    }

    resp = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=30
    )

    if resp.status_code == 200:
        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        print(f"Generated {len(text)} chars successfully")
        return text
    else:
        print(f"Gemini API failed: {resp.status_code} - {resp.text}")
        sys.exit(1)

# ── POST TO LINKEDIN ──────────────────────────────────────────
def post_to_linkedin(text: str):
    print("Posting to LinkedIn...")

    headers = {
        "Authorization": f"Bearer {LINKEDIN_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    payload = {
        "author": PERSON_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    resp = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers=headers,
        json=payload,
        timeout=30
    )

    if resp.status_code == 201:
        print("SUCCESS - Posted to LinkedIn!")
    else:
        print(f"LinkedIn failed: {resp.status_code} - {resp.text}")
        sys.exit(1)

# ── MAIN ──────────────────────────────────────────────────────
content_type = pick_content_type()
print(f"Today's content type: [{content_type['label']}]")

post_text = generate_post(content_type)

print("\n" + "=" * 50)
print("POST PREVIEW:")
print(post_text)
print("=" * 50 + "\n")

post_to_linkedin(post_text)

print("Done! Post is live on LinkedIn.")
# print("Next run: tomorrow at 8:30 AM IST (via GitHub Actions)")