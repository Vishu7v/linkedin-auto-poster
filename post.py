# ─────────────────────────────────────────────────────────────
# post.py — LinkedIn AI Auto Poster using Google Gemini (FREE)
# Generates a code-card IMAGE (not plain text) for each post so
# code renders with real syntax highlighting instead of being
# mangled by LinkedIn's lack of markdown support.
# Rotates through ALL 12 content types before repeating any!
# Tracks used types in last_posts.json
# Has fallback models in case one is unavailable (503/429)
# ─────────────────────────────────────────────────────────────
import requests, random, os, sys, json, time, re
from datetime import datetime

from card_renderer import (
    render_cheat_sheet_card,
    render_compare_card,
    render_single_block_card,
)

# ── CREDENTIALS ───────────────────────────────────────────────
LINKEDIN_TOKEN = os.environ.get("LINKEDIN_TOKEN")
PERSON_URN     = os.environ.get("PERSON_URN")
GEMINI_KEY     = os.environ.get("GEMINI_KEY")

# ── ROTATION TRACKER FILE ─────────────────────────────────────
TRACKER_FILE = "last_posts.json"
IMAGE_OUT    = "post_card.png"

print(f"LinkedIn AI Poster starting - {datetime.now():%A, %d %B %Y %H:%M}")
print("-" * 50)

# ── JSON SCHEMAS PER TEMPLATE ─────────────────────────────────
SCHEMA_COMPARE = """
Respond with ONLY a valid JSON object (no markdown fences, no commentary, no
text before or after) matching EXACTLY this schema:
{
  "title": "5-8 word punchy title, no emoji",
  "subtitle": "one short line of context",
  "wrong_label": "short caps label, e.g. MOST ENGINEERS WRITE THIS",
  "wrong_code": ["line 1", "line 2", "..."],
  "right_label": "short caps label, e.g. THIS IS BETTER",
  "right_code": ["line 1", "line 2", "..."],
  "insight_label": "short caps label, e.g. WHY IT MATTERS",
  "insight_text": "1-2 sentences explaining why the right approach is better",
  "footer_line": "short call to action, no hashtags here",
  "caption": "the LinkedIn post caption: one emoji + punchy hook line, then 1-2 lines of context, then one specific question to drive comments, then on the final line 4-5 hashtags. NO code in the caption. NO markdown. NO URLs."
}
Rules for code arrays: each string is ONE line of real, runnable code, under
60 characters where possible so it fits in an image. No markdown backticks
anywhere. 3-6 lines per code array is ideal."""

SCHEMA_SINGLE = """
Respond with ONLY a valid JSON object (no markdown fences, no commentary, no
text before or after) matching EXACTLY this schema:
{
  "title": "5-8 word punchy title, no emoji",
  "subtitle": "one short line of context",
  "filename": "a realistic filename for the header bar, e.g. pipeline.py or query.sql",
  "code_lines": ["line 1", "line 2", "..."],
  "insight_label": "short caps label, e.g. WHAT THIS SOLVES",
  "insight_text": "1-2 sentences explaining the value of this approach",
  "tip_text": "one extra practical tip, or empty string if not needed",
  "footer_line": "short call to action, no hashtags here",
  "caption": "the LinkedIn post caption: one emoji + punchy hook line, then 1-2 lines of context, then one specific question to drive comments, then on the final line 4-5 hashtags. NO code in the caption. NO markdown. NO URLs."
}
Rules for code_lines: each string is ONE line of real, runnable code/config,
under 60 characters where possible so it fits in an image. No markdown
backticks anywhere. 5-10 lines is ideal."""

SCHEMA_CHEATSHEET = """
Respond with ONLY a valid JSON object (no markdown fences, no commentary, no
text before or after) matching EXACTLY this schema:
{
  "title": "short title for the cheat sheet, no emoji",
  "subtitle": "one short line of context",
  "items": [
    {"label": "operation name", "explanation": "one short sentence", "code_lines": ["line 1", "line 2"]},
    {"label": "operation name", "explanation": "one short sentence", "code_lines": ["line 1", "line 2"]},
    {"label": "operation name", "explanation": "one short sentence", "code_lines": ["line 1", "line 2"]},
    {"label": "operation name", "explanation": "one short sentence", "code_lines": ["line 1", "line 2"]}
  ],
  "footer_line": "short call to action, no hashtags here",
  "caption": "the LinkedIn post caption: one emoji + punchy hook line, then 1-2 lines of context, then one specific question to drive comments, then on the final line 4-5 hashtags. NO code in the caption. NO markdown. NO URLs."
}
Rules: exactly 4 items. Each code_lines entry is 1-2 short real lines of
code, under 60 characters where possible. No markdown backticks anywhere."""

# ── CONTENT TYPES (all 12, unchanged topics) ──────────────────
CONTENT_TYPES = [
    {
        "label": "SQL Code Tip",
        "template": "compare",
        "prompt": """Create LinkedIn card content with a REAL SQL code example for data engineers.
Show a WRONG approach vs a RIGHT approach.
Pick one specific topic from: window functions, CTEs, query optimization,
EXISTS vs IN, NULL handling, partitioning in Synapse/Redshift, MERGE statements,
EXPLAIN plans, index usage, or GROUP BY optimisation."""
    },
    {
        "label": "PySpark Code Tip",
        "template": "compare",
        "prompt": """Create LinkedIn card content with a REAL PySpark code example for data engineers.
Show a wrong (slow) way vs a right (fast) way, a genuine performance improvement.
Pick one topic: broadcast joins, avoiding .count() in loops, caching strategy,
repartition vs coalesce, avoiding UDFs, window functions in Spark,
Delta Lake MERGE, handling skew, AQE config."""
    },
    {
        "label": "Python Code Tip",
        "template": "compare",
        "prompt": """Create LinkedIn card content with a REAL Python code example for data engineers.
Show a messy "before" vs a clean "after" version, a practical improvement.
Pick one topic: generators for large files, dataclasses for pipeline config,
context managers for DB connections, type hints in ETL functions,
logging setup, error handling with retries, pathlib for file handling,
pydantic for data validation, pandas memory optimisation."""
    },
    {
        "label": "Azure Code Tip",
        "template": "single_block",
        "prompt": """Create LinkedIn card content with a REAL code or config example for Azure data engineers.
Use actual code, JSON config, ADF expression, or CLI commands.
Pick one topic: ADF dynamic pipelines, Databricks mount ADLS Gen2,
Synapse external tables, Delta Lake on ADLS, Azure Functions for ETL triggers,
Key Vault secrets in Databricks, Event Hubs + Spark streaming,
COPY INTO in Synapse, or Databricks job cluster config.
Hashtags should include #Azure #DataEngineering #Databricks style tags."""
    },
    {
        "label": "AWS Code Tip",
        "template": "single_block",
        "prompt": """Create LinkedIn card content with a REAL code or config example for AWS data engineers.
Use actual code, Glue script, Athena SQL, boto3, or CLI commands.
Pick one topic: Glue DynamicFrame vs DataFrame, S3 partition pruning in Athena,
boto3 S3 operations, EMR Spark submit config, Redshift COPY command,
Lambda trigger for S3 events, Step Functions for pipelines,
Lake Formation permissions, or Kinesis + Spark streaming.
Hashtags should include #AWS #DataEngineering #Glue style tags."""
    },
    {
        "label": "Databricks Code Tip",
        "template": "single_block",
        "prompt": """Create LinkedIn card content with a REAL Databricks code example.
Use actual PySpark or SQL code that runs on Databricks.
Pick one topic: Delta Lake MERGE for upserts, Auto Loader for incremental ingestion,
Delta time travel queries, OPTIMIZE and ZORDER commands,
Databricks Widgets for parameterised notebooks, Unity Catalog usage,
Structured Streaming with Delta, or Change Data Feed.
Hashtags should include #Databricks #DeltaLake #DataEngineering style tags."""
    },
    {
        "label": "Interview Q&A with Code",
        "template": "single_block",
        "prompt": """Create LinkedIn card content as a data engineering interview Q&A with real code.
Put the interview question itself in "title" (as a question).
Set "subtitle" to "Data Engineering Interview Question".
"code_lines" should be the code from a strong answer.
"insight_label" should be something like "WHY THIS ANSWER WORKS" and
"insight_text" should explain why it impresses interviewers.
Set "tip_text" to an empty string.
"footer_line" should invite people to share how they'd answer.
Topics: window functions, Spark joins, SCD Type 2,
idempotent pipeline design, incremental load, partition strategy.
Hashtags should include #DataEngineering #Interview style tags."""
    },
    {
        "label": "ADF Pipeline Tip",
        "template": "single_block",
        "prompt": """Create LinkedIn card content sharing a practical Azure Data Factory tip with a real example.
Use a real ADF pattern, expression, or JSON snippet in "code_lines".
Pick one topic: dynamic file paths with parameters, ForEach with parallelism,
error handling with If Condition, Lookup + ForEach pattern,
ADF expressions for date partitioning, tumbling window triggers,
parameterised linked services, or copy activity with schema mapping.
Hashtags should include #ADF #Azure #DataEngineering style tags."""
    },
    {
        "label": "Data Pipeline Design",
        "template": "single_block",
        "prompt": """Create LinkedIn card content about a data pipeline design pattern with real code.
Use actual code showing the pattern implementation in "code_lines" (8-12 lines is fine here).
Pick one topic: idempotent pipeline with DELETE+INSERT,
incremental load using watermark pattern, dead letter queue handling,
retry logic with exponential backoff, schema validation before load,
checkpointing in Spark streaming, or SCD Type 2 with PySpark MERGE.
"title" should be the pattern name."""
    },
    {
        "label": "Performance Optimisation",
        "template": "compare",
        "prompt": """Create LinkedIn card content about a performance optimisation with real before/after code.
Show actual before (slow) and after (fast) code with a specific performance gain
mentioned in "insight_text" (e.g. "10x faster" or "80% less shuffle").
Pick one topic: SQL query plan optimisation, Spark partition tuning,
Pandas vs Polars for large files, vectorised operations vs loops,
Redshift distribution keys, Synapse result set caching,
or Delta Lake ZORDER for faster queries."""
    },
    {
        "label": "Mistake and Fix with Code",
        "template": "compare",
        "prompt": """Create LinkedIn card content about a common data engineering mistake with code showing the fix.
Show the wrong code AND the correct code.
Pick one topic: SELECT * in production, missing idempotency,
collecting large DataFrames to driver, wrong join causing cartesian product,
not handling NULLs in aggregations, hardcoded dates in queries,
or not using pushdown predicates.
"insight_text" should explain the real production impact of the mistake."""
    },
    {
        "label": "Cheat Sheet with Code",
        "template": "cheat_sheet",
        "prompt": """Create LinkedIn card content as a practical code cheat sheet for data engineers.
Include 4 short real code examples as the 4 items.
Pick one topic: PySpark DataFrame operations cheat sheet,
SQL window functions with examples, Python one-liners for data cleaning,
Delta Lake commands cheat sheet, or Spark config settings that matter."""
    },
]

TEMPLATE_SCHEMAS = {
    "compare": SCHEMA_COMPARE,
    "single_block": SCHEMA_SINGLE,
    "cheat_sheet": SCHEMA_CHEATSHEET,
}

TEMPLATE_REQUIRED_KEYS = {
    "compare": ["title", "subtitle", "wrong_label", "wrong_code", "right_label",
                "right_code", "insight_label", "insight_text", "footer_line", "caption"],
    "single_block": ["title", "subtitle", "filename", "code_lines", "insight_label",
                      "insight_text", "tip_text", "footer_line", "caption"],
    "cheat_sheet": ["title", "subtitle", "items", "footer_line", "caption"],
}

# ── ROTATION LOGIC ────────────────────────────────────────────
def load_tracker():
    if os.path.exists(TRACKER_FILE):
        try:
            with open(TRACKER_FILE, "r") as f:
                return json.load(f).get("used", [])
        except:
            return []
    return []

def save_tracker(used: list):
    with open(TRACKER_FILE, "w") as f:
        json.dump({"used": used, "updated": str(datetime.now())}, f, indent=2)

def pick_content_type() -> dict:
    all_labels  = [c["label"] for c in CONTENT_TYPES]
    used_labels = load_tracker()

    unused = [c for c in CONTENT_TYPES if c["label"] not in used_labels]

    if not unused:
        print("All 12 content types used! Starting fresh rotation cycle.")
        used_labels = []
        unused = CONTENT_TYPES
        save_tracker([])

    chosen = random.choice(unused)
    used_labels.append(chosen["label"])
    save_tracker(used_labels)

    print(f"Rotation: {len(used_labels)}/12 types used this cycle")
    remaining = [l for l in all_labels if l not in used_labels]
    if remaining:
        print(f"Remaining types: {', '.join(remaining)}")

    return chosen

# ── PARSE / VALIDATE JSON FROM GEMINI ──────────────────────────
def _extract_json(text: str):
    text = text.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'```\s*$', '', text)
    text = text.strip()
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1:
        raise ValueError("no JSON object found")
    return json.loads(text[start:end+1])

def _validate(data: dict, template: str) -> bool:
    required = TEMPLATE_REQUIRED_KEYS[template]
    if not all(k in data for k in required):
        return False
    if template == "compare":
        return isinstance(data["wrong_code"], list) and isinstance(data["right_code"], list) \
            and len(data["wrong_code"]) > 0 and len(data["right_code"]) > 0
    if template == "single_block":
        return isinstance(data["code_lines"], list) and len(data["code_lines"]) > 0
    if template == "cheat_sheet":
        return isinstance(data["items"], list) and len(data["items"]) >= 3 and all(
            "label" in it and "explanation" in it and "code_lines" in it for it in data["items"]
        )
    return False

# ── GENERATE STRUCTURED POST DATA WITH GEMINI ──────────────────
def generate_post_data(content_type: dict) -> dict:
    print(f"Asking Gemini to generate: [{content_type['label']}]")

    schema = TEMPLATE_SCHEMAS[content_type["template"]]
    full_prompt = f"{content_type['prompt']}\n\n{schema}"

    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 8192,
            "temperature": 0.85,
            "responseMimeType": "application/json",
        }
    }

    models = [
        "gemini-2.0-flash",
        "gemini-2.5-flash",
        "gemini-2.0-flash-lite",
        "gemini-flash-latest",
        "gemini-flash-lite-latest",
    ]

    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
        for attempt in range(1, 3):
            try:
                print(f"Trying {model} — attempt {attempt}/2...")
                resp = requests.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=60
                )
                if resp.status_code == 200:
                    candidate = resp.json()["candidates"][0]
                    finish_reason = candidate.get("finishReason", "STOP")
                    text = candidate["content"]["parts"][0]["text"].strip()

                    if finish_reason == "MAX_TOKENS":
                        print(f"{model} hit token limit — trying next model...")
                        break

                    try:
                        data = _extract_json(text)
                    except (ValueError, json.JSONDecodeError) as e:
                        print(f"{model} returned invalid JSON ({e}) — trying next model...")
                        break

                    if not _validate(data, content_type["template"]):
                        print(f"{model} JSON missing required fields — trying next model...")
                        break

                    print(f"Generated valid content using {model}")
                    return data
                elif resp.status_code in [503, 429]:
                    print(f"{model} unavailable ({resp.status_code}) — trying next model...")
                    time.sleep(5)
                    break
                else:
                    print(f"Gemini API failed: {resp.status_code} - {resp.text}")
                    sys.exit(1)
            except requests.exceptions.Timeout:
                print(f"Timeout on {model} attempt {attempt}")
                if attempt == 2:
                    print("Moving to next model...")
                    break
                time.sleep(10)

    print("All models failed. Exiting.")
    sys.exit(1)

# ── RENDER THE CARD IMAGE ──────────────────────────────────────
def render_image(content_type: dict, data: dict, out_path: str) -> str:
    template = content_type["template"]
    if template == "compare":
        return render_compare_card(
            title=data["title"], subtitle=data["subtitle"],
            wrong_label=data["wrong_label"], wrong_code=data["wrong_code"],
            right_label=data["right_label"], right_code=data["right_code"],
            insight_label=data["insight_label"], insight_text=data["insight_text"],
            footer_line=data["footer_line"], out_path=out_path,
        )
    if template == "single_block":
        return render_single_block_card(
            title=data["title"], subtitle=data["subtitle"],
            filename=data.get("filename", "pipeline.py"), code_lines=data["code_lines"],
            insight_label=data["insight_label"], insight_text=data["insight_text"],
            tip_text=data.get("tip_text", ""), footer_line=data["footer_line"],
            out_path=out_path,
        )
    if template == "cheat_sheet":
        return render_cheat_sheet_card(
            title=data["title"], subtitle=data["subtitle"], items=data["items"],
            footer_line=data["footer_line"], out_path=out_path,
        )
    raise ValueError(f"Unknown template: {template}")

# ── CLEAN CAPTION TEXT ─────────────────────────────────────────
def clean_caption(text: str) -> str:
    """Strip any stray markdown Gemini might add to the caption and
    neutralise LinkedIn's domain-style auto-linker as a safety net."""
    text = re.sub(r'```[a-zA-Z]*\n?', '', text)
    text = text.replace('```', '').replace('`', '')
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'(?<!\w)\*(.+?)\*(?!\w)', r'\1', text)
    text = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'\1', text)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    text = re.sub(
        r'https?://\S+',
        lambda m: m.group().replace('https://', '').replace('http://', ''),
        text
    )
    text = re.sub(r'(?<=[A-Za-z0-9_])\.(?=[A-Za-z0-9_])', '.\u200b', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

# ── LINKEDIN: IMAGE UPLOAD + POST ──────────────────────────────
def register_upload():
    """Registers an image upload with LinkedIn. Returns (upload_url, asset_urn)."""
    print("Registering image upload with LinkedIn...")
    url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": PERSON_URN,
            "serviceRelationships": [
                {"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}
            ],
        }
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    if resp.status_code not in (200, 201):
        print(f"registerUpload failed: {resp.status_code} - {resp.text}")
        sys.exit(1)
    value = resp.json()["value"]
    upload_url = value["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset_urn = value["asset"]
    return upload_url, asset_urn

def upload_image_bytes(upload_url: str, image_path: str):
    print("Uploading image bytes...")
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    headers = {
        "Authorization": f"Bearer {LINKEDIN_TOKEN}",
        "Content-Type": "application/octet-stream",
    }
    resp = requests.put(upload_url, headers=headers, data=img_bytes, timeout=60)
    if resp.status_code not in (200, 201):
        print(f"Image upload failed: {resp.status_code} - {resp.text}")
        sys.exit(1)

def post_image_to_linkedin(asset_urn: str, caption_text: str):
    print("Publishing image post to LinkedIn...")
    headers = {
        "Authorization": f"Bearer {LINKEDIN_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    payload = {
        "author": PERSON_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": caption_text},
                "shareMediaCategory": "IMAGE",
                "media": [
                    {
                        "status": "READY",
                        "media": asset_urn,
                    }
                ],
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }
    resp = requests.post(
        "https://api.linkedin.com/v2/ugcPosts", headers=headers, json=payload, timeout=30
    )
    if resp.status_code == 201:
        print("SUCCESS - Posted to LinkedIn!")
    else:
        print(f"LinkedIn failed: {resp.status_code} - {resp.text}")
        sys.exit(1)

# ── MAIN ──────────────────────────────────────────────────────
def main():
    content_type = pick_content_type()
    print(f"Today's content type: [{content_type['label']}]")

    post_data = generate_post_data(content_type)
    image_path = render_image(content_type, post_data, IMAGE_OUT)
    caption = clean_caption(post_data["caption"])

    print("\n" + "=" * 50)
    print(f"Image saved to: {image_path}")
    print("CAPTION PREVIEW:")
    print(caption)
    print("=" * 50 + "\n")

    upload_url, asset_urn = register_upload()
    upload_image_bytes(upload_url, image_path)
    post_image_to_linkedin(asset_urn, caption)

    print("Done! Post is live on LinkedIn.")

if __name__ == "__main__":
    main()
