# ─────────────────────────────────────────────────────────────────────────────
# post_pdf_weekly_tech.py
# Weekly Thursday 7 PM IST LinkedIn Tech PDF Poster
#
# Covers (rotates through 8 topics):
#   1. Databricks Genie AI (NL-to-SQL, Genie Spaces)
#   2. VS Code + Claude AI Full Setup Guide
#   3. GitHub ↔ Databricks Integration (DABs, CI/CD)
#   4. Delta Live Tables (DLT) — Medallion Architecture
#   5. Unity Catalog & Role-Based Access Control (RBAC)
#   6. Data Catalog & Data Governance (Lineage, Purview)
#   7. AI Tools Cheat Sheet (Claude, Copilot, Cursor, Genie, Tabnine)
#   8. Databricks External Connections (ADLS, S3, Kafka, Event Hubs)
#
# Schedule : Every Thursday at 7 PM IST = 13:30 UTC (GitHub Actions)
# PDF size : 3–4 pages — cover · sections · code blocks · cheat sheet
# ─────────────────────────────────────────────────────────────────────────────

import requests, os, sys, json, time, io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, HRFlowable, Preformatted, KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# ── CREDENTIALS ───────────────────────────────────────────────────────────────
LINKEDIN_TOKEN = os.environ.get("LINKEDIN_TOKEN")
PERSON_URN     = os.environ.get("PERSON_URN")
GEMINI_KEY     = os.environ.get("GEMINI_KEY")
TRACKER_FILE   = "last_weekly_tech.json"

NOW  = datetime.now()
DATE = NOW.strftime("%d %B %Y")
print(f"Weekly Tech PDF Poster — {NOW:%A, %d %B %Y %H:%M} IST")
print("=" * 60)

# ── BRAND COLORS ──────────────────────────────────────────────────────────────
C_NAVY    = colors.HexColor("#003366")
C_BLUE    = colors.HexColor("#0A66C2")
C_LBLUE   = colors.HexColor("#D6E8FF")
C_CODE_BG = colors.HexColor("#F4F6F8")
C_CODE_BD = colors.HexColor("#CCCCCC")
C_WHITE   = colors.white
C_ORANGE  = colors.HexColor("#E8660A")
C_TEXT    = colors.HexColor("#1A1A1A")
C_GRAY    = colors.HexColor("#888888")
C_STRIPE  = colors.HexColor("#EEF4FF")
C_GREEN   = colors.HexColor("#1E7E34")
C_GBG     = colors.HexColor("#E6F4EA")

# ── TOPIC ROTATION ────────────────────────────────────────────────────────────
WEEKLY_TECH_TOPICS = [
    # ── Topic 1 ────────────────────────────────────────────────────────────────
    {
        "label": "Databricks Genie AI",
        "prompt": """Generate a comprehensive guide for a 3-4 page LinkedIn PDF about Databricks Genie AI.

Return ONLY valid JSON (no markdown, no backticks, no extra text outside the JSON):
{
  "title": "Databricks Genie AI — Complete Guide for Data Engineers",
  "subtitle": "Natural Language to SQL · Genie Spaces · Unity Catalog · Real Examples",
  "week_label": "Thursday Deep Dive | AI Tools for Data Engineers",
  "introduction": "2-3 sentences: what Databricks Genie is, how it turns plain English into SQL, and why data engineers should set it up for their teams.",
  "sections": [
    {
      "heading": "What Is Databricks Genie & How It Works",
      "content": "3-4 sentences covering: Genie is an AI assistant embedded in Databricks that converts natural language questions into SQL queries using the underlying LLM trained on your data catalog context. Explain NL2SQL flow, Genie Spaces concept, and how Unity Catalog powers the data understanding.",
      "code": "-- User asks: 'Show top 10 customers by revenue last quarter'\n-- Genie auto-generates:\nSELECT customer_name,\n       SUM(order_amount) AS total_revenue\nFROM   catalog.sales.orders\nWHERE  order_date >= DATE_TRUNC('quarter', CURRENT_DATE - INTERVAL 3 MONTHS)\nGROUP  BY customer_name\nORDER  BY total_revenue DESC\nLIMIT  10;",
      "code_label": "SQL — Genie auto-generated query from natural language"
    },
    {
      "heading": "Setting Up Genie Spaces Step by Step",
      "content": "3-4 sentences: A Genie Space is a curated AI workspace you configure with specific tables, business definitions, and sample questions. Walk through: create a Space, assign a SQL Warehouse, add table identifiers, define KPI terms (e.g. 'active customer'), add seed questions.",
      "code": "# Databricks REST API — Create a Genie Space\nimport requests\n\nheaders = {'Authorization': 'Bearer <DATABRICKS_TOKEN>'}\npayload = {\n    'title': 'Sales Analytics Genie',\n    'warehouse_id': 'abc123ef',\n    'table_identifiers': [\n        'main.sales.transactions',\n        'main.sales.customers'\n    ],\n    'sample_questions': [\n        'What is MoM revenue growth?',\n        'Which product had highest returns this week?'\n    ]\n}\nresp = requests.post(\n    'https://<workspace>.azuredatabricks.net/api/2.0/genie/spaces',\n    headers=headers, json=payload\n)\nprint(resp.json()['space_id'])",
      "code_label": "Python — Genie Space setup via Databricks REST API"
    },
    {
      "heading": "Unity Catalog Integration — Security & Governance",
      "content": "3-4 sentences: Genie fully respects Unity Catalog table/row/column-level permissions. A user querying Genie only sees data they are granted SELECT on. Row-level security and column masking policies are automatically applied. This makes Genie safe to roll out to non-technical business users.",
      "code": "-- Grant SELECT to analysts group (UC)\nGRANT SELECT ON TABLE main.sales.transactions\n  TO `data-analysts`;\n\n-- Column masking for PII\nALTER TABLE main.sales.customers\nALTER COLUMN email\nSET MASK main.masks.email_mask\n  USING COLUMNS (customer_tier);\n\n-- Row-level filter policy\nCREATE ROW FILTER main.filters.region_filter\nON TABLE main.sales.transactions (region STRING)\n  RETURN region = SESSION_USER_GROUP('region');",
      "code_label": "SQL — Unity Catalog security applied automatically to Genie queries"
    },
    {
      "heading": "Real-World Patterns & Pro Tips",
      "content": "3-4 sentences: Data engineers who set up Genie properly see analyst SQL request tickets drop by 60-70%. Key tips: (1) add business term definitions so Genie understands company-specific KPIs; (2) pair Genie Spaces with Serverless SQL Warehouses for cold-start speed; (3) use the Genie conversation API to embed NL querying into internal dashboards; (4) review Genie query history weekly to improve prompts.",
      "code": "",
      "code_label": ""
    }
  ],
  "cheat_sheet_rows": [
    ["Feature / Term", "What It Does", "Real-World Use Case"],
    ["Genie Space", "Curated AI workspace with tables + business context", "Sales team self-service analytics"],
    ["NL2SQL", "Converts natural language to SQL automatically", "Non-SQL users query data in plain English"],
    ["Warehouse ID", "SQL compute assigned to a Genie Space", "Point to Serverless warehouse for fast cold start"],
    ["Business Definitions", "Custom KPI/metric terms Genie learns", "Teach Genie what 'active customer' means"],
    ["Sample Questions", "Seed questions to improve Genie accuracy", "Common business queries answered instantly"],
    ["UC Integration", "Genie respects table/row/column permissions", "Analysts only see data they are authorized for"],
    ["Genie REST API", "Programmatic Genie Space management", "Embed Genie NL queries into internal tools"],
    ["Conversation History", "Genie remembers context within a session", "Ask follow-up questions without repeating context"],
    ["Query History", "Review all Genie-generated SQL queries", "Audit, improve prompts, catch misinterpreted questions"],
    ["/api/2.0/genie/spaces", "API endpoint for Genie Space CRUD", "Automate Space creation in CI/CD pipelines"]
  ],
  "key_takeaways": [
    "Genie AI converts natural language into SQL — analysts need zero SQL skills to query data",
    "Create Genie Spaces to scope AI access to specific tables and business domains",
    "Genie fully respects Unity Catalog permissions — row/column security is automatic",
    "Add business term definitions so Genie understands your company's specific KPIs",
    "Use Serverless SQL Warehouses with Genie for near-instant cold start and cost efficiency",
    "Review Genie query history weekly to tune prompts and catch misinterpretations",
    "Embed Genie via REST API into internal dashboards — analysts self-serve without tickets"
  ],
  "linkedin_caption": "🤖 Databricks Genie AI — Your Data Team's Self-Service Superpower!\\n\\nTired of answering 'Can you write a SQL for me?' 50x a week?\\n\\nGenie lets your analysts type plain English and get production-quality SQL instantly — fully secured by Unity Catalog.\\n\\nThis week's Thursday PDF covers setup, real code, Unity Catalog integration, and a cheat sheet. 3 pages. Save it!\\n\\n📥 Drop a comment — does your team use Genie yet?",
  "hashtags": "#Databricks #GenieAI #DataEngineering #DeltaLake #UnityCatalog #NL2SQL #AI #DataAnalytics"
}""",
    },

    # ── Topic 2 ────────────────────────────────────────────────────────────────
    {
        "label": "VS Code + Claude AI Setup Guide",
        "prompt": """Generate a comprehensive guide for a 3-4 page LinkedIn PDF about setting up VS Code with Claude AI and other AI coding tools.

Return ONLY valid JSON (no markdown, no backticks, no extra text outside JSON):
{
  "title": "VS Code + Claude AI — The Ultimate Data Engineer Setup Guide",
  "subtitle": "Extensions · Settings · Scoring · GitHub Copilot vs Claude · Cheat Sheet",
  "week_label": "Thursday Deep Dive | Developer Productivity Series",
  "introduction": "2-3 sentences about how AI-powered coding assistants have transformed how data engineers write pipelines, debug PySpark, and generate SQL — and why setting up VS Code properly is now a core skill.",
  "sections": [
    {
      "heading": "Essential VS Code Extensions for Data Engineers",
      "content": "3-4 sentences: The right extension stack turns VS Code into a full data engineering IDE. Must-have extensions: GitHub Copilot (AI completion), Claude for VS Code / Continue (Claude integration), Pylance + Python (type checking), Databricks Extension (run notebooks from VS Code), SQLTools (query databases), Rainbow CSV, Git Graph, Remote SSH for connecting to Databricks clusters.",
      "code": "// VS Code settings.json — Recommended data engineer config\n{\n  \"python.defaultInterpreterPath\": \"/usr/bin/python3\",\n  \"editor.formatOnSave\": true,\n  \"[python]\": {\n    \"editor.defaultFormatter\": \"ms-python.black-formatter\"\n  },\n  \"github.copilot.enable\": { \"*\": true },\n  \"continue.enableTabAutocomplete\": true,\n  \"databricks.host\": \"https://<workspace>.azuredatabricks.net\",\n  \"sqltools.connections\": [],\n  \"editor.rulers\": [88],\n  \"files.autoSave\": \"afterDelay\"\n}",
      "code_label": "JSON — VS Code settings.json for data engineering"
    },
    {
      "heading": "Claude AI in VS Code — Setup & Real-Time Coding",
      "content": "3-4 sentences: Claude can be integrated into VS Code via the Continue extension (open source, free). Once connected to Anthropic API, Claude becomes an inline coding assistant. Use it to: generate PySpark transformations from comments, explain complex SQL, review pipeline code, write unit tests, convert Pandas to PySpark. Claude scores well on code reasoning — especially for multi-step data pipeline logic.",
      "code": "# ~/.continue/config.json — Add Claude as Continue provider\n{\n  \"models\": [\n    {\n      \"title\": \"Claude Sonnet\",\n      \"provider\": \"anthropic\",\n      \"model\": \"claude-sonnet-4-5\",\n      \"apiKey\": \"sk-ant-...\"\n    }\n  ],\n  \"tabAutocompleteModel\": {\n    \"title\": \"Claude Haiku (Fast)\",\n    \"provider\": \"anthropic\",\n    \"model\": \"claude-haiku-3\",\n    \"apiKey\": \"sk-ant-...\"\n  }\n}",
      "code_label": "JSON — Continue extension config for Claude AI"
    },
    {
      "heading": "GitHub Copilot vs Claude — Scoring & When to Use Which",
      "content": "3-4 sentences comparing GitHub Copilot and Claude for data engineering tasks. Copilot excels at line-level autocompletion and is deeply integrated into VS Code. Claude excels at multi-step reasoning, explaining complex logic, code review, and longer context tasks like reviewing a full PySpark script. For a data engineer: use Copilot for speed (tab completion), use Claude for intelligence (ask, review, refactor).",
      "code": "# Real-time coding workflow with Claude:\n# 1. Write a comment describing what you need\n# Comment: 'Read Parquet from ADLS, deduplicate on id+date, write Delta'\n\n# Claude generates:\nfrom pyspark.sql import SparkSession\nfrom pyspark.sql.functions import row_number\nfrom pyspark.sql.window import Window\n\nspark = SparkSession.builder.getOrCreate()\n\ndf = spark.read.parquet('abfss://raw@storageacct.dfs.core.windows.net/data/')\n\nwindow = Window.partitionBy('id').orderBy('date')\ndf_deduped = (df.withColumn('rn', row_number().over(window))\n                .filter('rn = 1')\n                .drop('rn'))\n\ndf_deduped.write.format('delta').mode('overwrite').save('/mnt/silver/data')",
      "code_label": "Python — Claude generates full PySpark from a plain comment"
    },
    {
      "heading": "Productivity Tips & Keyboard Shortcuts",
      "content": "3-4 sentences: Knowing VS Code keyboard shortcuts cuts coding time significantly. Key AI shortcuts: Ctrl+I (Copilot inline chat), Ctrl+Shift+I (Continue chat with Claude), Ctrl+Shift+P (command palette — run 'Databricks: Sync to Workspace'). Also: use @workspace in Copilot chat to ask questions about your entire codebase, use /explain to get line-by-line explanation, and /tests to generate pytest unit tests.",
      "code": "",
      "code_label": ""
    }
  ],
  "cheat_sheet_rows": [
    ["Tool / Shortcut", "What It Does", "Data Engineering Use Case"],
    ["GitHub Copilot", "AI tab completion (line-level)", "Fast boilerplate: PySpark, SQL, YAML"],
    ["Continue + Claude", "AI chat inside VS Code (multi-turn)", "Review pipelines, explain Spark errors"],
    ["Databricks Extension", "Run/sync notebooks from VS Code", "Edit notebooks locally, run on cluster"],
    ["Pylance + Black", "Type checking + auto code formatting", "Clean PySpark code with type hints"],
    ["SQLTools", "Query databases inside VS Code", "Test SQL against dev warehouse directly"],
    ["Ctrl + I", "Copilot inline chat at cursor", "Fix a single line or function quickly"],
    ["Ctrl + Shift + I", "Continue chat panel (Claude)", "Ask Claude to review entire pipeline file"],
    ["/explain", "Copilot: explain selected code", "Understand inherited legacy PySpark code"],
    ["/tests", "Copilot: generate unit tests", "Auto-generate pytest for ETL functions"],
    ["@workspace", "Copilot: ask about entire repo", "Find where a table schema is defined"],
    ["Remote SSH", "Connect VS Code to remote Databricks", "Edit cluster-side code with local IDE"]
  ],
  "key_takeaways": [
    "Install Continue extension + Claude API key for inline Claude AI inside VS Code",
    "Use GitHub Copilot for fast tab completion, Claude for code review and complex reasoning",
    "Databricks VS Code Extension lets you run and sync notebooks without leaving your editor",
    "Pylance + Black formatter enforces type-safe, clean PySpark code automatically on save",
    "Ctrl+I (Copilot inline) and Ctrl+Shift+I (Continue/Claude) are your two most-used shortcuts",
    "Use @workspace in Copilot chat to ask questions across your entire codebase",
    "The right VS Code setup reduces pipeline development time by 40–60% for data engineers"
  ],
  "linkedin_caption": "⚡ VS Code + Claude AI — The Setup Every Data Engineer Needs in 2025!\\n\\nI see people using VS Code without AI extensions and I want to fix that.\\n\\nThis week's Thursday PDF is a complete setup guide: extensions, Claude integration, Copilot vs Claude comparison, keyboard shortcuts — 3 pages with cheat sheet.\\n\\n📥 Save it. Share it with your team.\\n\\nDo you use Claude, Copilot, or something else for coding? Drop below 👇",
  "hashtags": "#VSCode #ClaudeAI #GitHubCopilot #DataEngineering #DeveloperProductivity #AI #Python #PySpark"
}""",
    },

    # ── Topic 3 ────────────────────────────────────────────────────────────────
    {
        "label": "GitHub & Databricks Integration",
        "prompt": """Generate a comprehensive guide for a 3-4 page LinkedIn PDF about integrating GitHub with Databricks for data engineers.

Return ONLY valid JSON (no markdown, no backticks, no extra text outside JSON):
{
  "title": "GitHub ↔ Databricks Integration — Complete CI/CD Guide",
  "subtitle": "Databricks Asset Bundles · Git Folders · GitHub Actions · Secrets",
  "week_label": "Thursday Deep Dive | DataOps & DevOps Series",
  "introduction": "2-3 sentences: most data teams treat notebooks as ad-hoc scripts — but production pipelines need version control, code review, and automated deployments. GitHub + Databricks integration via Asset Bundles is the industry standard for DataOps.",
  "sections": [
    {
      "heading": "Databricks Asset Bundles (DABs) — What & Why",
      "content": "3-4 sentences: Databricks Asset Bundles (DABs) is the official framework to define Databricks resources (jobs, pipelines, clusters) as code using YAML. Think Terraform but for Databricks. DABs let you version-control your entire Databricks workspace configuration in GitHub and deploy with a single command: databricks bundle deploy.",
      "code": "# databricks.yml — Databricks Asset Bundle definition\nbundle:\n  name: sales-pipeline\n\ntargets:\n  dev:\n    workspace:\n      host: https://dev.azuredatabricks.net\n  prod:\n    workspace:\n      host: https://prod.azuredatabricks.net\n\nresources:\n  jobs:\n    daily_sales_etl:\n      name: daily-sales-etl-${bundle.target}\n      tasks:\n        - task_key: ingest\n          notebook_task:\n            notebook_path: ./notebooks/01_ingest.py\n          new_cluster:\n            spark_version: 15.4.x-scala2.12\n            num_workers: 4\n        - task_key: transform\n          depends_on:\n            - task_key: ingest\n          notebook_task:\n            notebook_path: ./notebooks/02_transform.py",
      "code_label": "YAML — databricks.yml Asset Bundle definition"
    },
    {
      "heading": "Git Folders — Version Control Notebooks Directly",
      "content": "3-4 sentences: Databricks Git Folders sync your GitHub repository directly into the Databricks workspace. When you push code to GitHub, the Git Folder reflects the change. This means analysts and engineers can work in Databricks notebooks while the code is actually stored in GitHub — best of both worlds.",
      "code": "# GitHub Actions — Auto-sync Git Folder on push to main\nname: Databricks Git Folder Sync\non:\n  push:\n    branches: [main]\njobs:\n  sync:\n    runs-on: ubuntu-latest\n    steps:\n      - name: Trigger Databricks Git Folder Pull\n        run: |\n          curl -X POST \\\n            -H 'Authorization: Bearer ${{ secrets.DATABRICKS_TOKEN }}' \\\n            -H 'Content-Type: application/json' \\\n            https://${{ secrets.DATABRICKS_HOST }}/api/2.0/repos/${{ secrets.REPO_ID }}/checkout \\\n            -d '{\"branch\": \"main\"}'",
      "code_label": "YAML — GitHub Actions sync Git Folder on every push to main"
    },
    {
      "heading": "Full CI/CD Pipeline — GitHub Actions + DABs",
      "content": "3-4 sentences: A production DABs CI/CD pipeline: on PR open → run unit tests with pytest; on merge to main → deploy to dev environment; on release tag → deploy to prod. Use GitHub Environments for approval gates before prod deployments. Store Databricks tokens and workspace URLs in GitHub Secrets.",
      "code": "# .github/workflows/deploy.yml\nname: Deploy to Databricks\non:\n  push:\n    branches: [main]\n  release:\n    types: [published]\njobs:\n  deploy:\n    runs-on: ubuntu-latest\n    environment: ${{ github.event_name == 'release' && 'prod' || 'dev' }}\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-python@v5\n        with:\n          python-version: '3.11'\n      - run: pip install databricks-cli\n      - run: databricks bundle validate\n        env:\n          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}\n          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}\n      - run: databricks bundle deploy --target ${{ github.event_name == 'release' && 'prod' || 'dev' }}\n        env:\n          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}\n          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}",
      "code_label": "YAML — Full CI/CD with dev/prod environment targets"
    },
    {
      "heading": "Secrets, Security & Best Practices",
      "content": "3-4 sentences: Never hardcode Databricks tokens — store in GitHub Secrets and reference via ${{ secrets.DATABRICKS_TOKEN }}. Use Databricks Service Principals (not personal tokens) for CI/CD. Rotate tokens every 90 days. Use GitHub Environments with required reviewers for production deployments. Store sensitive config (connection strings) in Databricks Secrets backed by Azure Key Vault.",
      "code": "# Databricks CLI — Create a secret scope backed by Azure Key Vault\ndatabricks secrets create-scope \\\n  --scope prod-secrets \\\n  --scope-backend-type AZURE_KEYVAULT \\\n  --resource-id /subscriptions/.../vaults/mykeyvault \\\n  --dns-name https://mykeyvault.vault.azure.net/\n\n# Reference the secret in a notebook:\nconnection_string = dbutils.secrets.get(\n    scope='prod-secrets',\n    key='adls-connection-string'\n)",
      "code_label": "Bash + Python — Databricks Secrets backed by Azure Key Vault"
    }
  ],
  "cheat_sheet_rows": [
    ["Concept / Command", "What It Does", "When to Use"],
    ["Databricks Asset Bundles", "Define Databricks resources as YAML code", "Version-control jobs, pipelines, clusters"],
    ["databricks bundle deploy", "Deploy DABs resources to a target workspace", "Deploy to dev or prod from CLI/CI-CD"],
    ["databricks bundle validate", "Validate YAML config before deploying", "Run in CI pipeline on every PR"],
    ["Git Folders / Repos API", "Sync GitHub repo into Databricks workspace", "Let analysts code in notebooks, backed by git"],
    ["GitHub Environments", "Approval gates for deployment stages", "Require reviewer before prod deployment"],
    ["Service Principal", "Non-human identity for CI/CD auth", "Use instead of personal token in pipelines"],
    ["GitHub Secrets", "Encrypted variables for CI/CD", "Store DATABRICKS_TOKEN, HOST, passwords"],
    ["Databricks Secret Scope", "Encrypted secrets inside Databricks", "Store ADLS keys, DB passwords in notebooks"],
    ["--target flag", "Specify dev/prod in DABs commands", "databricks bundle deploy --target prod"],
    ["Pre-commit hooks", "Run linting/tests before every commit", "Catch PySpark errors before they reach CI"]
  ],
  "key_takeaways": [
    "Use Databricks Asset Bundles (DABs) to define all Databricks resources as version-controlled YAML code",
    "Git Folders give analysts the Databricks notebook UX while keeping code safely in GitHub",
    "Full CI/CD: PR triggers tests, merge-to-main deploys to dev, release tag deploys to prod",
    "Always use Service Principals — never personal tokens — in GitHub Actions pipelines",
    "Store all secrets in GitHub Secrets + Databricks Secret Scopes backed by Azure Key Vault",
    "Use GitHub Environments with required reviewers as an approval gate before production deployments",
    "databricks bundle validate in every PR catches misconfigurations before they hit live workspaces"
  ],
  "linkedin_caption": "🚀 GitHub ↔ Databricks — The CI/CD Setup Every Data Team Needs!\\n\\nIf your team is still copy-pasting notebook code or running manual deployments — this is for you.\\n\\nThis week's Thursday PDF covers Databricks Asset Bundles, Git Folders, full GitHub Actions CI/CD pipeline, and secrets management. 3 pages + cheat sheet.\\n\\n📥 Save it. What's your current Databricks deployment process?\\n\\n#Databricks #GitHub #DataEngineering #DevOps #DataOps #CICD #DABs",
  "hashtags": "#Databricks #GitHub #DataEngineering #DevOps #DataOps #CICD #DatabricksAssetBundles #GitOps"
}""",
    },

    # ── Topic 4 ────────────────────────────────────────────────────────────────
    {
        "label": "Delta Live Tables (DLT) Mastery",
        "prompt": """Generate a comprehensive guide for a 3-4 page LinkedIn PDF about Delta Live Tables (DLT) for data engineers.

Return ONLY valid JSON (no markdown, no backticks, no extra text outside JSON):
{
  "title": "Delta Live Tables (DLT) — Complete Mastery Guide",
  "subtitle": "Medallion Architecture · Expectations · CDC · Streaming · Cheat Sheet",
  "week_label": "Thursday Deep Dive | Databricks & Delta Lake Series",
  "introduction": "2-3 sentences: Delta Live Tables is Databricks' declarative ETL framework — you declare WHAT data should look like, DLT handles HOW to run it reliably, incrementally, and at scale. It is the modern replacement for hand-coded Spark pipelines.",
  "sections": [
    {
      "heading": "DLT Fundamentals — Bronze · Silver · Gold",
      "content": "3-4 sentences explaining the Medallion architecture in DLT: Bronze = raw ingestion (append-only), Silver = cleaned/enriched data with quality checks, Gold = business-level aggregates for BI/ML. DLT manages incremental processing automatically — only new data is processed each run, saving cost and compute.",
      "code": "import dlt\nfrom pyspark.sql.functions import col, current_timestamp\n\n# Bronze — raw ingestion via Auto Loader\n@dlt.table(comment='Raw orders from ADLS landing zone')\ndef orders_bronze():\n    return (\n        spark.readStream\n             .format('cloudFiles')\n             .option('cloudFiles.format', 'json')\n             .load('abfss://landing@storage.dfs.core.windows.net/orders/')\n             .withColumn('ingested_at', current_timestamp())\n    )\n\n# Silver — cleaned with quality expectations\n@dlt.table(comment='Validated and cleaned orders')\n@dlt.expect_or_drop('valid_amount', 'order_amount > 0')\n@dlt.expect_or_drop('valid_customer', 'customer_id IS NOT NULL')\ndef orders_silver():\n    return dlt.read_stream('orders_bronze').select(\n        col('order_id'), col('customer_id'),\n        col('order_amount').cast('double'),\n        col('order_date').cast('date')\n    )",
      "code_label": "Python — DLT Bronze and Silver tables with Auto Loader"
    },
    {
      "heading": "DLT Expectations — Data Quality as Code",
      "content": "3-4 sentences: DLT Expectations are declarative data quality rules. Three modes: @dlt.expect (warn but keep bad rows), @dlt.expect_or_drop (remove bad rows), @dlt.expect_or_fail (stop the pipeline on violation). All constraint metrics are tracked in the DLT event log — you get data quality dashboards for free.",
      "code": "import dlt\n\n@dlt.table\n# Warn: track metric, keep bad rows\n@dlt.expect('non_null_email', 'email IS NOT NULL')\n# Drop: remove invalid rows silently\n@dlt.expect_or_drop('valid_age', 'age BETWEEN 18 AND 120')\n# Fail: stop pipeline — critical business rule\n@dlt.expect_or_fail('unique_order_id', 'COUNT(DISTINCT order_id) = COUNT(*)')\ndef customers_silver():\n    return dlt.read_stream('customers_bronze')\n\n# Query expectation metrics from event log\ndf_quality = spark.sql(\"\"\"\n    SELECT expectations, timestamp\n    FROM   event_log('customers_silver')\n    WHERE  event_type = 'flow_progress'\n\"\"\")",
      "code_label": "Python + SQL — DLT Expectations and quality metrics"
    },
    {
      "heading": "Change Data Capture (CDC) with DLT APPLY CHANGES",
      "content": "3-4 sentences: DLT natively handles CDC via the APPLY CHANGES INTO command. It processes insert/update/delete events from sources like Debezium, Kafka, or SQL Server CDC and applies them to a target Delta table as an SCD Type 1 (or Type 2) — all without you writing merge logic manually.",
      "code": "import dlt\n\n# Source: CDC events from Kafka/Debezium\n@dlt.table\ndef customers_cdc_feed():\n    return (\n        spark.readStream.format('kafka')\n             .option('kafka.bootstrap.servers', 'broker:9092')\n             .option('subscribe', 'dbserver.public.customers')\n             .load()\n    )\n\n# Apply CDC changes — DLT handles MERGE automatically\ndlt.apply_changes(\n    target      = 'customers_silver',\n    source      = 'customers_cdc_feed',\n    keys        = ['customer_id'],\n    sequence_by = 'cdc_timestamp',\n    apply_as_deletes = expr('op = \\'d\\''),\n    except_column_list = ['op', 'cdc_timestamp']\n)",
      "code_label": "Python — DLT APPLY CHANGES for CDC (SCD Type 1)"
    },
    {
      "heading": "DLT Pipeline Configuration & Cost Tips",
      "content": "3-4 sentences: DLT pipelines are configured as JSON or via Databricks UI — set continuous vs triggered mode, cluster size, photon acceleration, and target schema. Use TRIGGERED mode for batch and CONTINUOUS mode for near-real-time streaming. Photon acceleration is recommended for DLT and gives 2-4x speedup on Silver/Gold transformations at a small cost premium.",
      "code": "",
      "code_label": ""
    }
  ],
  "cheat_sheet_rows": [
    ["Command / Decorator", "What It Does", "Use Case"],
    ["@dlt.table", "Declare a DLT table", "Every Bronze/Silver/Gold table definition"],
    ["@dlt.view", "Declare a temporary view (not stored)", "Intermediate transformations in pipeline"],
    ["@dlt.expect", "Warn on violation, keep bad rows", "Non-critical quality checks"],
    ["@dlt.expect_or_drop", "Drop bad rows, continue pipeline", "Remove nulls / invalid ranges"],
    ["@dlt.expect_or_fail", "Stop pipeline on violation", "Critical business rules must pass"],
    ["dlt.read_stream()", "Read from another DLT table as stream", "Silver reading from Bronze (incremental)"],
    ["dlt.read()", "Read from another DLT table as batch", "Gold aggregations from Silver"],
    ["APPLY CHANGES INTO", "CDC upsert/delete into a Delta table", "Sync from Debezium / Kafka CDC feed"],
    ["Auto Loader", "Incrementally ingest files from cloud storage", "Bronze layer ingestion from ADLS/S3"],
    ["TRIGGERED mode", "Run pipeline on schedule or manual trigger", "Nightly batch ETL jobs"],
    ["CONTINUOUS mode", "Pipeline runs permanently as streaming", "Near-real-time dashboards (latency < 1 min)"]
  ],
  "key_takeaways": [
    "DLT is declarative — define WHAT your data should look like, DLT handles incremental execution",
    "Medallion Architecture: Bronze (raw) → Silver (clean + validated) → Gold (business aggregates)",
    "DLT Expectations are data quality rules built into the pipeline — tracked automatically",
    "Use @expect_or_drop for invalid rows, @expect_or_fail for critical business constraints",
    "APPLY CHANGES INTO handles CDC (insert/update/delete) from Kafka/Debezium with zero merge code",
    "Auto Loader in Bronze layer incrementally ingests new files — no manual file tracking needed",
    "Use TRIGGERED mode for batch and CONTINUOUS mode for near-real-time — pick based on SLA"
  ],
  "linkedin_caption": "🏗️ Delta Live Tables (DLT) — The Framework That Replaces 500 Lines of Spark Code!\\n\\nI keep seeing teams write complex Spark merge logic when DLT handles it declaratively in 10 lines.\\n\\nThis Thursday's PDF: DLT fundamentals, Bronze/Silver/Gold, Expectations, CDC with APPLY CHANGES, cheat sheet. 3 pages.\\n\\n📥 Save it for your next pipeline build!\\n\\nAre you using DLT in production? What's your experience?",
  "hashtags": "#DeltaLiveTables #DLT #Databricks #DataEngineering #DeltaLake #ETL #ApacheSpark #DataPipelines"
}""",
    },

    # ── Topic 5 ────────────────────────────────────────────────────────────────
    {
        "label": "Unity Catalog & RBAC",
        "prompt": """Generate a comprehensive guide for a 3-4 page LinkedIn PDF about Databricks Unity Catalog and Role-Based Access Control (RBAC).

Return ONLY valid JSON (no markdown, no backticks, no extra text outside JSON):
{
  "title": "Unity Catalog & RBAC — Data Governance at Scale in Databricks",
  "subtitle": "Metastore · Namespaces · Grants · Row/Column Security · Data Sharing",
  "week_label": "Thursday Deep Dive | Data Governance Series",
  "introduction": "2-3 sentences: Unity Catalog is Databricks' unified governance layer that brings SQL-based access control, data lineage, and auditing to all Databricks assets — tables, files, ML models, and Delta Sharing. It's the single control plane for who sees what data.",
  "sections": [
    {
      "heading": "Unity Catalog Architecture — 3-Level Namespace",
      "content": "3-4 sentences: Unity Catalog uses a 3-level namespace: Catalog → Schema (Database) → Table/View. You assign permissions at each level — GRANT on a catalog trickles down, or you can grant on individual tables. Best practice: one catalog per environment (dev/staging/prod) and one catalog per domain (sales, hr, finance).",
      "code": "-- Create the catalog hierarchy\nCREATE CATALOG IF NOT EXISTS prod;\nCREATE CATALOG IF NOT EXISTS dev;\n\nCREATE SCHEMA IF NOT EXISTS prod.sales;\nCREATE SCHEMA IF NOT EXISTS prod.finance;\n\n-- Grant catalog-level access to a group\nGRANT USE CATALOG ON CATALOG prod TO `data-engineers`;\nGRANT USE SCHEMA   ON SCHEMA  prod.sales TO `data-analysts`;\nGRANT SELECT       ON TABLE   prod.sales.transactions TO `data-analysts`;\n\n-- List grants on a table\nSHOW GRANTS ON TABLE prod.sales.transactions;",
      "code_label": "SQL — Unity Catalog 3-level namespace and grants"
    },
    {
      "heading": "Row-Level Security & Column Masking",
      "content": "3-4 sentences: Unity Catalog supports row-level filters and column masking policies — data is secured at query time, not at application level. A column mask can hide PII (e.g. show full email only to admins). A row filter ensures a sales rep only sees their own region's data even when querying the same shared table.",
      "code": "-- Column masking: hide PII from non-admins\nCREATE FUNCTION prod.masks.mask_email(email STRING)\n  RETURN CASE\n    WHEN is_account_group_member('pii-admins') THEN email\n    ELSE CONCAT(LEFT(email, 2), '***@***.***')\n  END;\n\nALTER TABLE prod.sales.customers\n  ALTER COLUMN email SET MASK prod.masks.mask_email;\n\n-- Row-level filter: reps see only their region\nCREATE FUNCTION prod.filters.region_filter(region STRING)\n  RETURN region = current_user()  -- map user → region in a lookup table\n       OR is_account_group_member('sales-admins');\n\nALTER TABLE prod.sales.transactions\n  SET ROW FILTER prod.filters.region_filter ON (region);",
      "code_label": "SQL — Column masking and row-level security in Unity Catalog"
    },
    {
      "heading": "Data Lineage & Audit Logs",
      "content": "3-4 sentences: Unity Catalog automatically tracks column-level data lineage — you can see exactly which upstream table a column came from, through all transformations. Audit logs capture every query, GRANT, and REVOKE — stored in the system.access tables for compliance reporting. This is critical for GDPR, HIPAA, and SOC 2.",
      "code": "-- Query built-in lineage via system tables (Unity Catalog)\nSELECT source_table_full_name,\n       target_table_full_name,\n       event_time\nFROM   system.access.table_lineage\nWHERE  target_table_full_name = 'prod.sales.transactions'\nORDER  BY event_time DESC\nLIMIT  20;\n\n-- Audit: who queried a sensitive table?\nSELECT user_identity.email, action_name, request_params, event_time\nFROM   system.access.audit\nWHERE  request_params.full_name_arg = 'prod.finance.payroll'\n  AND  event_date >= CURRENT_DATE - 7;",
      "code_label": "SQL — Query data lineage and audit logs from system tables"
    },
    {
      "heading": "Delta Sharing & External Data Sharing",
      "content": "3-4 sentences: Delta Sharing is an open protocol for sharing live Delta tables across organizations or clouds — the recipient does not need Databricks. You create a Share, add tables, create a Recipient, and they access data via a credential file. This replaces manual CSV exports or S3 bucket sharing.",
      "code": "",
      "code_label": ""
    }
  ],
  "cheat_sheet_rows": [
    ["Command / Concept", "What It Does", "Real-World Use Case"],
    ["CREATE CATALOG", "Top-level namespace (per env or domain)", "prod / dev / hr / finance catalogs"],
    ["CREATE SCHEMA", "Database within a catalog", "prod.sales, prod.finance schemas"],
    ["GRANT SELECT", "Allow group to read a table", "data-analysts can read sales.transactions"],
    ["GRANT MODIFY", "Allow insert/update/delete on table", "ETL service account writes to silver tables"],
    ["REVOKE", "Remove a previously granted permission", "Remove access when project ends"],
    ["SHOW GRANTS", "List all permissions on an object", "Audit who has access to a sensitive table"],
    ["Column Masking", "Hide/transform column values by role", "Mask SSN/email for non-PII-admins"],
    ["Row Filter", "Filter rows returned based on user identity", "Sales reps see only their region"],
    ["system.access.audit", "Built-in audit log for all data access", "GDPR/SOC2 compliance reporting"],
    ["system.access.table_lineage", "Column-level data lineage tracking", "Trace where a KPI metric comes from"],
    ["Delta Sharing", "Share live Delta tables across orgs/clouds", "Partner data sharing without data copy"]
  ],
  "key_takeaways": [
    "Unity Catalog uses a 3-level namespace: Catalog → Schema → Table — grant permissions at any level",
    "Column masking hides PII at query time — no application-level code changes needed",
    "Row-level filters ensure users automatically see only the data they are authorized for",
    "Audit logs in system.access.audit capture every query and permission change — essential for compliance",
    "Data lineage in Unity Catalog is automatic — trace column origins through all transformations",
    "Delta Sharing shares live Delta tables across organizations or clouds — no data duplication",
    "Best practice: one catalog per environment (dev/prod) and one per business domain (sales/finance)"
  ],
  "linkedin_caption": "🔐 Unity Catalog & RBAC — The Right Way to Govern Data in Databricks!\\n\\nRow-level security. Column masking. Automatic lineage. Audit logs. All built-in — no extra tooling.\\n\\nThis Thursday's PDF is a complete Unity Catalog guide: architecture, GRANT commands, row/column security, audit queries, and a full cheat sheet.\\n\\n📥 Download and share with your data governance team!\\n\\nIs your org using Unity Catalog yet?",
  "hashtags": "#UnityCatalog #Databricks #DataGovernance #RBAC #DataEngineering #DataSecurity #DeltaSharing #GDPR"
}""",
    },

    # ── Topic 6 ────────────────────────────────────────────────────────────────
    {
        "label": "Data Catalog & Data Governance",
        "prompt": """Generate a comprehensive guide for a 3-4 page LinkedIn PDF about Data Catalog, Data Lineage, and Data Governance tools for data engineers.

Return ONLY valid JSON (no markdown, no backticks, no extra text outside JSON):
{
  "title": "Data Catalog & Data Governance — Complete Practical Guide",
  "subtitle": "Unity Catalog · Microsoft Purview · OpenLineage · Tags · Policies",
  "week_label": "Thursday Deep Dive | Data Governance Series",
  "introduction": "2-3 sentences: Data governance is no longer just a compliance checkbox — it is a competitive advantage. Teams with good data catalogs ship data products 3x faster because engineers know exactly what data exists, where it came from, and who owns it.",
  "sections": [
    {
      "heading": "What Is a Data Catalog & Why It Matters",
      "content": "3-4 sentences: A data catalog is a searchable inventory of all data assets — tables, reports, ML models, pipelines — enriched with metadata: schema, ownership, lineage, quality scores, and business glossary terms. Without a catalog, data engineers spend 30-40% of their time hunting for the right table or understanding what a column means. Tools: Databricks Unity Catalog, Microsoft Purview, Apache Atlas, Amundsen, DataHub.",
      "code": "-- Unity Catalog: enrich tables with tags and descriptions\nCOMMENT ON TABLE prod.sales.transactions IS\n    'Daily sales transactions from POS and e-commerce. Refreshed at 2 AM UTC. Owner: Data Engineering Team.';\n\nALTER TABLE prod.sales.transactions\n  SET TAGS ('domain' = 'sales', 'pii' = 'false', 'sla' = '2am-utc', 'tier' = 'gold');\n\nALTER TABLE prod.sales.customers\n  ALTER COLUMN email\n  COMMENT 'Customer email. PII — masked for non-admins. Source: CRM system.';\n\n-- Search catalog by tag\nSELECT * FROM system.information_schema.tables\nWHERE table_catalog = 'prod'\n  AND table_schema   = 'sales';",
      "code_label": "SQL — Add catalog metadata, tags, and descriptions in Unity Catalog"
    },
    {
      "heading": "Microsoft Purview — Enterprise Data Catalog",
      "content": "3-4 sentences: Microsoft Purview is Azure's enterprise data governance solution. It automatically scans Azure data sources (ADLS, Azure SQL, Synapse, Databricks) and builds a catalog with data lineage, classification, and sensitivity labels. Data engineers register their sources in Purview and Purview scans on schedule — no manual cataloging needed.",
      "code": "# Python SDK — Register Databricks as a Purview source\nfrom azure.purview.catalog import PurviewCatalogClient\nfrom azure.identity import DefaultAzureCredential\n\ncred = DefaultAzureCredential()\nclient = PurviewCatalogClient(\n    endpoint='https://mypurview.purview.azure.com',\n    credential=cred\n)\n\n# Create a Databricks source entity\ndatabricks_entity = {\n    'typeName': 'databricks_workspace',\n    'attributes': {\n        'name': 'prod-databricks',\n        'qualifiedName': 'databricks://prod.azuredatabricks.net',\n        'workspaceUrl': 'https://prod.azuredatabricks.net'\n    }\n}\nclient.entity.create_or_update({'entity': databricks_entity})",
      "code_label": "Python — Register Databricks workspace in Microsoft Purview"
    },
    {
      "heading": "Data Lineage with OpenLineage & Marquez",
      "content": "3-4 sentences: OpenLineage is the open standard for capturing data lineage events. Databricks emits OpenLineage events natively when you enable it. Marquez is the open-source lineage backend — it receives OpenLineage events and provides a UI to visualize job-to-dataset lineage. This is the foundation for impact analysis: if table X changes, which downstream jobs and reports break?",
      "code": "# Enable OpenLineage in Databricks Spark config\n# Add to cluster config or spark_conf in databricks.yml:\n# spark.openlineage.transport.type http\n# spark.openlineage.transport.url http://marquez:5000/api/v1\n# spark.openlineage.namespace my-databricks-namespace\n\n# Or emit a manual OpenLineage event from a pipeline:\nimport requests, json\n\nopenlineage_event = {\n    'eventType': 'COMPLETE',\n    'job': {'namespace': 'databricks', 'name': 'sales_etl_job'},\n    'inputs':  [{'namespace': 'adls', 'name': 'raw/orders/'}],\n    'outputs': [{'namespace': 'delta', 'name': 'prod.sales.orders_silver'}],\n    'run': {'runId': 'abc-123'}\n}\nrequests.post('http://marquez:5000/api/v1/lineage', json=openlineage_event)",
      "code_label": "Python — Emit OpenLineage event for data lineage tracking"
    },
    {
      "heading": "Data Classification, Policies & Business Glossary",
      "content": "3-4 sentences: Data classification automatically identifies sensitive data (PII, financial, health) and labels it. Unity Catalog and Purview both support classification rules. A business glossary maps technical terms to business definitions — e.g. 'active_customer' = customer with a purchase in the last 90 days. Policies then enforce how classified data can be used.",
      "code": "",
      "code_label": ""
    }
  ],
  "cheat_sheet_rows": [
    ["Tool / Concept", "What It Does", "When to Use"],
    ["Databricks Unity Catalog", "Built-in catalog + governance for Databricks", "Primary choice for Databricks-first teams"],
    ["Microsoft Purview", "Enterprise catalog for all Azure data sources", "Multi-source Azure data governance"],
    ["Apache Atlas", "Open-source catalog (used with Hadoop/Hive)", "On-prem or AWS/GCP workloads"],
    ["DataHub (LinkedIn)", "Open-source metadata platform", "Multi-cloud or vendor-neutral teams"],
    ["OpenLineage", "Open standard for data lineage events", "Capture lineage across all pipeline tools"],
    ["Marquez", "Open-source lineage backend + UI", "Visualize OpenLineage events locally/cloud"],
    ["Data Classification", "Auto-label PII/financial/health data", "Purview or Unity Catalog scanners"],
    ["Business Glossary", "Map technical terms to business definitions", "Align engineers and business on KPI meaning"],
    ["Data Tags (UC)", "Add searchable metadata to tables/columns", "Tag by domain, SLA, tier, PII status"],
    ["COMMENT ON TABLE", "Add description to a Unity Catalog table", "Document tables for self-service discovery"],
    ["Impact Analysis", "Find downstream jobs affected by a change", "Before altering a heavily-used table"]
  ],
  "key_takeaways": [
    "A data catalog is the single source of truth for what data exists, where it came from, and who owns it",
    "Unity Catalog tags and COMMENT ON TABLE turn raw tables into self-documenting data assets",
    "Microsoft Purview auto-scans Azure sources — no manual cataloging needed for ADLS, SQL, Synapse",
    "OpenLineage is the open standard for lineage — enable it in Databricks with 3 Spark config lines",
    "Business glossary aligns engineers and business teams on KPI definitions — critical for trusted data",
    "Data classification auto-identifies PII and sensitive data — required for GDPR/HIPAA compliance",
    "Impact analysis with lineage prevents breaking downstream jobs when schemas change"
  ],
  "linkedin_caption": "🗂️ Data Catalog & Governance — The Foundation Every Data Team Needs!\\n\\nWithout a catalog, engineers spend 30-40% of their time just FINDING the right table.\\n\\nThis Thursday's PDF: Unity Catalog, Microsoft Purview, OpenLineage, business glossary, and data classification — 3 pages with a full cheat sheet.\\n\\n📥 Download and share with your data governance team!\\n\\nWhat catalog does your team use?",
  "hashtags": "#DataCatalog #DataGovernance #UnityCatalog #MicrosoftPurview #OpenLineage #DataEngineering #DataLineage #DataManagement"
}""",
    },

    # ── Topic 7 ────────────────────────────────────────────────────────────────
    {
        "label": "AI Tools for Data Engineers — Full Comparison",
        "prompt": """Generate a comprehensive guide for a 3-4 page LinkedIn PDF comparing all major AI tools for data engineers in 2025.

Return ONLY valid JSON (no markdown, no backticks, no extra text outside JSON):
{
  "title": "AI Tools for Data Engineers — 2025 Complete Comparison",
  "subtitle": "Claude · GitHub Copilot · Cursor · Databricks Genie · Tabnine · Cheat Sheet",
  "week_label": "Thursday Deep Dive | AI-Powered Data Engineering Series",
  "introduction": "2-3 sentences: In 2025, data engineers who use AI coding tools ship pipelines 2-3x faster than those who don't. But not all tools are equal — the right combination matters. This guide covers every major AI tool, what it's best at, and how to use it in real-time data engineering workflows.",
  "sections": [
    {
      "heading": "Claude AI — Best for Complex Reasoning & Code Review",
      "content": "3-4 sentences: Claude (by Anthropic) excels at long-context reasoning, code review, and complex multi-step tasks. It has a 200K token context window — you can paste an entire PySpark pipeline and ask it to find bugs or optimize for performance. Best use cases: reviewing complex Spark jobs, explaining obscure errors, generating detailed documentation, refactoring legacy ETL code. Access via VS Code Continue extension, API, or Claude.ai web.",
      "code": "# Real-world Claude usage: review a PySpark pipeline\n# Paste into Claude with this prompt:\n\"\"\"\nYou are a senior data engineer. Review this PySpark job for:\n1. Performance issues (shuffles, skew, inefficient joins)\n2. Data quality problems (null handling, type mismatches)\n3. Reliability issues (no error handling, non-idempotent writes)\nHere is the code: [paste your code]\nGive specific, actionable fixes with code examples.\n\"\"\"\n\n# Claude's strengths:\n# ✅ 200K context — review entire pipeline files\n# ✅ Reasoning — explain WHY not just WHAT\n# ✅ Code review — finds subtle Spark anti-patterns\n# ✅ Documentation — generates detailed docstrings",
      "code_label": "Python — Effective Claude prompts for data engineering"
    },
    {
      "heading": "GitHub Copilot — Best for Speed & VS Code Integration",
      "content": "3-4 sentences: GitHub Copilot is the most widely adopted AI coding tool — it sits directly in VS Code and auto-completes as you type. Best for data engineers: fast boilerplate (PySpark DataFrame transforms, SQL queries, YAML configs), tab-completion in notebooks, and the @workspace command to ask about your entire codebase. Copilot Chat adds inline chat for quick questions without leaving the editor.",
      "code": "# GitHub Copilot in action — type a comment, get code\n# Comment:\n# Read parquet from ADLS, apply SCD Type 2 on customer_id\n\n# Copilot generates:\nfrom delta.tables import DeltaTable\nfrom pyspark.sql.functions import current_timestamp, lit, sha2, concat_ws\n\n# Load source\nsource_df = spark.read.parquet('abfss://raw@storage.dfs.core.windows.net/customers/')\nsource_df = source_df.withColumn('hash_key', sha2(concat_ws('|', *source_df.columns), 256))\n\n# SCD Type 2 merge\ndelta_table = DeltaTable.forPath(spark, '/mnt/silver/customers')\ndelta_table.alias('target').merge(\n    source_df.alias('source'),\n    'target.customer_id = source.customer_id AND target.is_current = true'\n).whenMatchedUpdate(set={'is_current': lit(False), 'end_date': current_timestamp()})\n .whenNotMatchedInsertAll()\n .execute()",
      "code_label": "Python — GitHub Copilot generates SCD Type 2 merge from a comment"
    },
    {
      "heading": "Cursor IDE & Other AI Tools",
      "content": "3-4 sentences: Cursor is a VS Code fork with AI built into the core — Ctrl+K to edit code with AI, Ctrl+L for chat, Ctrl+Shift+K to generate from scratch. It supports Claude, GPT-4, and Gemini as backends. Other tools: Tabnine (privacy-first, runs locally), Amazon CodeWhisperer (free for AWS, good for boto3/Glue), Codeium (free alternative to Copilot). For notebook-centric workflows: Databricks Genie (NL-to-SQL) and Notebook Assistant (inline AI suggestions in Databricks notebooks).",
      "code": "",
      "code_label": ""
    },
    {
      "heading": "The Recommended AI Stack for Data Engineers",
      "content": "3-4 sentences: The optimal 2025 AI stack: GitHub Copilot for speed (tab completion everywhere), Claude via Continue for deep reasoning and code review, Databricks Genie for self-service analytics, and ChatGPT/Gemini for quick lookups. Cost: Copilot Individual $10/mo, Claude Pro $20/mo, Genie included in Databricks. Total investment: ~$30/month saves 10-15 hours/month = very high ROI.",
      "code": "",
      "code_label": ""
    }
  ],
  "cheat_sheet_rows": [
    ["AI Tool", "Best At", "Data Engineering Use Case", "Cost"],
    ["Claude (Anthropic)", "Long context, reasoning, code review", "Review full pipelines, explain Spark errors", "$20/mo (Pro)"],
    ["GitHub Copilot", "Tab completion, VS Code integration", "Fast boilerplate: PySpark, SQL, YAML", "$10/mo"],
    ["Cursor IDE", "AI-native editor, multi-model", "Full file edits with AI, codebase chat", "$20/mo"],
    ["Databricks Genie", "NL-to-SQL for analysts", "Self-service analytics on Delta tables", "Included in DBX"],
    ["Tabnine", "Privacy-first, local model option", "Air-gapped or sensitive environments", "$12/mo"],
    ["Amazon Q (CodeWhisperer)", "AWS services, boto3, Glue", "AWS Glue scripts, Lambda, S3 operations", "Free tier"],
    ["Codeium", "Free Copilot alternative", "Tab completion without subscription cost", "Free"],
    ["ChatGPT / Gemini", "Quick lookups, general reasoning", "Architecture questions, quick SQL help", "Free / $20/mo"],
    ["Notebook Assistant (DBX)", "Inline AI in Databricks notebooks", "Suggest next cell, explain errors in notebook", "Included in DBX"],
    ["Continue Extension", "Connect any LLM to VS Code", "Use Claude/GPT in VS Code without Copilot", "Free + API cost"]
  ],
  "key_takeaways": [
    "Use GitHub Copilot for fast tab-completion everywhere — it's the baseline AI tool",
    "Add Claude via Continue extension for code review, complex reasoning, and 200K context tasks",
    "Databricks Genie handles analyst self-service — set it up once, reduce SQL request tickets by 60%",
    "Cursor IDE is the best all-in-one AI editor — consider switching from VS Code if you want AI-native",
    "The $30/month Claude + Copilot stack saves 10-15 hours/month — extremely high ROI for engineers",
    "For AWS teams: Amazon Q (CodeWhisperer) is free and excellent for boto3/Glue/S3 code generation",
    "Combine tools: Copilot for speed, Claude for intelligence, Genie for self-service analytics"
  ],
  "linkedin_caption": "🛠️ AI Tools for Data Engineers — The 2025 Complete Comparison!\\n\\nClaude vs Copilot vs Cursor vs Genie vs Tabnine — which should you use and when?\\n\\nSpoiler: the answer is not one tool. It's the right combination.\\n\\nThis Thursday's PDF breaks it all down: what each tool does best, real data engineering use cases, and the recommended $30/mo AI stack. Full cheat sheet included.\\n\\n📥 Save it!\\n\\nWhich AI tool do you use most for data engineering?",
  "hashtags": "#AITools #DataEngineering #ClaudeAI #GitHubCopilot #Cursor #Databricks #GenieAI #DeveloperProductivity"
}""",
    },

    # ── Topic 8 ────────────────────────────────────────────────────────────────
    {
        "label": "Databricks External Connections",
        "prompt": """Generate a comprehensive guide for a 3-4 page LinkedIn PDF about connecting Databricks to external services (ADLS, S3, Kafka, Event Hubs, Service Bus, etc.).

Return ONLY valid JSON (no markdown, no backticks, no extra text outside JSON):
{
  "title": "Databricks External Connections — Complete Integration Guide",
  "subtitle": "ADLS Gen2 · S3 · Kafka · Event Hubs · Service Bus · Key Vault · Snowflake",
  "week_label": "Thursday Deep Dive | Data Engineering Architecture Series",
  "introduction": "2-3 sentences: Databricks rarely works in isolation — production architectures connect it to cloud storage, message queues, databases, and SaaS tools. This guide covers the most common external connections with working code, so you stop Googling the same config snippets.",
  "sections": [
    {
      "heading": "Azure ADLS Gen2 — The Standard Databricks Storage Layer",
      "content": "3-4 sentences: ADLS Gen2 is the recommended storage backend for Databricks on Azure. Three connection methods: (1) Service Principal OAuth — recommended for production, (2) Managed Identity — best when running on Azure Databricks, (3) Access Key — simple but not recommended for prod. Always store credentials in Databricks Secret Scopes backed by Azure Key Vault.",
      "code": "# Method 1: Service Principal OAuth (recommended)\nspark.conf.set(\n    'fs.azure.account.auth.type.storageacct.dfs.core.windows.net',\n    'OAuth'\n)\nspark.conf.set(\n    'fs.azure.account.oauth.provider.type.storageacct.dfs.core.windows.net',\n    'org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider'\n)\nspark.conf.set('fs.azure.account.oauth2.client.id.storageacct.dfs.core.windows.net',\n               dbutils.secrets.get('prod-secrets', 'sp-client-id'))\nspark.conf.set('fs.azure.account.oauth2.client.secret.storageacct.dfs.core.windows.net',\n               dbutils.secrets.get('prod-secrets', 'sp-client-secret'))\nspark.conf.set('fs.azure.account.oauth2.client.endpoint.storageacct.dfs.core.windows.net',\n               'https://login.microsoftonline.com/<tenant-id>/oauth2/token')\n\n# Read Delta from ADLS\ndf = spark.read.format('delta').load(\n    'abfss://silver@storageacct.dfs.core.windows.net/sales/transactions/'\n)",
      "code_label": "Python — ADLS Gen2 connection via Service Principal OAuth"
    },
    {
      "heading": "AWS S3 & GCS — Cross-Cloud Storage",
      "content": "3-4 sentences: Databricks on AWS connects to S3 via IAM Roles (recommended) or Access Keys. On GCP, Databricks connects to GCS via Service Account. For multi-cloud architectures, Unity Catalog External Locations provide a governed, single-config way to reference storage across clouds.",
      "code": "# AWS S3 — IAM Role (configured at cluster level, no code needed)\n# Just read directly:\ndf = spark.read.parquet('s3a://my-data-lake/raw/orders/')\n\n# GCS — Service Account Key\nspark.conf.set('google.cloud.auth.service.account.enable', 'true')\nspark.conf.set('google.cloud.auth.service.account.json.keyfile',\n               '/dbfs/FileStore/sa-key.json')\ndf = spark.read.parquet('gs://my-gcs-bucket/raw/orders/')\n\n# Unity Catalog External Location (recommended for both)\n# Define once, use everywhere with governance:\nCREATE EXTERNAL LOCATION s3_raw\n  URL 's3://my-data-lake/raw/'\n  WITH (STORAGE CREDENTIAL aws_prod_cred);\nGRANT READ FILES ON EXTERNAL LOCATION s3_raw TO `data-engineers`;",
      "code_label": "Python + SQL — S3, GCS and Unity Catalog External Locations"
    },
    {
      "heading": "Streaming: Kafka, Azure Event Hubs & Service Bus",
      "content": "3-4 sentences: Databricks Structured Streaming connects to Kafka and Azure Event Hubs (which is Kafka-compatible). For high-throughput streaming: use Auto Loader for file-based streaming, Kafka connector for event streams, and Delta Live Tables for managed streaming pipelines. Azure Service Bus integration uses the azure-servicebus SDK in a Databricks job.",
      "code": "# Azure Event Hubs — Kafka-compatible connection\nEH_NAMESPACE  = dbutils.secrets.get('prod-secrets', 'eh-namespace')\nEH_NAME       = dbutils.secrets.get('prod-secrets', 'eh-name')\nEH_CONN_STR   = dbutils.secrets.get('prod-secrets', 'eh-connection-string')\n\ndf_stream = (\n    spark.readStream\n         .format('kafka')\n         .option('kafka.bootstrap.servers', f'{EH_NAMESPACE}.servicebus.windows.net:9093')\n         .option('subscribe', EH_NAME)\n         .option('kafka.security.protocol', 'SASL_SSL')\n         .option('kafka.sasl.mechanism', 'PLAIN')\n         .option('kafka.sasl.jaas.config',\n                 f'kafkashaded.org.apache.kafka.common.security.plain.PlainLoginModule required '\n                 f'username=\"$ConnectionString\" password=\"{EH_CONN_STR}\";')\n         .option('startingOffsets', 'latest')\n         .load()\n)\n\n# Write stream to Delta Lake\n(df_stream.writeStream\n          .format('delta')\n          .outputMode('append')\n          .option('checkpointLocation', '/mnt/checkpoints/events/')\n          .table('prod.streaming.events_bronze')\n          .start())",
      "code_label": "Python — Azure Event Hubs Kafka-compatible Structured Streaming"
    },
    {
      "heading": "Snowflake, Azure SQL & Other Database Connections",
      "content": "3-4 sentences: Databricks connects to Snowflake via the official Snowflake Spark connector — reads push computation to Snowflake (pushdown optimization). For Azure SQL / SQL Server: use the JDBC connector with a connection string from Key Vault. For PostgreSQL: same JDBC pattern. For all database connections, always store credentials in Databricks Secret Scopes — never hardcode connection strings.",
      "code": "# Snowflake connection from Databricks\nsnowflake_options = {\n    'sfUrl':       'myorg.snowflakecomputing.com',\n    'sfUser':      dbutils.secrets.get('prod-secrets', 'sf-user'),\n    'sfPassword':  dbutils.secrets.get('prod-secrets', 'sf-password'),\n    'sfDatabase':  'PROD_DB',\n    'sfSchema':    'SALES',\n    'sfWarehouse': 'COMPUTE_WH'\n}\ndf = (spark.read\n           .format('snowflake')\n           .options(**snowflake_options)\n           .option('dbtable', 'TRANSACTIONS')\n           .load())\n\n# Azure SQL via JDBC\njdbc_url = f'jdbc:sqlserver://myserver.database.windows.net:1433;database=SalesDB'\ndf = (spark.read.format('jdbc')\n           .option('url', jdbc_url)\n           .option('dbtable', 'dbo.orders')\n           .option('user', dbutils.secrets.get('prod-secrets', 'sql-user'))\n           .option('password', dbutils.secrets.get('prod-secrets', 'sql-password'))\n           .load())",
      "code_label": "Python — Snowflake and Azure SQL JDBC connections from Databricks"
    }
  ],
  "cheat_sheet_rows": [
    ["Service", "Connection Method", "Key Config / Secret"],
    ["ADLS Gen2 (Azure)", "Service Principal OAuth (recommended)", "client-id, client-secret, tenant-id"],
    ["ADLS Gen2 (Azure)", "Managed Identity", "No secrets needed — cluster identity"],
    ["AWS S3", "IAM Role (cluster-level)", "No code secrets — configure in cluster"],
    ["GCS (Google Cloud)", "Service Account JSON key", "JSON keyfile path in DBFS"],
    ["Azure Event Hubs", "Kafka connector (SASL_SSL)", "Connection string from Event Hubs"],
    ["Apache Kafka", "Kafka Spark connector", "bootstrap.servers, security.protocol"],
    ["Azure Service Bus", "azure-servicebus Python SDK", "Connection string from Service Bus"],
    ["Snowflake", "Snowflake Spark connector", "sfUrl, sfUser, sfPassword, sfWarehouse"],
    ["Azure SQL / SQL Server", "JDBC connector", "JDBC URL, username, password"],
    ["PostgreSQL", "JDBC connector", "jdbc:postgresql://host/db, user, pass"],
    ["Azure Key Vault", "Databricks Secret Scope (backed by KV)", "Secret scope name → dbutils.secrets.get"]
  ],
  "key_takeaways": [
    "Always store credentials in Databricks Secret Scopes backed by Azure Key Vault — never hardcode",
    "ADLS Gen2: use Service Principal OAuth for production, Managed Identity where available",
    "Azure Event Hubs is Kafka-compatible — use the Kafka connector, no separate SDK needed",
    "Use Unity Catalog External Locations to govern S3/ADLS/GCS access in one place",
    "Snowflake Spark connector supports pushdown — heavy aggregations run in Snowflake, not Spark",
    "All JDBC connections (Azure SQL, PostgreSQL, Snowflake) follow the same pattern — store creds in secrets",
    "Auto Loader is the recommended Bronze ingestion method for file-based streaming from ADLS/S3/GCS"
  ],
  "linkedin_caption": "🔌 Databricks External Connections — Every Integration You Need in One Guide!\\n\\nADLS Gen2, S3, Kafka, Event Hubs, Snowflake, Azure SQL... I keep seeing engineers Google these same configs every week.\\n\\nThis Thursday's PDF has working connection code for all major services + a cheat sheet with every config option.\\n\\n📥 Download it. Bookmark it. Send it to your team.\\n\\nWhich connection does your team set up most often?",
  "hashtags": "#Databricks #DataEngineering #Azure #AWS #Kafka #EventHubs #Snowflake #DeltaLake #DataArchitecture"
}""",
    },

    # ── Topic 9 ────────────────────────────────────────────────────────────────
    {
        "label": "MCP — Model Context Protocol for Data Engineers",
        "prompt": """Generate a comprehensive guide for a 3-4 page LinkedIn PDF about Model Context Protocol (MCP) for data engineers.

Return ONLY valid JSON (no markdown, no backticks, no extra text outside JSON):
{
  "title": "MCP — Model Context Protocol for Data Engineers",
  "subtitle": "What It Is · How It Works · Build MCP Servers · Connect AI to Your Data",
  "week_label": "Thursday Deep Dive | AI Integration Series",
  "introduction": "2-3 sentences: Model Context Protocol (MCP) is an open standard by Anthropic that lets AI assistants like Claude securely connect to external data sources and tools — databases, APIs, files, Databricks, Kafka — via lightweight MCP servers. Think of it as a USB-C port for AI: any AI connects to any data tool using one standard interface.",
  "sections": [
    {
      "heading": "What Is MCP and Why Data Engineers Need It",
      "content": "3-4 sentences: MCP defines a standard client-server protocol where an MCP Server exposes tools and resources (e.g. query a database, read a file, call an API), and an MCP Client (Claude, Copilot, Cursor) connects to those servers to give AI access to real data. Without MCP, AI assistants only know about code in the editor window. With MCP, Claude can query your Databricks tables, read your ADLS files, or trigger an ADF pipeline — all from a chat prompt.",
      "code": "# Minimal MCP server exposing a Databricks SQL tool\nfrom mcp.server import Server\nfrom mcp.server.stdio import stdio_server\nfrom mcp import types\nimport subprocess\n\napp = Server('databricks-mcp')\n\n@app.list_tools()\nasync def list_tools():\n    return [\n        types.Tool(\n            name='run_databricks_sql',\n            description='Run a SQL query on Databricks and return results',\n            inputSchema={\n                'type': 'object',\n                'properties': {'query': {'type': 'string', 'description': 'SQL query to execute'}},\n                'required': ['query']\n            }\n        )\n    ]\n\n@app.call_tool()\nasync def call_tool(name: str, arguments: dict):\n    if name == 'run_databricks_sql':\n        result = subprocess.run(\n            ['databricks', 'sql', 'execute', '--statement', arguments['query']],\n            capture_output=True, text=True\n        )\n        return [types.TextContent(type='text', text=result.stdout)]\n\nasync def main():\n    async with stdio_server() as (r, w):\n        await app.run(r, w, app.create_initialization_options())",
      "code_label": "Python — Minimal MCP server exposing Databricks SQL to Claude AI"
    },
    {
      "heading": "Setting Up MCP with Claude Desktop & VS Code",
      "content": "3-4 sentences: Claude Desktop and VS Code Continue extension both support MCP natively. You configure MCP servers in a JSON config file — Claude auto-discovers tools when it starts. For data engineers: connect Claude to your Databricks workspace, ADLS, or local database and Claude can answer questions about your actual data in real time.",
      "code": "// claude_desktop_config.json — Add MCP servers for data engineering\n{\n  \"mcpServers\": {\n    \"databricks\": {\n      \"command\": \"python\",\n      \"args\": [\"/path/to/databricks_mcp_server.py\"],\n      \"env\": {\n        \"DATABRICKS_HOST\": \"https://prod.azuredatabricks.net\",\n        \"DATABRICKS_TOKEN\": \"dapi...\"\n      }\n    },\n    \"filesystem\": {\n      \"command\": \"npx\",\n      \"args\": [\"-y\", \"@modelcontextprotocol/server-filesystem\", \"/data/pipelines\"]\n    },\n    \"postgres\": {\n      \"command\": \"npx\",\n      \"args\": [\"-y\", \"@modelcontextprotocol/server-postgres\",\n               \"postgresql://user:pass@localhost/mydb\"]\n    }\n  }\n}",
      "code_label": "JSON — Claude Desktop config connecting to Databricks, filesystem, Postgres MCP servers"
    },
    {
      "heading": "Real-World MCP Use Cases for Data Engineers",
      "content": "3-4 sentences: Once Claude connects to your MCP servers, you can ask in plain English: 'Show me tables in the sales schema', 'What was yesterday's pipeline failure?', 'Compare row counts between bronze and silver layers'. Claude calls your MCP tool, gets real data, and gives you an intelligent answer. Use cases: ad-hoc data investigation, pipeline debugging, schema exploration, data quality checks — all without leaving the chat.",
      "code": "# MCP tool: query Delta table row counts across layers\n@app.call_tool()\nasync def call_tool(name: str, arguments: dict):\n    if name == 'compare_layer_counts':\n        table = arguments['table_name']\n        spark_query = f\"\"\"\n            SELECT\n              (SELECT COUNT(*) FROM bronze.{table}) AS bronze_count,\n              (SELECT COUNT(*) FROM silver.{table}) AS silver_count,\n              (SELECT COUNT(*) FROM gold.{table})   AS gold_count\n        \"\"\"\n        # Execute via Databricks SQL API\n        result = call_databricks_sql(spark_query)\n        return [types.TextContent(type='text', text=str(result))]\n    # Claude prompt: 'Compare row counts for the orders table across all layers'\n    # Claude calls this tool and explains any discrepancies automatically",
      "code_label": "Python — MCP tool for cross-layer row count comparison, callable by Claude"
    },
    {
      "heading": "Pre-Built MCP Servers & the Ecosystem",
      "content": "3-4 sentences: The MCP ecosystem is growing rapidly — there are pre-built servers for Postgres, SQLite, filesystem, GitHub, Slack, Google Drive, AWS, and more. For Databricks: the community has built MCP servers wrapping the Databricks REST API. Check the official MCP server registry at modelcontextprotocol.io. For enterprise use, host MCP servers inside your VNet so they access internal databases securely.",
      "code": "",
      "code_label": ""
    }
  ],
  "cheat_sheet_rows": [
    ["MCP Concept", "What It Does", "Data Engineering Use Case"],
    ["MCP Server", "Exposes tools/resources via standard protocol", "Wrap Databricks SQL, ADF, ADLS as AI tools"],
    ["MCP Client", "AI that connects to MCP servers", "Claude Desktop, VS Code Continue, Cursor"],
    ["Tool", "A callable function exposed by MCP server", "run_sql(), list_tables(), get_pipeline_status()"],
    ["Resource", "A readable data source exposed by MCP", "Expose pipeline YAML files or config to AI"],
    ["stdio transport", "Local MCP server via stdin/stdout", "Development — run MCP server locally"],
    ["HTTP/SSE transport", "Remote MCP server over HTTP", "Production — deploy MCP server in VNet"],
    ["claude_desktop_config.json", "Config file to register MCP servers with Claude", "Add Databricks, Postgres, filesystem servers"],
    ["@modelcontextprotocol/server-postgres", "Pre-built PostgreSQL MCP server", "Let Claude query Postgres with plain English"],
    ["@modelcontextprotocol/server-filesystem", "Pre-built filesystem MCP server", "Claude reads pipeline code/config files"],
    ["mcp Python SDK", "Build custom MCP servers in Python", "Wrap any internal API or database as MCP tool"],
    ["modelcontextprotocol.io", "Official MCP server registry", "Find pre-built servers for your stack"]
  ],
  "key_takeaways": [
    "MCP is a standard protocol — any AI client connects to any data tool using the same interface",
    "Build an MCP server in Python with 30 lines to expose any database or API to Claude",
    "Claude Desktop uses claude_desktop_config.json to auto-discover and connect MCP servers",
    "Pre-built MCP servers exist for Postgres, SQLite, filesystem, GitHub, AWS — use them immediately",
    "With Databricks MCP, Claude can query your Delta tables, check pipeline status, and compare row counts",
    "For production: deploy MCP servers inside your VNet so AI accesses internal systems securely",
    "MCP eliminates copy-paste debugging — Claude reads real logs and real data, not examples you type"
  ],
  "linkedin_caption": "🔌 MCP (Model Context Protocol) — The Missing Link Between AI and Your Data!\\n\\nWhat if Claude could query your Databricks tables, check your ADF pipeline status, and compare Bronze vs Silver row counts — all from a chat prompt?\\n\\nThat's MCP. And it's already here.\\n\\nThis Thursday's PDF: what MCP is, how to build an MCP server in Python, Claude Desktop config, and pre-built servers for data engineers. Cheat sheet included.\\n\\n📥 Save it. This is the future of AI-assisted data engineering.\\n\\nHave you tried MCP yet?",
  "hashtags": "#MCP #ModelContextProtocol #Claude #AI #DataEngineering #Databricks #LLM #AITools #DataPipelines"
}""",
    },

    # ── Topic 10 ───────────────────────────────────────────────────────────────
    {
        "label": "LangChain for Data Engineers",
        "prompt": """Generate a comprehensive guide for a 3-4 page LinkedIn PDF about LangChain for data engineers building AI-powered data pipelines.

Return ONLY valid JSON (no markdown, no backticks, no extra text outside JSON):
{
  "title": "LangChain for Data Engineers — Build AI-Powered Data Pipelines",
  "subtitle": "Chains · Agents · RAG · SQL Agent · Tool Calling · Production Patterns",
  "week_label": "Thursday Deep Dive | AI + Data Engineering Series",
  "introduction": "2-3 sentences: LangChain is the most popular Python framework for building LLM-powered applications. For data engineers it enables AI-powered ETL — pipelines that use LLMs to classify data, extract entities, answer questions from documents, or auto-generate SQL from natural language. This guide covers the patterns data engineers actually use in production.",
  "sections": [
    {
      "heading": "LangChain Core Concepts — Chains, Agents & Tools",
      "content": "3-4 sentences: LangChain has three core building blocks: Chains (sequential LLM + tool calls), Agents (LLM decides which tool to call dynamically), and Tools (functions the LLM can invoke — SQL executor, API call, file reader). For data pipelines: use Chains for deterministic ETL steps, Agents for dynamic data investigation tasks. LangChain wraps any LLM — OpenAI, Claude, Gemini, local models.",
      "code": "from langchain_anthropic import ChatAnthropic\nfrom langchain_core.prompts import ChatPromptTemplate\nfrom langchain_core.output_parsers import StrOutputParser\n\n# Simple chain: classify incoming data records by category\nllm = ChatAnthropic(model='claude-3-5-sonnet-20241022')\n\nprompt = ChatPromptTemplate.from_template(\n    'Classify this customer support ticket into one of: BILLING, TECHNICAL, RETURNS, OTHER.\\n'\n    'Return ONLY the category word.\\n\\nTicket: {ticket_text}'\n)\n\n# Chain = prompt | llm | output parser\nclassify_chain = prompt | llm | StrOutputParser()\n\n# Use in a Spark UDF for batch classification\nresult = classify_chain.invoke({'ticket_text': 'My invoice shows a double charge'})\nprint(result)  # BILLING",
      "code_label": "Python — LangChain chain for batch data classification"
    },
    {
      "heading": "SQL Agent — Let LLM Query Your Database",
      "content": "3-4 sentences: LangChain's SQL Agent connects an LLM to any SQL database via SQLAlchemy. The agent reads the schema, translates natural language to SQL, executes it, and returns a human-readable answer. This is the fastest way to build an internal 'talk to your data' tool on top of Databricks, Postgres, or Snowflake.",
      "code": "from langchain_community.agent_toolkits import create_sql_agent\nfrom langchain_community.utilities import SQLDatabase\nfrom langchain_openai import ChatOpenAI\n\n# Connect to Databricks via JDBC (or any SQLAlchemy-compatible DB)\ndb = SQLDatabase.from_uri(\n    'databricks+connector://token:dapi...@prod.azuredatabricks.net:443/default',\n    include_tables=['sales_transactions', 'customers', 'products']\n)\n\nllm = ChatOpenAI(model='gpt-4o', temperature=0)\nagent = create_sql_agent(llm=llm, db=db, verbose=True)\n\n# Plain English query → SQL → result → human answer\nresponse = agent.invoke(\n    'What were the top 5 products by revenue last month, and how does that compare to the month before?'\n)\nprint(response['output'])",
      "code_label": "Python — LangChain SQL Agent on Databricks — plain English to SQL"
    },
    {
      "heading": "RAG Pipeline — AI Answers from Your Documents",
      "content": "3-4 sentences: Retrieval Augmented Generation (RAG) lets an LLM answer questions using your internal documents — runbooks, data dictionaries, pipeline documentation. LangChain makes RAG a 20-line pipeline: load docs, split into chunks, embed with a vector model, store in a vector DB (Chroma, Pinecone, Azure AI Search), then retrieve relevant chunks at query time. Data engineers use RAG to build internal knowledge bots over data documentation.",
      "code": "from langchain_community.document_loaders import DirectoryLoader\nfrom langchain.text_splitter import RecursiveCharacterTextSplitter\nfrom langchain_openai import OpenAIEmbeddings, ChatOpenAI\nfrom langchain_community.vectorstores import Chroma\nfrom langchain.chains import RetrievalQA\n\n# Load all pipeline documentation markdown files\nloader = DirectoryLoader('/docs/pipelines/', glob='**/*.md')\ndocs   = loader.load()\n\n# Split into chunks\nsplitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)\nchunks   = splitter.split_documents(docs)\n\n# Embed and store in vector DB\nvectorstore = Chroma.from_documents(chunks, OpenAIEmbeddings())\n\n# Build RAG chain\nqa_chain = RetrievalQA.from_chain_type(\n    llm=ChatOpenAI(model='gpt-4o'),\n    retriever=vectorstore.as_retriever(search_kwargs={'k': 4})\n)\n\nanswer = qa_chain.invoke('What is the SLA for the sales pipeline and who is the owner?')\nprint(answer['result'])",
      "code_label": "Python — Full RAG pipeline over pipeline documentation in 20 lines"
    },
    {
      "heading": "LLM in PySpark ETL — Batch AI at Scale",
      "content": "3-4 sentences: For batch AI processing at scale, use LangChain inside a Spark pandas_udf — this vectorizes LLM calls across millions of rows using Spark parallelism. Best for: entity extraction from text columns, sentiment classification, address normalization, product description enrichment. Rate-limit awareness: add a retry decorator and batch API calls where the provider supports it.",
      "code": "",
      "code_label": ""
    }
  ],
  "cheat_sheet_rows": [
    ["LangChain Concept", "What It Does", "Data Engineering Use Case"],
    ["Chain (LCEL)", "Sequential steps: prompt | llm | parser", "Classify records, extract fields from text"],
    ["Agent", "LLM dynamically picks which tool to call", "Ad-hoc data investigation, multi-step queries"],
    ["Tool", "A Python function the LLM can invoke", "run_sql(), fetch_api(), read_file()"],
    ["SQLDatabase", "SQLAlchemy wrapper for LangChain SQL Agent", "Connect to Databricks, Postgres, Snowflake"],
    ["create_sql_agent", "SQL Agent factory — NL to SQL to answer", "Internal 'talk to your data' tool"],
    ["DocumentLoader", "Loads docs (PDF, MD, CSV) into LangChain", "Load pipeline docs, runbooks, data dicts"],
    ["RecursiveCharacterTextSplitter", "Splits docs into overlapping chunks", "Prepare docs for RAG vector embedding"],
    ["Chroma / Pinecone / AI Search", "Vector database for RAG retrieval", "Store embedded doc chunks for search"],
    ["RetrievalQA", "RAG chain: retrieve chunks + LLM answer", "Answer questions from internal docs"],
    ["pandas_udf + LangChain", "Batch LLM calls across Spark partitions", "Classify/enrich millions of rows with AI"],
    ["ChatAnthropic / ChatOpenAI", "LLM providers for LangChain", "Swap models without changing chain code"]
  ],
  "key_takeaways": [
    "LangChain LCEL chains (prompt | llm | parser) are the simplest pattern for batch data classification",
    "SQL Agent translates plain English to SQL — build an internal 'talk to your data' tool in 15 lines",
    "RAG pipeline: load docs → chunk → embed → vector store → retrieve → answer — 20 lines with LangChain",
    "Use pandas_udf to run LangChain LLM calls across millions of Spark rows in parallel",
    "LangChain is model-agnostic — swap Claude, GPT-4, Gemini without changing pipeline code",
    "Rate limiting and retries are critical for production LLM ETL — always wrap API calls with retry logic",
    "For Databricks: connect LangChain SQL Agent via JDBC to query Delta tables in plain English"
  ],
  "linkedin_caption": "🦜 LangChain for Data Engineers — Build AI-Powered ETL Pipelines!\\n\\nWhat if your ETL pipeline could classify millions of support tickets, extract entities from PDFs, and answer questions about your data — all automatically?\\n\\nLangChain makes this a 20-line Python script.\\n\\nThis Thursday's PDF: Chains, SQL Agent, RAG pipeline, batch AI in PySpark — with real code. Cheat sheet included.\\n\\n📥 Download it and build your first AI pipeline this weekend!\\n\\nAre you using LangChain in your data stack?",
  "hashtags": "#LangChain #LLM #AI #DataEngineering #RAG #PySpark #Databricks #Python #GenerativeAI #ETL"
}""",
    },

    # ── Topic 11 ───────────────────────────────────────────────────────────────
    {
        "label": "Azure Data Factory — Advanced Patterns",
        "prompt": """Generate a comprehensive guide for a 3-4 page LinkedIn PDF about advanced Azure Data Factory (ADF) patterns for data engineers.

Return ONLY valid JSON (no markdown, no backticks, no extra text outside JSON):
{
  "title": "Azure Data Factory — Advanced Patterns Every Data Engineer Must Know",
  "subtitle": "Dynamic Pipelines · Parameterisation · Error Handling · CI/CD · Cost Tips",
  "week_label": "Thursday Deep Dive | Azure Data Engineering Series",
  "introduction": "2-3 sentences: Azure Data Factory is still the backbone of most Azure data pipelines — but most teams use only 20% of its capabilities. This guide covers the advanced patterns that separate junior ADF developers from senior ones: dynamic pipelines, metadata-driven ingestion, proper error handling, and CI/CD with Git.",
  "sections": [
    {
      "heading": "Metadata-Driven Dynamic Pipelines",
      "content": "3-4 sentences: Instead of building a separate pipeline for every source table, metadata-driven ADF uses a control table in SQL to drive all ingestion dynamically. One master pipeline reads the control table, iterates with ForEach, and processes every source/target combination. Adding a new table to ingestion = insert one row in the control table — no pipeline changes needed.",
      "code": "-- Control table: drives all ADF ingestion dynamically\nCREATE TABLE dbo.pipeline_control (\n    id              INT IDENTITY PRIMARY KEY,\n    source_system   NVARCHAR(50),   -- 'sql_server', 'api', 'csv'\n    source_object   NVARCHAR(200),  -- table name or endpoint\n    target_container NVARCHAR(100), -- ADLS container\n    target_path     NVARCHAR(200),  -- ADLS folder path\n    watermark_column NVARCHAR(100), -- 'updated_at' for incremental\n    last_watermark  DATETIME2,      -- last successful load timestamp\n    is_active       BIT DEFAULT 1,  -- enable/disable without deleting\n    load_type       NVARCHAR(10)    -- 'full' or 'incremental'\n);\n\n-- ADF pipeline reads this table in a Lookup activity\n-- then passes each row to a ForEach → Copy activity",
      "code_label": "SQL — Control table for metadata-driven ADF pipeline"
    },
    {
      "heading": "Incremental Load with Watermark Pattern",
      "content": "3-4 sentences: ADF's watermark pattern loads only changed records since the last run. A Lookup activity reads the last watermark, the Copy activity filters source data with WHERE updated_at > @last_watermark, and a Stored Procedure activity updates the watermark on success. This is more reliable than CDC for sources that don't support change tracking.",
      "code": "// ADF Copy Activity — dynamic source query with watermark\n// Source query expression (in Copy Activity → Source → Query):\n@concat(\n  'SELECT * FROM ', pipeline().parameters.source_table,\n  ' WHERE updated_at > ''', \n  string(activity('LookupWatermark').output.firstRow.last_watermark),\n  ''' AND updated_at <= ''',\n  string(utcNow()),\n  ''''\n)\n\n// After successful copy — update watermark stored procedure:\n// In Stored Procedure activity:\n{\n  \"storedProcedureName\": \"dbo.sp_update_watermark\",\n  \"storedProcedureParameters\": {\n    \"table_name\":    { \"value\": \"@pipeline().parameters.source_table\", \"type\": \"String\" },\n    \"new_watermark\": { \"value\": \"@utcNow()\", \"type\": \"DateTime\" }\n  }\n}",
      "code_label": "ADF Expression + JSON — Incremental watermark pattern"
    },
    {
      "heading": "Error Handling, Retries & Alerting",
      "content": "3-4 sentences: Most ADF pipelines fail silently — no one knows a pipeline broke until a business user complains about stale data. Fix this with: (1) If Condition activity to check Copy activity success/failure, (2) Web activity on failure path to send Teams/Slack webhook alert, (3) set retry counts and retry intervals on Copy activities, (4) Azure Monitor alerts on pipeline failure metrics.",
      "code": "// ADF Web Activity — send Teams alert on pipeline failure\n// URL: your Teams incoming webhook URL\n// Body (Dynamic Expression):\n@json(concat('{\n  \"type\": \"message\",\n  \"attachments\": [{\n    \"contentType\": \"application/vnd.microsoft.card.adaptive\",\n    \"content\": {\n      \"type\": \"AdaptiveCard\",\n      \"body\": [{\n        \"type\": \"TextBlock\",\n        \"text\": \"ADF Pipeline FAILED: ',\n        pipeline().Pipeline,\n        '  |  Run ID: ',\n        pipeline().RunId,\n        '  |  Time: ',\n        utcNow(),\n        '\"\n      }]\n    }\n  }]\n}'))",
      "code_label": "ADF Expression — Teams webhook alert on pipeline failure"
    },
    {
      "heading": "ADF CI/CD with Git & Azure DevOps",
      "content": "3-4 sentences: Connect ADF to a GitHub or Azure DevOps repository — ADF stores all pipeline JSON definitions in the repo. Use separate ADF instances for dev/test/prod. Deploy using the ADF ARM export + Azure DevOps release pipeline or GitHub Actions. Never publish directly to production — all changes go through PR review and automated deployment.",
      "code": "",
      "code_label": ""
    }
  ],
  "cheat_sheet_rows": [
    ["ADF Pattern / Activity", "What It Does", "When to Use"],
    ["Lookup Activity", "Read a single row/value from DB", "Read watermark, config, control table"],
    ["ForEach Activity", "Iterate over an array in parallel or serial", "Process list of tables from control table"],
    ["Copy Activity", "Move data between source and sink", "Core ingestion — SQL, REST, files → ADLS"],
    ["If Condition", "Branch on success/failure of upstream activity", "Route to alert path on failure"],
    ["Web Activity", "Call any HTTP endpoint", "Send Teams/Slack alert, trigger Logic App"],
    ["Set Variable", "Store intermediate value in pipeline", "Store current watermark, record counts"],
    ["Stored Procedure", "Run SQL stored procedure", "Update watermark, log pipeline metadata"],
    ["Tumbling Window Trigger", "Fixed-size time windows with dependencies", "Hourly incremental loads with gap detection"],
    ["Parameterised Linked Service", "One linked service for all environments", "Dev/test/prod SQL servers with one config"],
    ["Integration Runtime (Azure)", "Managed compute for cloud-to-cloud moves", "Copy between Azure services"],
    ["Self-Hosted IR", "On-prem or private network data movement", "Access SQL Server behind corporate firewall"]
  ],
  "key_takeaways": [
    "Metadata-driven pipelines: one master pipeline + control table replaces dozens of individual pipelines",
    "Watermark pattern: always track last successful load timestamp to enable reliable incremental loads",
    "Use Web Activity on the failure path of If Condition to send Teams/Slack alerts automatically",
    "Set retry count (3) and retry interval (30s) on every Copy Activity — transient failures are common",
    "Connect ADF to GitHub/DevOps — never deploy pipeline changes without PR review and CI/CD",
    "Parameterised Linked Services: one linked service config works across dev/test/prod with parameters",
    "Use Tumbling Window Trigger for hourly incremental loads — it handles backfill and gap detection"
  ],
  "linkedin_caption": "🏭 Azure Data Factory — The Advanced Patterns Most Engineers Skip!\\n\\nIf you're building a separate ADF pipeline for every source table, this PDF will save you weeks of work.\\n\\nThis Thursday: metadata-driven ingestion, watermark incremental loads, Teams alerts on failure, and CI/CD with Git. Real code and expressions included.\\n\\n📥 Download it and refactor your ADF pipelines this sprint!\\n\\nWhat's your biggest ADF pain point?",
  "hashtags": "#AzureDataFactory #ADF #DataEngineering #Azure #ETL #DataPipelines #DevOps #DataOps #CloudData"
}""",
    },

    # ── Topic 12 ───────────────────────────────────────────────────────────────
    {
        "label": "LLMs in Production — Data Engineering Perspective",
        "prompt": """Generate a comprehensive guide for a 3-4 page LinkedIn PDF about deploying and working with LLMs in production from a data engineer's perspective.

Return ONLY valid JSON (no markdown, no backticks, no extra text outside JSON):
{
  "title": "LLMs in Production — A Data Engineer's Complete Guide",
  "subtitle": "Prompt Engineering · Cost Control · Evaluation · MLflow · Monitoring",
  "week_label": "Thursday Deep Dive | AI in Production Series",
  "introduction": "2-3 sentences: Deploying LLMs to production is fundamentally a data engineering problem — managing prompts as versioned artifacts, tracking costs per pipeline run, evaluating output quality at scale, and monitoring for prompt drift. This guide covers what data engineers need to know to run LLMs reliably and economically in production pipelines.",
  "sections": [
    {
      "heading": "Prompt Engineering for Data Pipelines",
      "content": "3-4 sentences: A production prompt is a versioned artifact — not a string you typed into ChatGPT. Store prompts in a prompt registry (MLflow, LangSmith, or a simple Delta table), version them like code, and A/B test changes before rolling out. The prompt structure for reliable data extraction: system role → task description → output format → constraints → few-shot examples.",
      "code": "# Structured prompt template for production data extraction\nPROMPT_TEMPLATE = \"\"\"\nSystem: You are a data extraction assistant. Extract structured data ONLY.\nNever invent values. If a field is missing, return null.\n\nTask: Extract the following fields from the invoice text:\n- invoice_number (string)\n- total_amount (float)\n- currency (3-letter ISO code)\n- invoice_date (YYYY-MM-DD)\n\nOutput: Return ONLY a JSON object. No explanation, no markdown.\n\nInvoice text:\n{invoice_text}\n\nExamples:\nInput: 'INV-2024-001, Total: $1,250.00, Date: Jan 15 2024'\nOutput: {{\"invoice_number\": \"INV-2024-001\", \"total_amount\": 1250.0, \"currency\": \"USD\", \"invoice_date\": \"2024-01-15\"}}\n\"\"\"\n\nimport json, anthropic\n\nclient = anthropic.Anthropic()\n\ndef extract_invoice(text: str) -> dict:\n    msg = client.messages.create(\n        model='claude-3-5-haiku-20241022',\n        max_tokens=256,\n        messages=[{'role': 'user', 'content': PROMPT_TEMPLATE.format(invoice_text=text)}]\n    )\n    return json.loads(msg.content[0].text)",
      "code_label": "Python — Production prompt template for structured data extraction"
    },
    {
      "heading": "Cost Control — Tokens, Models & Batching",
      "content": "3-4 sentences: LLM costs in production pipelines can spiral fast — 1M rows × 500 tokens each = 500M tokens/day. Cost control levers: (1) use smaller/cheaper models for simpler tasks (Haiku vs Sonnet vs Opus), (2) use Batch API (50% cheaper) for non-real-time jobs, (3) cache identical prompts with a SHA256 hash lookup in Redis/Delta before calling the API, (4) truncate input to minimum necessary tokens.",
      "code": "import hashlib, json\nfrom pyspark.sql.functions import pandas_udf\nfrom pyspark.sql.types import StringType\nimport pandas as pd\nimport anthropic\n\n# Simple prompt cache using Delta Lake to avoid duplicate API calls\ndef get_cache_key(prompt: str) -> str:\n    return hashlib.sha256(prompt.encode()).hexdigest()\n\n# Check cache first, call API only on miss\ndef classify_with_cache(text: str, spark) -> str:\n    cache_key = get_cache_key(text)\n    cached = spark.sql(\n        f\"SELECT result FROM llm_cache WHERE cache_key = '{cache_key}'\"\n    ).collect()\n    if cached:\n        return cached[0]['result']  # Cache hit — free!\n    # Cache miss — call API (cost incurred)\n    client = anthropic.Anthropic()\n    resp = client.messages.create(\n        model='claude-3-5-haiku-20241022',  # Cheapest model for classification\n        max_tokens=10,\n        messages=[{'role': 'user', 'content': f'Classify: {text[:500]}. Return: POSITIVE/NEGATIVE/NEUTRAL'}]\n    )\n    result = resp.content[0].text.strip()\n    # Write to cache\n    spark.sql(f\"INSERT INTO llm_cache VALUES ('{cache_key}', '{result}', now())\")\n    return result",
      "code_label": "Python — LLM response caching with Delta Lake to cut API costs"
    },
    {
      "heading": "LLM Output Evaluation & Quality Monitoring",
      "content": "3-4 sentences: LLM output quality degrades silently — prompt drift, model updates, or edge cases can corrupt your data pipeline without any error being thrown. Evaluation strategies: (1) schema validation — assert the JSON output matches expected types, (2) LLM-as-judge — use a second LLM call to score output quality, (3) golden dataset comparison — compare 100 sample outputs vs human-labelled ground truth, (4) track quality metrics in MLflow over time.",
      "code": "import mlflow, json\nfrom jsonschema import validate, ValidationError\n\n# Schema validation: catch malformed LLM output before it reaches your Delta table\nINVOICE_SCHEMA = {\n    'type': 'object',\n    'required': ['invoice_number', 'total_amount', 'currency', 'invoice_date'],\n    'properties': {\n        'invoice_number': {'type': 'string'},\n        'total_amount':   {'type': 'number', 'minimum': 0},\n        'currency':       {'type': 'string', 'pattern': '^[A-Z]{3}$'},\n        'invoice_date':   {'type': 'string', 'pattern': '^\\\\d{4}-\\\\d{2}-\\\\d{2}$'}\n    }\n}\n\ndef validated_extract(text: str) -> dict | None:\n    result = extract_invoice(text)\n    try:\n        validate(instance=result, schema=INVOICE_SCHEMA)\n        mlflow.log_metric('extraction_success', 1)\n        return result\n    except ValidationError as e:\n        mlflow.log_metric('extraction_failure', 1)\n        mlflow.log_text(str(e), 'extraction_errors.txt')\n        return None  # Route to dead-letter Delta table",
      "code_label": "Python — JSON schema validation + MLflow tracking for LLM pipeline quality"
    },
    {
      "heading": "Model Selection Guide for Data Engineering Tasks",
      "content": "3-4 sentences: Choosing the right model for each task is the biggest cost/quality lever. Classification and sentiment → use cheapest fast model (Haiku, Gemini Flash). Structured extraction from messy text → mid-tier (Sonnet, GPT-4o-mini). Complex reasoning, code generation, multi-step analysis → use powerful model (Claude Sonnet/Opus, GPT-4o). Never use a powerful model for a task a cheap model can do — it's like using a GPU to run a spreadsheet.",
      "code": "",
      "code_label": ""
    }
  ],
  "cheat_sheet_rows": [
    ["LLM Production Pattern", "What It Does", "Cost / Quality Impact"],
    ["Prompt versioning (MLflow)", "Store and version prompts as artifacts", "Enables rollback and A/B testing"],
    ["Prompt caching (Delta/Redis)", "Skip API call for duplicate inputs", "Saves 40-70% API cost on repeated data"],
    ["Batch API (Anthropic/OpenAI)", "Async bulk processing at 50% discount", "Ideal for nightly batch classification jobs"],
    ["Input truncation", "Limit input to max necessary tokens", "Cuts cost proportionally to truncation %"],
    ["claude-3-5-haiku / gemini-flash", "Cheapest fast models for simple tasks", "Classification, sentiment, yes/no decisions"],
    ["claude-sonnet / gpt-4o-mini", "Mid-tier: good balance cost vs quality", "Structured extraction, summarization"],
    ["JSON schema validation", "Assert LLM output matches expected schema", "Catches 95% of malformed LLM responses"],
    ["LLM-as-judge", "Second LLM scores quality of first LLM", "Quality monitoring without human labelling"],
    ["Golden dataset", "100 human-labelled examples for comparison", "Catch quality regression after model updates"],
    ["MLflow LLM tracking", "Log prompts, outputs, metrics per run", "Track quality trends, detect drift"],
    ["Dead-letter Delta table", "Route failed extractions for human review", "Prevent corrupt data reaching Gold layer"]
  ],
  "key_takeaways": [
    "Treat prompts as versioned code artifacts — store in MLflow or Delta, never hardcode in scripts",
    "Cache LLM responses by prompt hash — saves 40-70% API cost on pipelines with repeated patterns",
    "Use the cheapest model that meets quality bar — Haiku for classification, Sonnet for extraction",
    "Always validate LLM JSON output against a schema before writing to Delta — silent failures kill data quality",
    "Use Batch API for nightly batch LLM jobs — 50% cheaper than synchronous API calls",
    "Track extraction success/failure rates in MLflow — catch quality regression before business users do",
    "Route LLM validation failures to a dead-letter Delta table for human review, not to /dev/null"
  ],
  "linkedin_caption": "🤖 LLMs in Production — What Data Engineers Actually Need to Know!\\n\\nRunning an LLM in a Jupyter notebook is easy. Running it reliably on 1M rows/day, within budget, with quality monitoring? That's a different skill entirely.\\n\\nThis Thursday's PDF: prompt versioning, cost control (caching, batch API, model selection), schema validation, MLflow tracking — all with real code.\\n\\n📥 Download it. This is the gap between AI experiments and AI in production.\\n\\nAre your LLM pipelines in production yet?",
  "hashtags": "#LLM #AI #DataEngineering #MLflow #Claude #ChatGPT #PromptEngineering #GenerativeAI #MLOps #Python"
}""",
    },

    # ── Topic 13 ───────────────────────────────────────────────────────────────
    {
        "label": "Mini Project — End-to-End Sales Analytics Pipeline",
        "prompt": """Generate a comprehensive guide for a 3-4 page LinkedIn PDF walking through a complete mini project: building an end-to-end sales analytics pipeline using Databricks, Delta Lake, and Power BI.

Return ONLY valid JSON (no markdown, no backticks, no extra text outside JSON):
{
  "title": "Mini Project: End-to-End Sales Analytics Pipeline",
  "subtitle": "Databricks · Delta Lake · Auto Loader · DLT · Power BI · GitHub Actions CI/CD",
  "week_label": "Thursday Deep Dive | Mini Project Series",
  "introduction": "2-3 sentences: This mini project walks through building a production-grade sales analytics pipeline from scratch in one day — raw CSV files from a CRM land in ADLS, Auto Loader ingests them to Bronze Delta, DLT transforms through Silver and Gold layers, and Power BI connects to the Gold layer for live dashboards. Every layer uses real, runnable code.",
  "sections": [
    {
      "heading": "Architecture Overview & Tech Stack",
      "content": "3-4 sentences: Stack: Azure Data Lake Storage Gen2 (landing zone), Databricks Auto Loader (Bronze ingestion), Delta Live Tables (Silver/Gold), Unity Catalog (governance), Power BI DirectQuery (consumption). Data flow: CRM exports CSV → ADLS landing/ → Auto Loader → Bronze Delta table → DLT Silver (clean + validate) → DLT Gold (aggregates) → Power BI Dashboard. CI/CD: Databricks Asset Bundles + GitHub Actions deploys the DLT pipeline on every merge to main.",
      "code": "# Project folder structure\n# sales-pipeline/\n# ├── databricks.yml          # Asset Bundle config\n# ├── notebooks/\n# │   ├── 01_bronze_autoloader.py\n# │   ├── 02_silver_dlt.py\n# │   └── 03_gold_dlt.py\n# ├── pipelines/\n# │   └── sales_dlt_pipeline.yml\n# ├── tests/\n# │   └── test_transformations.py\n# └── .github/workflows/\n#     └── deploy.yml\n\n# databricks.yml — Asset Bundle config\nbundle:\n  name: sales-analytics-pipeline\ntargets:\n  dev:  { workspace: { host: https://dev.azuredatabricks.net } }\n  prod: { workspace: { host: https://prod.azuredatabricks.net } }\nresources:\n  pipelines:\n    sales_dlt:\n      name: sales-analytics-dlt-${bundle.target}\n      target: prod_catalog.sales\n      configuration:\n        source_path: abfss://landing@storageacct.dfs.core.windows.net/crm/",
      "code_label": "YAML — Project structure and Databricks Asset Bundle config"
    },
    {
      "heading": "Bronze Layer — Auto Loader Ingestion",
      "content": "3-4 sentences: Auto Loader monitors the ADLS landing zone for new CSV files and incrementally ingests them — no manual file tracking needed. It infers schema on first load and handles schema evolution automatically. Every ingested file gets a metadata column (_source_file, _ingested_at) for lineage tracking.",
      "code": "# notebooks/01_bronze_autoloader.py\nimport dlt\nfrom pyspark.sql.functions import current_timestamp, input_file_name\n\n@dlt.table(\n    name='sales_transactions_bronze',\n    comment='Raw sales data from CRM CSV exports — Auto Loader ingested',\n    table_properties={'quality': 'bronze', 'pipelines.autoOptimize.managed': 'true'}\n)\ndef sales_bronze():\n    return (\n        spark.readStream\n             .format('cloudFiles')\n             .option('cloudFiles.format', 'csv')\n             .option('cloudFiles.schemaLocation', '/mnt/schema/sales_bronze')\n             .option('header', 'true')\n             .option('cloudFiles.inferColumnTypes', 'true')\n             .load('abfss://landing@storageacct.dfs.core.windows.net/crm/')\n             .withColumn('_source_file', input_file_name())\n             .withColumn('_ingested_at', current_timestamp())\n    )",
      "code_label": "Python — DLT Bronze Auto Loader for CRM CSV files"
    },
    {
      "heading": "Silver & Gold Layers — DLT Transformations",
      "content": "3-4 sentences: Silver applies data quality expectations (drop nulls, validate amounts) and standardises data types. Gold builds business aggregates — daily revenue by region, top products by revenue, customer lifetime value — which Power BI queries via DirectQuery with no data movement.",
      "code": "# notebooks/02_silver_dlt.py + 03_gold_dlt.py\nimport dlt\nfrom pyspark.sql.functions import col, to_date, round\n\n@dlt.table(comment='Cleaned and validated sales transactions')\n@dlt.expect_or_drop('positive_amount',  'order_amount > 0')\n@dlt.expect_or_drop('valid_customer',   'customer_id IS NOT NULL')\n@dlt.expect('valid_date',               'order_date IS NOT NULL')\ndef sales_silver():\n    return (\n        dlt.read_stream('sales_transactions_bronze')\n           .select(\n               col('order_id'),\n               col('customer_id'),\n               col('product_id'),\n               col('region'),\n               col('order_amount').cast('double').alias('order_amount'),\n               to_date('order_date', 'yyyy-MM-dd').alias('order_date')\n           )\n    )\n\n@dlt.table(comment='Daily revenue by region — Power BI Gold layer')\ndef revenue_by_region_gold():\n    return (\n        dlt.read('sales_silver')\n           .groupBy('order_date', 'region')\n           .agg(round(spark_sum('order_amount'), 2).alias('daily_revenue'),\n                count('order_id').alias('order_count'))\n    )",
      "code_label": "Python — DLT Silver quality expectations + Gold aggregations"
    },
    {
      "heading": "Power BI DirectQuery & CI/CD Deployment",
      "content": "3-4 sentences: Power BI connects to the Gold Delta tables via Databricks SQL Warehouse using DirectQuery — every report refresh queries live Delta data, no data duplication. CI/CD: GitHub Actions runs pytest unit tests on PR, then deploys the DLT pipeline to dev on merge to main, and to prod on release tag using databricks bundle deploy.",
      "code": "",
      "code_label": ""
    }
  ],
  "cheat_sheet_rows": [
    ["Layer / Component", "Technology", "Key Command / Pattern"],
    ["Landing Zone", "ADLS Gen2 landing/ container", "CRM drops CSV files here automatically"],
    ["Bronze Ingestion", "DLT + Auto Loader (cloudFiles)", "@dlt.table + spark.readStream cloudFiles"],
    ["Schema Evolution", "Auto Loader schemaLocation", "Schema tracked in /mnt/schema/ checkpoint"],
    ["Silver Validation", "DLT Expectations", "@dlt.expect_or_drop for nulls and ranges"],
    ["Gold Aggregates", "DLT batch table from Silver", "dlt.read() + groupBy + agg for BI metrics"],
    ["Governance", "Unity Catalog target schema", "All tables land in prod_catalog.sales schema"],
    ["Consumption", "Power BI DirectQuery", "Connect via Databricks SQL Warehouse JDBC"],
    ["Unit Tests", "pytest + PySpark local mode", "Test transformations without a cluster"],
    ["CI/CD", "GitHub Actions + DABs", "databricks bundle deploy --target prod"],
    ["Deployment Gate", "GitHub Environment (prod)", "Requires reviewer approval before prod deploy"],
    ["Monitoring", "DLT event log + Expectations UI", "Track data quality metrics per pipeline run"]
  ],
  "key_takeaways": [
    "This full project (Auto Loader → DLT Bronze/Silver/Gold → Power BI) can be built in one day",
    "Auto Loader handles schema evolution automatically — no manual schema changes when source adds columns",
    "DLT Expectations in Silver catch bad data before it pollutes Gold and Power BI reports",
    "Power BI DirectQuery on Gold Delta tables means always-fresh reports with zero data duplication",
    "GitHub Actions + DABs gives you a full CI/CD pipeline — PR tests, dev deploy, prod approval gate",
    "Unity Catalog governs all tables — analysts only see data they are authorised to query",
    "The entire pipeline config lives in databricks.yml + GitHub — fully reproducible, no manual steps"
  ],
  "linkedin_caption": "🏗️ Mini Project: Build a Production Sales Analytics Pipeline in One Day!\\n\\nCRM CSVs → ADLS → Auto Loader → DLT Bronze/Silver/Gold → Power BI DirectQuery → GitHub Actions CI/CD.\\n\\nThis is a real architecture used in enterprise data teams — and this Thursday's PDF walks through every layer with working code.\\n\\n📥 Download it. Build it over the weekend. Add it to your portfolio.\\n\\nWhat data engineering mini project would you like me to cover next?",
  "hashtags": "#DataEngineering #Databricks #DeltaLake #DLT #PowerBI #AutoLoader #ADLS #Azure #MiniProject #Portfolio"
}""",
    },

    # ── Topic 14 ───────────────────────────────────────────────────────────────
    {
        "label": "Mini Project — Real-Time Streaming with Kafka & Databricks",
        "prompt": """Generate a comprehensive guide for a 3-4 page LinkedIn PDF for a mini project: building a real-time streaming pipeline using Kafka, Databricks Structured Streaming, and Delta Lake.

Return ONLY valid JSON (no markdown, no backticks, no extra text outside JSON):
{
  "title": "Mini Project: Real-Time Streaming Pipeline with Kafka & Databricks",
  "subtitle": "Kafka · Structured Streaming · Delta Lake · DLT · Grafana · End-to-End Code",
  "week_label": "Thursday Deep Dive | Mini Project Series",
  "introduction": "2-3 sentences: This mini project builds a real-time clickstream analytics pipeline — user events published to Kafka, consumed by Databricks Structured Streaming, written to Delta Lake, and visualised in Grafana. Every component uses production-grade patterns including schema validation, checkpointing, and exactly-once delivery semantics.",
  "sections": [
    {
      "heading": "Architecture & Data Flow",
      "content": "3-4 sentences: Event flow: Web app → Kafka topic (user_events) → Databricks Structured Streaming consumer → Bronze Delta table (raw events) → DLT Silver (parsed + validated) → DLT Gold (1-minute aggregates: active users, page views, conversion rate) → Grafana dashboard via Databricks SQL. Exactly-once: Delta Lake + Structured Streaming checkpointing guarantees no duplicate or lost events.",
      "code": "# Kafka producer — simulate user clickstream events\nfrom kafka import KafkaProducer\nimport json, time, random, uuid\nfrom datetime import datetime\n\nproducer = KafkaProducer(\n    bootstrap_servers=['kafka-broker:9092'],\n    value_serializer=lambda v: json.dumps(v).encode('utf-8'),\n    acks='all',         # wait for all replicas\n    retries=5\n)\n\ndef generate_event():\n    return {\n        'event_id':   str(uuid.uuid4()),\n        'user_id':    f'user_{random.randint(1, 10000)}',\n        'event_type': random.choice(['page_view', 'click', 'purchase', 'add_to_cart']),\n        'page':       random.choice(['/home', '/products', '/checkout', '/login']),\n        'timestamp':  datetime.utcnow().isoformat(),\n        'session_id': str(uuid.uuid4())\n    }\n\n# Send 100 events/second\nwhile True:\n    producer.send('user_events', value=generate_event())\n    time.sleep(0.01)",
      "code_label": "Python — Kafka producer simulating real-time clickstream events"
    },
    {
      "heading": "Structured Streaming Consumer — Kafka to Bronze Delta",
      "content": "3-4 sentences: Databricks Structured Streaming reads from Kafka as a micro-batch stream — every 10 seconds, new events are consumed, parsed from JSON, and appended to the Bronze Delta table. The checkpoint location in ADLS tracks exactly which Kafka offsets have been processed — restart the stream and it continues exactly where it left off, never reprocessing or losing events.",
      "code": "from pyspark.sql.functions import from_json, col, current_timestamp\nfrom pyspark.sql.types import StructType, StructField, StringType, TimestampType\n\n# Schema for Kafka event payload\nEVENT_SCHEMA = StructType([\n    StructField('event_id',   StringType()),\n    StructField('user_id',    StringType()),\n    StructField('event_type', StringType()),\n    StructField('page',       StringType()),\n    StructField('timestamp',  StringType()),\n    StructField('session_id', StringType())\n])\n\nkafka_df = (\n    spark.readStream.format('kafka')\n         .option('kafka.bootstrap.servers', 'kafka-broker:9092')\n         .option('subscribe', 'user_events')\n         .option('startingOffsets', 'latest')\n         .option('failOnDataLoss', 'false')\n         .load()\n)\n\nparsed_df = (\n    kafka_df\n    .select(from_json(col('value').cast('string'), EVENT_SCHEMA).alias('event'))\n    .select('event.*')\n    .withColumn('_consumed_at', current_timestamp())\n)\n\n(parsed_df.writeStream\n          .format('delta')\n          .outputMode('append')\n          .option('checkpointLocation', 'abfss://checkpoints@storage.dfs.core.windows.net/user_events/')\n          .table('prod.clickstream.events_bronze')\n          .start())",
      "code_label": "Python — Kafka → Databricks Structured Streaming → Bronze Delta"
    },
    {
      "heading": "DLT Silver & Gold — Validation and 1-Minute Aggregates",
      "content": "3-4 sentences: DLT Silver validates events (drop unknown event types, filter null user IDs) and parses the timestamp string to a proper timestamp type. Gold uses a 1-minute tumbling window aggregate — active unique users, total page views, purchase count, and conversion rate — updated every 30 seconds. Grafana connects to the Gold Delta table via Databricks SQL for a live dashboard.",
      "code": "import dlt\nfrom pyspark.sql.functions import col, to_timestamp, window, countDistinct, count, when\n\n@dlt.table\n@dlt.expect_or_drop('known_event_type', \"event_type IN ('page_view','click','purchase','add_to_cart')\")\n@dlt.expect_or_drop('valid_user',        'user_id IS NOT NULL')\ndef events_silver():\n    return (\n        dlt.read_stream('events_bronze')\n           .withColumn('event_ts', to_timestamp('timestamp'))\n           .drop('timestamp')\n    )\n\n@dlt.table(comment='1-minute rolling metrics for Grafana dashboard')\ndef clickstream_metrics_gold():\n    return (\n        dlt.read_stream('events_silver')\n           .withWatermark('event_ts', '2 minutes')\n           .groupBy(window('event_ts', '1 minute'))\n           .agg(\n               countDistinct('user_id').alias('active_users'),\n               count('event_id').alias('total_events'),\n               count(when(col('event_type') == 'purchase', 1)).alias('purchases'),\n               count(when(col('event_type') == 'page_view', 1)).alias('page_views')\n           )\n    )",
      "code_label": "Python — DLT Silver validation + Gold 1-minute streaming aggregates"
    },
    {
      "heading": "Monitoring, Alerting & Production Checklist",
      "content": "3-4 sentences: Production streaming pipelines need: (1) lag monitoring — alert if Kafka consumer lag exceeds 10K events (use Azure Monitor or Confluent Cloud metrics), (2) dead-letter topic — route malformed events to user_events_dlq instead of dropping them, (3) schema registry — use Confluent Schema Registry or AWS Glue Schema Registry to enforce event schema at the producer, (4) auto-scaling — enable Databricks cluster autoscaling so the stream handles traffic spikes automatically.",
      "code": "",
      "code_label": ""
    }
  ],
  "cheat_sheet_rows": [
    ["Concept / Config", "What It Does", "Production Setting"],
    ["startingOffsets: latest", "Start consuming from newest events", "Use 'earliest' for backfill / initial load"],
    ["checkpointLocation", "Track processed Kafka offsets in ADLS", "Never share checkpoints between streams"],
    ["failOnDataLoss: false", "Continue if Kafka topic offset gaps", "Required for Kafka topic compaction"],
    ["withWatermark", "Handle late-arriving events in aggregations", "Set to 2x max expected event latency"],
    ["window() tumbling", "Fixed non-overlapping time windows", "1-minute metrics for live dashboards"],
    ["outputMode: append", "Write only new rows to sink", "Use for Bronze raw event tables"],
    ["outputMode: complete", "Overwrite entire sink with updated agg", "Use for small Gold aggregation tables"],
    ["Delta + Structured Streaming", "Exactly-once end-to-end guarantee", "Default when writing to Delta sink"],
    ["Dead-letter topic", "Route bad events to separate Kafka topic", "Never silently discard malformed events"],
    ["Kafka Consumer Lag", "Events in topic not yet consumed", "Alert if lag > 10K events in prod"],
    ["Schema Registry", "Enforce event schema at producer", "Prevents schema breaking changes"]
  ],
  "key_takeaways": [
    "Kafka + Databricks Structured Streaming + Delta Lake = exactly-once real-time pipeline in 50 lines",
    "Always set checkpointLocation — it's what makes streaming pipelines restartable without data loss",
    "withWatermark handles late-arriving events — set it to 2x your maximum expected event delay",
    "DLT Expectations in Silver prevent bad events from corrupting your Gold aggregation metrics",
    "Dead-letter topic: route malformed events to user_events_dlq — never silently drop them",
    "Monitor Kafka consumer lag — if it grows, your streaming job is slower than event production rate",
    "Use Databricks cluster autoscaling so your stream handles traffic spikes without manual intervention"
  ],
  "linkedin_caption": "⚡ Mini Project: Real-Time Streaming Pipeline — Kafka + Databricks + Delta Lake!\\n\\nUser clicks web app → Kafka → Structured Streaming → Delta Lake → Grafana live dashboard. End to end. Real code. Production patterns.\\n\\nThis Thursday's PDF walks through every layer: Kafka producer, Structured Streaming consumer, DLT Silver/Gold with 1-minute aggregates, and production monitoring checklist.\\n\\n📥 Download it. This is the most common streaming architecture in modern data teams.\\n\\nDo you run streaming pipelines in production? What's your biggest challenge?",
  "hashtags": "#Kafka #Databricks #StructuredStreaming #DeltaLake #DataEngineering #RealTime #StreamProcessing #DLT #Python"
}""",
    },

    # ── Topic 15 ───────────────────────────────────────────────────────────────
    {
        "label": "Mini Project — AI-Powered Data Quality Monitor",
        "prompt": """Generate a comprehensive guide for a 3-4 page LinkedIn PDF for a mini project: building an AI-powered data quality monitoring system using Python, Great Expectations, and LLMs.

Return ONLY valid JSON (no markdown, no backticks, no extra text outside JSON):
{
  "title": "Mini Project: AI-Powered Data Quality Monitor",
  "subtitle": "Great Expectations · LLM Anomaly Detection · Slack Alerts · Delta Lake · Full Code",
  "week_label": "Thursday Deep Dive | Mini Project Series",
  "introduction": "2-3 sentences: This mini project builds an intelligent data quality system that goes beyond simple null checks — it uses Great Expectations for rule-based validation, an LLM to detect statistical anomalies and explain them in plain English, and Slack webhooks to alert the team instantly with AI-generated root cause analysis.",
  "sections": [
    {
      "heading": "Great Expectations — Automated Rule-Based Validation",
      "content": "3-4 sentences: Great Expectations (GX) is the industry standard for data quality validation in Python pipelines. You define Expectations (rules) about your data: column not null, value in range, row count between bounds, regex match, referential integrity. GX runs these rules, produces a JSON Validation Result, and generates beautiful HTML data quality reports. Integrate GX into every Delta table write in your Databricks pipeline.",
      "code": "import great_expectations as gx\nfrom great_expectations.dataset import SparkDFDataset\n\n# Load Delta table as Spark DataFrame\ndf = spark.read.format('delta').load('/mnt/silver/sales_transactions')\ngx_df = SparkDFDataset(df)\n\n# Define expectations — the data quality rules\ngx_df.expect_column_to_exist('order_id')\ngx_df.expect_column_values_to_not_be_null('customer_id')\ngx_df.expect_column_values_to_be_between('order_amount', min_value=0.01, max_value=1_000_000)\ngx_df.expect_column_values_to_match_regex('order_date', r'^\\d{4}-\\d{2}-\\d{2}$')\ngx_df.expect_table_row_count_to_be_between(min_value=1000, max_value=10_000_000)\ngx_df.expect_column_values_to_be_in_set('currency', ['USD', 'EUR', 'GBP', 'INR'])\n\n# Run validation and get results\nresult = gx_df.validate()\nprint(f'Success: {result.success}')\nprint(f'Failed: {sum(1 for r in result.results if not r.success)}/{len(result.results)} checks')",
      "code_label": "Python — Great Expectations validation on a Silver Delta table"
    },
    {
      "heading": "LLM Anomaly Detection — AI Explains What's Wrong",
      "content": "3-4 sentences: Rule-based checks catch known problems — but LLMs detect unknown patterns. After GX runs, pass the validation results JSON + table statistics (row count trend, null rate trend, value distribution) to Claude or GPT-4 and ask it to identify anomalies and probable root causes in plain English. The LLM can spot things like: 'Row count dropped 40% vs yesterday — this matches the pattern of a source system outage'.",
      "code": "import anthropic, json\n\nclient = anthropic.Anthropic()\n\ndef ai_analyze_quality(gx_result: dict, table_stats: dict) -> str:\n    failed_checks = [\n        r for r in gx_result['results']\n        if not r['success']\n    ]\n    prompt = f\"\"\"\nYou are a senior data quality engineer. Analyze these data quality results.\n\nFailed validation checks:\n{json.dumps(failed_checks, indent=2)}\n\nTable statistics trend (last 7 days):\n{json.dumps(table_stats, indent=2)}\n\nProvide:\n1. Root cause hypothesis for each failure (2-3 sentences each)\n2. Severity: CRITICAL / HIGH / MEDIUM / LOW\n3. Recommended immediate action\n4. Prevention recommendation\n\nBe specific and actionable. Avoid generic responses.\n\"\"\"\n    msg = client.messages.create(\n        model='claude-3-5-sonnet-20241022',\n        max_tokens=800,\n        messages=[{'role': 'user', 'content': prompt}]\n    )\n    return msg.content[0].text",
      "code_label": "Python — Claude analyzes GX failures and explains root cause in plain English"
    },
    {
      "heading": "Slack Alert with AI-Generated Root Cause",
      "content": "3-4 sentences: The final piece: when data quality fails, send a Slack message containing the failed checks AND the AI-generated root cause analysis. Engineers get actionable context immediately — not just 'null check failed on column order_id' but 'The null rate on order_id jumped to 15% — this matches the pattern of the CRM export job failing mid-run. Check the CRM scheduler logs for 2-4 AM UTC.'",
      "code": "import requests\n\ndef send_slack_alert(table: str, failed_count: int, ai_analysis: str, webhook_url: str):\n    severity_emoji = '🔴' if 'CRITICAL' in ai_analysis else '🟡'\n    message = {\n        'blocks': [\n            {\n                'type': 'header',\n                'text': {'type': 'plain_text', 'text': f'{severity_emoji} Data Quality Alert: {table}'}\n            },\n            {\n                'type': 'section',\n                'text': {\n                    'type': 'mrkdwn',\n                    'text': f'*{failed_count} quality checks failed*\\n\\n*🤖 AI Root Cause Analysis:*\\n{ai_analysis[:1000]}'\n                }\n            },\n            {\n                'type': 'section',\n                'text': {'type': 'mrkdwn', 'text': f'*Table:* `{table}` | *Time:* {datetime.utcnow():%Y-%m-%d %H:%M} UTC'}\n            }\n        ]\n    }\n    requests.post(webhook_url, json=message)\n\n# Full pipeline: GX → LLM → Slack\nresult   = gx_df.validate()\nfailed   = [r for r in result.results if not r.success]\nif failed:\n    analysis = ai_analyze_quality(result.to_json_dict(), get_table_stats('sales_transactions'))\n    send_slack_alert('sales_transactions', len(failed), analysis, SLACK_WEBHOOK)",
      "code_label": "Python — Slack alert with AI root cause analysis on data quality failure"
    },
    {
      "heading": "Scheduling & Production Integration",
      "content": "3-4 sentences: Run the quality monitor after every pipeline write using a Databricks Job downstream task. Store all validation results in a Delta table (dq_results) for trending — track which checks fail most often over time. Build a Databricks SQL dashboard over dq_results to show data quality score by table, by day. Set a data quality SLA: Gold tables must have 98%+ pass rate or the downstream job does not run.",
      "code": "",
      "code_label": ""
    }
  ],
  "cheat_sheet_rows": [
    ["Component", "Tool / Library", "What It Checks / Does"],
    ["Null checks", "Great Expectations", "expect_column_values_to_not_be_null()"],
    ["Range checks", "Great Expectations", "expect_column_values_to_be_between()"],
    ["Row count check", "Great Expectations", "expect_table_row_count_to_be_between()"],
    ["Regex check", "Great Expectations", "expect_column_values_to_match_regex()"],
    ["Set membership", "Great Expectations", "expect_column_values_to_be_in_set()"],
    ["Anomaly detection", "LLM (Claude / GPT-4)", "Explain statistical anomalies in plain English"],
    ["Root cause analysis", "LLM prompt with stats trend", "Correlate failures with upstream patterns"],
    ["Alerting", "Slack Incoming Webhook", "Block message with severity + AI explanation"],
    ["Result storage", "Delta table (dq_results)", "Track quality score trends over time"],
    ["Dashboard", "Databricks SQL", "Data quality score by table, by day"],
    ["Scheduling", "Databricks Jobs (downstream task)", "Run DQ monitor after every pipeline write"]
  ],
  "key_takeaways": [
    "Great Expectations + 10 expectation rules covers 90% of common data quality problems in pipelines",
    "LLMs turn cryptic GX failure JSON into plain English root cause explanations engineers can act on",
    "Slack alerts with AI analysis mean engineers fix issues before business users notice stale data",
    "Store all GX results in a Delta table to track quality score trends and catch recurring failures",
    "Set a data quality SLA: downstream jobs do not run if the Gold table DQ score drops below 98%",
    "The full system (GX + LLM + Slack) takes one day to build and runs automated on every pipeline write",
    "LLM anomaly detection catches patterns that rule-based checks miss — like 'same failure every Monday'"
  ],
  "linkedin_caption": "🔍 Mini Project: Build an AI-Powered Data Quality Monitor in One Day!\\n\\nGreat Expectations catches rule violations. Claude explains WHY it failed in plain English. Slack sends the alert with root cause analysis automatically.\\n\\nNo more 'null check failed on column X' — your team gets: 'The null rate jumped 15% — this matches a CRM export job failure. Check the scheduler logs.'\\n\\nThis Thursday's PDF: full code, GX setup, LLM integration, Slack alerts, result tracking. 3 pages.\\n\\n📥 Save it. Build it. Your data team will thank you.\\n\\nWhat's your current data quality monitoring setup?",
  "hashtags": "#DataQuality #GreatExpectations #LLM #Claude #DataEngineering #Python #Databricks #AI #DataReliability #Slack"
}""",
    },

    # ── Topic 16 ───────────────────────────────────────────────────────────────
    {
        "label": "Databricks + Snowflake Integration Patterns",
        "prompt": """Generate a comprehensive guide for a 3-4 page LinkedIn PDF about integrating Databricks and Snowflake together in a modern data architecture.

Return ONLY valid JSON (no markdown, no backticks, no extra text outside JSON):
{
  "title": "Databricks + Snowflake — Complete Integration Patterns",
  "subtitle": "Snowflake Connector · Delta Sharing · Zero-Copy · dbt · When to Use Which",
  "week_label": "Thursday Deep Dive | Data Architecture Series",
  "introduction": "2-3 sentences: Databricks and Snowflake are the two dominant platforms in modern data architecture — and most enterprise data teams use BOTH. Databricks excels at heavy ETL, ML, and streaming; Snowflake excels at concurrency, BI, and data sharing. This guide covers every integration pattern so you can use the right tool for each layer.",
  "sections": [
    {
      "heading": "When to Use Databricks vs Snowflake",
      "content": "3-4 sentences: Databricks: choose for complex ETL/ELT transformations, ML model training, streaming pipelines, Delta Lake storage, and workloads requiring PySpark or custom Python. Snowflake: choose for high-concurrency BI queries, semi-structured JSON querying, clean SQL transformations, and data sharing with external partners. Most architectures: Databricks handles Bronze/Silver transformation, Snowflake serves as the Gold/BI layer for analysts.",
      "code": "# Common pattern: Databricks transforms → Snowflake serves\n# Architecture:\n#\n# Raw Data (ADLS/S3)\n#     ↓  Auto Loader\n# Bronze Delta (Databricks) — raw ingestion\n#     ↓  DLT / PySpark\n# Silver Delta (Databricks) — clean + enrich\n#     ↓  Snowflake Spark Connector\n# Snowflake Gold (Snowflake) — BI / analyst queries\n#     ↓\n# Power BI / Tableau / Sigma\n#\n# Why split it?\n# Databricks: better for Python, ML, streaming, complex transforms\n# Snowflake: better for concurrent BI, SQL-first analysts, data sharing",
      "code_label": "Architecture — Databricks Bronze/Silver → Snowflake Gold pattern"
    },
    {
      "heading": "Snowflake Spark Connector — Read/Write from Databricks",
      "content": "3-4 sentences: The official Snowflake Connector for Spark lets Databricks read from and write to Snowflake tables directly. It supports pushdown optimization — aggregations and filters run inside Snowflake rather than pulling all data to Spark. Always store Snowflake credentials in Databricks Secret Scopes — never hardcode passwords in notebooks.",
      "code": "# Install on cluster: net.snowflake:spark-snowflake_2.12:2.15.0-spark_3.3\n\nSF_OPTIONS = {\n    'sfUrl':       'myorg.snowflakecomputing.com',\n    'sfUser':      dbutils.secrets.get('prod-secrets', 'sf-user'),\n    'sfPassword':  dbutils.secrets.get('prod-secrets', 'sf-password'),\n    'sfDatabase':  'PROD_DW',\n    'sfSchema':    'GOLD',\n    'sfWarehouse': 'TRANSFORM_WH',\n    'sfRole':      'DATA_ENGINEER'\n}\n\n# Read from Snowflake into Databricks (with pushdown)\ndf = (spark.read.format('snowflake')\n           .options(**SF_OPTIONS)\n           .option('dbtable', 'CUSTOMER_SEGMENTS')\n           .load())\n\n# Write Databricks Silver Delta table to Snowflake Gold\n(silver_df.write.format('snowflake')\n          .options(**SF_OPTIONS)\n          .option('dbtable', 'SALES_FACT_GOLD')\n          .mode('overwrite')\n          .save())",
      "code_label": "Python — Read from and write to Snowflake from Databricks"
    },
    {
      "heading": "Delta Sharing — Zero-Copy Data Sharing",
      "content": "3-4 sentences: Delta Sharing (open protocol, supported natively by both Databricks and Snowflake) lets you share live Delta tables with Snowflake consumers — no data duplication, no ETL copy job. The Snowflake side mounts the share as an external table and queries it directly from ADLS/S3. This is the cleanest integration when you want Snowflake analysts to access Databricks Delta data without a copy.",
      "code": "-- Databricks side: create a Delta Share for Snowflake\nCREATE SHARE IF NOT EXISTS snowflake_share;\nADD TABLE prod.gold.customer_segments TO SHARE snowflake_share;\nADD TABLE prod.gold.revenue_by_region  TO SHARE snowflake_share;\n\nCREATE RECIPIENT IF NOT EXISTS snowflake_team\n  COMMENT 'Snowflake analytics team access';\n\nGRANT SELECT ON SHARE snowflake_share TO RECIPIENT snowflake_team;\n\n-- Get activation link for Snowflake team\nDESCRIBE RECIPIENT snowflake_team;\n-- Provides: activation_link → give to Snowflake admin to mount the share\n\n-- Snowflake side: mount the Delta Share\nCREATE DATABASE FROM SHARE databricks_provider.snowflake_share;",
      "code_label": "SQL — Delta Sharing from Databricks to Snowflake — zero data copy"
    },
    {
      "heading": "dbt with Both Platforms — Unified Transformation Layer",
      "content": "3-4 sentences: dbt (data build tool) works with both Databricks (dbt-databricks adapter) and Snowflake (dbt-snowflake adapter) — you can run the same dbt models on either platform by changing the profile. Teams that use dbt get SQL-based transformations, automatic lineage, data testing, and documentation that works across both Databricks and Snowflake. This is the recommended transformation layer when your team is SQL-first.",
      "code": "",
      "code_label": ""
    }
  ],
  "cheat_sheet_rows": [
    ["Pattern", "How It Works", "Best Use Case"],
    ["Snowflake Spark Connector read", "Databricks reads Snowflake table as DataFrame", "ML training on Snowflake data"],
    ["Snowflake Spark Connector write", "Databricks writes Delta data to Snowflake table", "Load Silver Delta into Snowflake Gold"],
    ["Delta Sharing (DB→SF)", "Snowflake mounts live Delta table as external", "Zero-copy access — no ETL needed"],
    ["dbt-databricks", "Run dbt models on Databricks SQL Warehouse", "SQL-first transformations on Delta Lake"],
    ["dbt-snowflake", "Run dbt models on Snowflake compute", "SQL-first transformations in Snowflake"],
    ["Databricks → Snowflake COPY", "Databricks writes Parquet to S3, Snowflake COPY INTO", "Alternative to Spark connector for large loads"],
    ["Snowflake External Table on S3", "Snowflake queries Parquet/Delta files directly", "Lightweight access without full data load"],
    ["Pushdown optimization (SF connector)", "Aggregations run in Snowflake not Spark", "Always enabled — avoids large data transfer"],
    ["Secret Scopes for SF creds", "Store SF password in Databricks secrets", "Never hardcode sfPassword in notebooks"],
    ["Separate warehouses per workload", "TRANSFORM_WH for ETL, BI_WH for dashboards", "Prevent ETL from blocking analyst queries"]
  ],
  "key_takeaways": [
    "Use Databricks for ETL, streaming, ML — use Snowflake for BI concurrency and data sharing",
    "Snowflake Spark Connector supports pushdown — aggregations run in Snowflake, not on Spark workers",
    "Delta Sharing lets Snowflake analysts query live Databricks Delta tables with zero data duplication",
    "Always store Snowflake credentials in Databricks Secret Scopes — never in notebook code",
    "dbt works with both platforms — unify transformation logic in SQL regardless of compute engine",
    "Use separate Snowflake warehouses for ETL and BI to prevent resource contention",
    "Most enterprise architectures use both: Databricks for processing heavy lifting, Snowflake for analyst access"
  ],
  "linkedin_caption": "❄️ Databricks + Snowflake — How to Use Both Together (The Right Way)!\\n\\nMost enterprise data teams use BOTH platforms — but they're not sure which layer belongs where.\\n\\nThis Thursday's PDF: when to use each, Snowflake Spark Connector with real code, Delta Sharing (zero-copy), dbt with both platforms. Full cheat sheet.\\n\\n📥 Download it and architect your next data platform with confidence.\\n\\nDoes your team use Databricks, Snowflake, or both?",
  "hashtags": "#Databricks #Snowflake #DataEngineering #DeltaLake #DeltaSharing #dbt #DataArchitecture #Azure #AWS"
}""",
    },

    # ── Topic 17 ───────────────────────────────────────────────────────────────
    {
        "label": "dbt — Data Build Tool Complete Guide",
        "prompt": """Generate a comprehensive guide for a 3-4 page LinkedIn PDF about dbt (data build tool) for data engineers.

Return ONLY valid JSON (no markdown, no backticks, no extra text outside JSON):
{
  "title": "dbt — The Data Build Tool Every Data Engineer Must Know",
  "subtitle": "Models · Tests · Sources · Macros · CI/CD · dbt Cloud · Cheat Sheet",
  "week_label": "Thursday Deep Dive | Data Transformation Series",
  "introduction": "2-3 sentences: dbt (data build tool) has become the standard for SQL-based data transformation — it brings software engineering practices to SQL: version control, testing, documentation, and modular code. Over 30,000 companies use dbt in production, including GitLab, Shopify, and JetBlue. This guide covers everything a data engineer needs to be productive with dbt in one week.",
  "sections": [
    {
      "heading": "dbt Core Concepts — Models, Sources & Refs",
      "content": "3-4 sentences: In dbt, a model is a single SQL SELECT statement saved as a .sql file — dbt compiles it into a CREATE TABLE or VIEW statement and runs it against your warehouse. ref() references another model (creating an automatic dependency graph), and source() references a raw table in your warehouse. dbt builds the full dependency DAG and executes models in the correct order — no more manually ordering SQL scripts.",
      "code": "-- models/silver/stg_orders.sql — staging model (view)\n{{ config(materialized='view') }}\n\nSELECT\n    order_id,\n    customer_id,\n    CAST(order_amount AS DECIMAL(18,2))  AS order_amount,\n    CAST(order_date   AS DATE)           AS order_date,\n    UPPER(TRIM(status))                  AS status,\n    _loaded_at\nFROM {{ source('raw', 'orders') }}  -- references raw.orders table\nWHERE order_id IS NOT NULL\n\n-- models/gold/fct_daily_revenue.sql — fact table (incremental)\n{{ config(materialized='incremental', unique_key='order_date') }}\n\nSELECT\n    order_date,\n    SUM(order_amount) AS daily_revenue,\n    COUNT(order_id)   AS order_count\nFROM {{ ref('stg_orders') }}         -- ref() creates the dependency\n{% if is_incremental() %}\n    WHERE order_date > (SELECT MAX(order_date) FROM {{ this }})\n{% endif %}\nGROUP BY order_date",
      "code_label": "SQL — dbt staging model (view) and incremental fact model"
    },
    {
      "heading": "dbt Tests — Data Quality Built In",
      "content": "3-4 sentences: dbt has four built-in generic tests: not_null, unique, accepted_values, and relationships (referential integrity). You apply them in YAML — no SQL needed. Add custom singular tests for complex business rules as plain SQL files in the tests/ folder. Run dbt test in CI to catch data quality issues before they reach production.",
      "code": "# models/silver/schema.yml — dbt tests as YAML\nversion: 2\n\nmodels:\n  - name: stg_orders\n    description: 'Cleaned and typed orders from raw source'\n    columns:\n      - name: order_id\n        description: 'Unique order identifier'\n        tests:\n          - not_null\n          - unique\n      - name: status\n        tests:\n          - accepted_values:\n              values: ['PENDING', 'CONFIRMED', 'SHIPPED', 'DELIVERED', 'CANCELLED']\n      - name: customer_id\n        tests:\n          - not_null\n          - relationships:\n              to: ref('stg_customers')\n              field: customer_id\n      - name: order_amount\n        tests:\n          - not_null\n          - dbt_utils.expression_is_true:\n              expression: \">= 0\"",
      "code_label": "YAML — dbt schema tests: unique, not_null, accepted_values, relationships"
    },
    {
      "heading": "dbt Macros & Packages — Reusable SQL Logic",
      "content": "3-4 sentences: Macros are Jinja-templated SQL functions — write once, reuse across all models. Common macros: generate_surrogate_key() (hash-based PK), SCD Type 2 snapshot, date spine generator. dbt packages extend functionality — dbt_utils, dbt_expectations (Great Expectations-style tests), and dbt_audit_helper are used in most production dbt projects. Install packages in packages.yml and run dbt deps.",
      "code": "-- macros/clean_string.sql — reusable macro for all models\n{% macro clean_string(column_name) %}\n    UPPER(TRIM(REGEXP_REPLACE({{ column_name }}, '[^a-zA-Z0-9 ]', '')))\n{% endmacro %}\n\n-- Use in any model:\nSELECT\n    {{ clean_string('product_name') }} AS product_name,\n    {{ dbt_utils.generate_surrogate_key(['order_id', 'product_id']) }} AS sk\nFROM {{ ref('stg_order_items') }}\n\n-- packages.yml — install community packages\npackages:\n  - package: dbt-labs/dbt_utils\n    version: '>=1.1.0'\n  - package: calogica/dbt_expectations\n    version: '>=0.10.0'\n  - package: dbt-labs/audit_helper\n    version: '>=0.9.0'",
      "code_label": "Jinja + YAML — dbt macro and packages configuration"
    },
    {
      "heading": "dbt in Production — CI/CD & dbt Cloud",
      "content": "3-4 sentences: Production dbt: PR in GitHub triggers dbt build --select state:modified+ (run only changed models and dependants) via GitHub Actions. dbt Cloud provides a managed scheduler, IDE, documentation hosting, and job alerts. Environment variables (dev/prod) control which database/schema models land in — dev runs land in dev schema, prod runs in prod schema.",
      "code": "",
      "code_label": ""
    }
  ],
  "cheat_sheet_rows": [
    ["dbt Command / Concept", "What It Does", "When to Use"],
    ["dbt run", "Compile and run all models against warehouse", "Full refresh — use sparingly in prod"],
    ["dbt run --select +model_name", "Run model and all upstream dependencies", "Run a specific model with its parents"],
    ["dbt test", "Run all schema and custom tests", "After every dbt run in CI pipeline"],
    ["dbt build", "Run + Test in one command", "CI pipeline: build and test together"],
    ["dbt docs generate + serve", "Build and host interactive documentation", "Share data catalog with stakeholders"],
    ["materialized: view", "Model built as SQL view", "Lightweight staging models"],
    ["materialized: table", "Model built as physical table", "Frequently queried Gold tables"],
    ["materialized: incremental", "Only new/changed rows processed", "Large fact tables — process daily delta"],
    ["materialized: snapshot", "Track row history (SCD Type 2)", "Customer/product attribute history"],
    ["ref()", "Reference another dbt model", "Creates dependency — dbt orders execution"],
    ["source()", "Reference a raw table in warehouse", "Base tables not managed by dbt"]
  ],
  "key_takeaways": [
    "dbt models are just SELECT statements — one file per table, version-controlled in Git",
    "ref() creates the DAG automatically — dbt runs models in correct dependency order",
    "Four built-in tests (not_null, unique, accepted_values, relationships) cover most DQ needs",
    "Incremental materialization processes only new rows — essential for large fact tables",
    "dbt docs generate creates an interactive data catalog with lineage — share with stakeholders",
    "Use dbt build in CI (PR) to run and test only changed models: --select state:modified+",
    "Install dbt_utils and dbt_expectations packages — they eliminate 80% of custom macro writing"
  ],
  "linkedin_caption": "🛠️ dbt — The Tool That Turned SQL Into Software Engineering!\\n\\nVersion control. Automated testing. Dependency management. Interactive documentation. All in SQL.\\n\\nThis Thursday's PDF is a complete dbt guide: models, sources, refs, tests, macros, incremental loads, CI/CD. Full cheat sheet with every command.\\n\\n📥 Save it. This is the fastest way to get productive with dbt.\\n\\nAre you using dbt in your data stack?",
  "hashtags": "#dbt #DataBuildTool #DataEngineering #SQL #DataTransformation #Databricks #Snowflake #DataOps #Analytics"
}""",
    },

    # ── Topic 18 ───────────────────────────────────────────────────────────────
    {
        "label": "Apache Airflow for Data Orchestration",
        "prompt": """Generate a comprehensive guide for a 3-4 page LinkedIn PDF about Apache Airflow for orchestrating data pipelines.

Return ONLY valid JSON (no markdown, no backticks, no extra text outside JSON):
{
  "title": "Apache Airflow — Complete Orchestration Guide for Data Engineers",
  "subtitle": "DAGs · Operators · Sensors · TaskFlow API · Astronomer · Airflow on Databricks",
  "week_label": "Thursday Deep Dive | Pipeline Orchestration Series",
  "introduction": "2-3 sentences: Apache Airflow is the most widely deployed data pipeline orchestrator — over 13 million downloads/month. It lets you define pipelines as Python code, schedule them, visualise dependencies, retry on failure, and alert on issues. Whether you're on Databricks, AWS, GCP, or on-prem, Airflow works as the single control plane for all your pipeline schedules.",
  "sections": [
    {
      "heading": "Airflow Fundamentals — DAGs, Tasks & Operators",
      "content": "3-4 sentences: A DAG (Directed Acyclic Graph) is the Airflow pipeline — it defines tasks and the dependencies between them. Operators are pre-built task types: PythonOperator (run a Python function), BashOperator (run a shell command), DatabricksRunNowOperator (trigger a Databricks job), SqlOperator (run SQL). The TaskFlow API (@task decorator) is the modern way to write Airflow DAGs — cleaner than instantiating operators directly.",
      "code": "from airflow.decorators import dag, task\nfrom airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator\nfrom pendulum import datetime\n\n@dag(\n    schedule='0 2 * * *',  # 2 AM UTC daily\n    start_date=datetime(2024, 1, 1),\n    catchup=False,\n    tags=['sales', 'etl', 'daily'],\n    default_args={'retries': 2, 'retry_delay': timedelta(minutes=5)}\n)\ndef sales_etl_pipeline():\n\n    @task()\n    def validate_source_files():\n        # Check ADLS landing zone has today's files\n        from azure.storage.blob import BlobServiceClient\n        client = BlobServiceClient.from_connection_string(CONN_STR)\n        blobs  = list(client.get_container_client('landing').list_blobs(prefix=f'crm/{today}'))\n        if not blobs:\n            raise ValueError(f'No source files found for {today}')\n        return len(blobs)\n\n    run_databricks_etl = DatabricksRunNowOperator(\n        task_id='run_databricks_etl',\n        databricks_conn_id='databricks_prod',\n        job_id=12345  # Databricks job ID\n    )\n\n    validate_source_files() >> run_databricks_etl\n\nsales_etl_pipeline()",
      "code_label": "Python — Airflow DAG with TaskFlow API and Databricks operator"
    },
    {
      "heading": "Sensors — Wait for Data Before Running",
      "content": "3-4 sentences: Sensors are a special type of operator that waits for a condition to be true before proceeding — a file to appear in ADLS, a table partition to exist, an API endpoint to return 200. Use sensors at the start of your DAG to wait for upstream data instead of hard-coding time delays. Always set a timeout (poke_interval + timeout) to prevent sensors running forever and blocking Airflow workers.",
      "code": "from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor\nfrom airflow.providers.http.sensors.http import HttpSensor\n\n# Wait for today's file to land in ADLS/S3 before running ETL\nwait_for_file = S3KeySensor(\n    task_id='wait_for_crm_export',\n    bucket_key=f's3://data-lake/landing/crm/{today}/export.csv',\n    aws_conn_id='aws_prod',\n    poke_interval=60,   # check every 60 seconds\n    timeout=3600,       # fail after 1 hour if file never arrives\n    mode='reschedule'   # release worker slot between pokes (saves resources)\n)\n\n# Wait for upstream API to be healthy\nwait_for_api = HttpSensor(\n    task_id='wait_for_crm_api',\n    http_conn_id='crm_api',\n    endpoint='/health',\n    poke_interval=30,\n    timeout=600,\n    mode='reschedule'\n)\n\n# Dependency: both sensors must pass before ETL runs\n[wait_for_file, wait_for_api] >> run_databricks_etl",
      "code_label": "Python — S3KeySensor and HttpSensor with reschedule mode"
    },
    {
      "heading": "Connections, Variables & Secrets",
      "content": "3-4 sentences: Airflow Connections store credentials for external systems (Databricks, AWS, Snowflake, Postgres) — configure them in the Airflow UI or via environment variables. Variables store pipeline configuration values. In production, back connections and variables with a secrets backend (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault) — Airflow reads secrets from the backend at runtime, never storing them in the Airflow DB.",
      "code": "# Set Databricks connection via environment variable (no Airflow UI needed)\n# AIRFLOW_CONN_DATABRICKS_PROD=databricks://token@prod.azuredatabricks.net?token=dapi...\n\n# Or configure secrets backend (airflow.cfg or env vars):\n# [secrets]\n# backend = airflow.providers.azure.secrets.azure_key_vault.AzureKeyVaultBackend\n# backend_kwargs = {\"connections_prefix\": \"airflow-conn\", \"variables_prefix\": \"airflow-var\",\n#                   \"vault_url\": \"https://myvault.vault.azure.net/\"}\n\n# Use in DAG:\nfrom airflow.models import Variable\n\nbatch_size  = Variable.get('sales_etl_batch_size', default_var=10000)\nenv         = Variable.get('environment', default_var='prod')\n# Airflow fetches these from Azure Key Vault at runtime if secrets backend is configured",
      "code_label": "Python + Config — Connections and variables with Azure Key Vault secrets backend"
    },
    {
      "heading": "Managed Airflow — Astronomer, MWAA & Cloud Composer",
      "content": "3-4 sentences: Running Airflow yourself means managing Kubernetes, workers, and upgrades. Managed options: Astronomer (best-in-class managed Airflow, open-source friendly), AWS MWAA (Managed Workflows for Apache Airflow), Google Cloud Composer. For Databricks users: Databricks Workflows (built-in Databricks job orchestration) is simpler for pure Databricks pipelines — use Airflow when you orchestrate across multiple systems (Databricks + Snowflake + APIs + dbt).",
      "code": "",
      "code_label": ""
    }
  ],
  "cheat_sheet_rows": [
    ["Airflow Concept", "What It Does", "Data Engineering Use Case"],
    ["DAG", "Pipeline definition as Python code", "One DAG per pipeline (sales_etl, user_events)"],
    ["PythonOperator / @task", "Run a Python function as a task", "Validate files, call APIs, send alerts"],
    ["DatabricksRunNowOperator", "Trigger a Databricks job by job ID", "Run Databricks ETL from Airflow schedule"],
    ["SnowflakeOperator", "Run SQL in Snowflake", "Run dbt models or Gold layer aggregations"],
    ["S3KeySensor", "Wait for a file to appear in S3/ADLS", "Block ETL until CRM export file lands"],
    ["HttpSensor", "Wait for HTTP endpoint to return 200", "Wait for upstream API to be healthy"],
    ["mode='reschedule'", "Release worker between sensor pokes", "Prevents sensor from blocking Airflow workers"],
    ["XCom", "Pass small values between tasks", "Pass file count from validator to next task"],
    ["Airflow Connections", "Store external system credentials", "Databricks token, AWS key, Snowflake password"],
    ["Secrets Backend (KV/SM)", "Read credentials from external vault", "Zero credentials stored in Airflow DB"],
    ["catchup=False", "Skip historical DAG runs on first deploy", "Always set this — prevents backfill floods"]
  ],
  "key_takeaways": [
    "Use the TaskFlow API (@task decorator) for clean, modern Airflow DAG code — avoid legacy operators",
    "DatabricksRunNowOperator triggers Databricks jobs directly — Airflow schedules, Databricks executes",
    "Always use reschedule mode for sensors — it releases the worker slot between pokes, saving resources",
    "Set timeout on every sensor — a sensor without timeout will block Airflow workers indefinitely",
    "Back Airflow connections with Azure Key Vault or AWS Secrets Manager — never store secrets in Airflow DB",
    "catchup=False is essential — without it, Airflow runs all historical intervals on first DAG deploy",
    "Use Airflow when orchestrating across multiple systems; use Databricks Workflows for pure Databricks pipelines"
  ],
  "linkedin_caption": "🌀 Apache Airflow — The Complete Guide for Data Engineers!\\n\\nScheduling, dependency management, retries, sensors, secrets — all in Python code you version-control in Git.\\n\\nThis Thursday's PDF: DAGs with TaskFlow API, Databricks operator, sensors (wait for files before running!), secrets backend, managed options. Full cheat sheet.\\n\\n📥 Download it. Airflow is a skill every data engineer needs.\\n\\nDo you use Airflow, Databricks Workflows, or something else for orchestration?",
  "hashtags": "#Airflow #ApacheAirflow #DataEngineering #Orchestration #Databricks #ETL #DataPipelines #Python #Astronomer"
}""",
    },

    # ── Topic 19 ───────────────────────────────────────────────────────────────
    {
        "label": "Mini Project — GitHub to Databricks Full DataOps Setup",
        "prompt": """Generate a comprehensive guide for a 3-4 page LinkedIn PDF mini project: setting up a complete DataOps workflow connecting GitHub, Databricks, dbt, and Airflow with full CI/CD from scratch.

Return ONLY valid JSON (no markdown, no backticks, no extra text outside JSON):
{
  "title": "Mini Project: Complete DataOps Setup — GitHub + Databricks + dbt + Airflow",
  "subtitle": "From Zero to Production CI/CD in One Day · Asset Bundles · DAGs · Approvals",
  "week_label": "Thursday Deep Dive | Mini Project Series",
  "introduction": "2-3 sentences: This mini project sets up a production-grade DataOps workflow from scratch — GitHub as the source of truth, Databricks Asset Bundles for pipeline code, dbt for SQL transformations, Airflow for scheduling, and GitHub Actions for full CI/CD with dev/prod deployment gates. Every piece connects end to end with real configuration files.",
  "sections": [
    {
      "heading": "Repository Structure & Branch Strategy",
      "content": "3-4 sentences: One mono-repo per data domain — all pipeline code, dbt models, Databricks notebooks, Airflow DAGs, and infrastructure YAML live in the same Git repo. Branch strategy: feature branches → PR review → merge to main (auto-deploys to dev) → release tag vYYYY.MM.DD (auto-deploys to prod with approval gate). Folder structure: /databricks/ (DABs), /dbt/ (models), /airflow/ (DAGs), /tests/ (unit tests), /infra/ (Bicep/Terraform).",
      "code": "# Repository structure for a complete DataOps project\n# sales-dataops/\n# ├── databricks.yml              # Asset Bundle — Databricks jobs/pipelines\n# ├── databricks/\n# │   ├── notebooks/\n# │   │   ├── 01_bronze.py        # Auto Loader ingestion\n# │   │   ├── 02_silver_dlt.py    # DLT Silver transformations\n# │   │   └── 03_gold_dlt.py      # DLT Gold aggregations\n# │   └── pipelines/\n# │       └── sales_dlt.yml       # DLT pipeline definition\n# ├── dbt/\n# │   ├── dbt_project.yml\n# │   ├── profiles.yml\n# │   ├── models/\n# │   │   ├── staging/            # stg_* views\n# │   │   ├── intermediate/       # int_* views\n# │   │   └── marts/              # fct_*, dim_* tables\n# │   └── tests/\n# ├── airflow/\n# │   └── dags/\n# │       └── sales_etl_dag.py\n# ├── tests/\n# │   ├── test_bronze.py\n# │   └── test_dbt_models.sql\n# └── .github/\n#     └── workflows/\n#         ├── ci.yml              # PR: lint + test\n#         └── deploy.yml          # Push to main/tag: deploy",
      "code_label": "Shell — Complete DataOps repo folder structure"
    },
    {
      "heading": "CI Pipeline — PR Checks (GitHub Actions)",
      "content": "3-4 sentences: Every PR triggers the CI pipeline: Python linting (ruff/flake8), dbt compile + test (slim CI with --select state:modified+), Databricks bundle validate, and pytest for unit tests. CI must pass before the PR can be merged. This catches 95% of bugs before they ever reach a Databricks cluster.",
      "code": "# .github/workflows/ci.yml — runs on every Pull Request\nname: CI — Lint, Test, Validate\non:\n  pull_request:\n    branches: [main]\n\njobs:\n  ci:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n\n      - uses: actions/setup-python@v5\n        with: { python-version: '3.11' }\n\n      - name: Install dependencies\n        run: pip install ruff pytest dbt-databricks databricks-cli\n\n      - name: Lint Python (ruff)\n        run: ruff check databricks/ airflow/ tests/\n\n      - name: dbt compile (slim CI — changed models only)\n        run: |\n          cd dbt\n          dbt deps\n          dbt compile --select state:modified+ --defer --state prod_artifacts/\n        env:\n          DBT_DATABRICKS_HOST:  ${{ secrets.DATABRICKS_HOST }}\n          DBT_DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}\n\n      - name: Databricks bundle validate\n        run: databricks bundle validate\n        env:\n          DATABRICKS_HOST:  ${{ secrets.DATABRICKS_HOST }}\n          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}\n\n      - name: Unit tests (pytest)\n        run: pytest tests/ -v",
      "code_label": "YAML — CI pipeline: lint + dbt compile + bundle validate + pytest on every PR"
    },
    {
      "heading": "CD Pipeline — Deploy to Dev & Prod",
      "content": "3-4 sentences: Merge to main triggers dev deployment: Databricks bundle deploy --target dev + dbt run --target dev. Release tag vYYYY.MM.DD triggers prod deployment with a required reviewer approval gate — no accidental prod pushes. Deployment steps: bundle deploy → DLT pipeline update → dbt run → dbt test → Airflow DAG sync via astro deploy.",
      "code": "# .github/workflows/deploy.yml — deploys to dev on merge, prod on tag\nname: CD — Deploy\non:\n  push:\n    branches: [main]\n    tags: ['v*.*.*']\n\njobs:\n  deploy:\n    runs-on: ubuntu-latest\n    environment: ${{ startsWith(github.ref, 'refs/tags/') && 'production' || 'development' }}\n    env:\n      TARGET: ${{ startsWith(github.ref, 'refs/tags/') && 'prod' || 'dev' }}\n      DATABRICKS_HOST:  ${{ secrets.DATABRICKS_HOST }}\n      DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-python@v5\n        with: { python-version: '3.11' }\n      - run: pip install databricks-cli dbt-databricks\n\n      - name: Deploy Databricks Asset Bundle\n        run: databricks bundle deploy --target $TARGET\n\n      - name: Run dbt transformations\n        run: |\n          cd dbt\n          dbt deps\n          dbt run  --target $TARGET --select state:modified+\n          dbt test --target $TARGET --select state:modified+\n\n      - name: Notify Slack\n        run: |\n          curl -X POST ${{ secrets.SLACK_WEBHOOK }} \\\n            -H 'Content-Type: application/json' \\\n            -d '{\"text\": \"Deployed to ${{ env.TARGET }} — ${{ github.ref_name }}\"}'",
      "code_label": "YAML — CD pipeline: dev on push to main, prod on release tag with approval gate"
    },
    {
      "heading": "Airflow DAG Sync & Production Checklist",
      "content": "3-4 sentences: Sync Airflow DAGs from GitHub using Astronomer's astro deploy command or by pushing DAG files to an S3/ADLS bucket that MWAA watches. Production checklist: (1) all secrets in GitHub Secrets + Azure Key Vault, (2) PR requires 1 reviewer approval, (3) prod GitHub Environment requires a named approver, (4) dbt tests run in every deployment, (5) Slack alerts configured for pipeline failures.",
      "code": "",
      "code_label": ""
    }
  ],
  "cheat_sheet_rows": [
    ["DataOps Component", "Tool", "Key File / Command"],
    ["Source control", "GitHub (mono-repo)", "Branch per feature, PR to main"],
    ["CI — lint", "ruff / flake8 (GitHub Actions)", "ruff check databricks/ airflow/"],
    ["CI — dbt slim CI", "dbt compile state:modified+", "Only compile changed dbt models on PR"],
    ["CI — bundle validate", "Databricks CLI", "databricks bundle validate"],
    ["CI — unit tests", "pytest", "pytest tests/ -v"],
    ["CD — dev deploy", "GitHub Actions on push to main", "databricks bundle deploy --target dev"],
    ["CD — prod deploy", "GitHub Actions on release tag", "Required reviewer in GitHub Environment"],
    ["dbt transformations", "dbt-databricks", "dbt run + dbt test on every deploy"],
    ["Airflow DAG sync", "Astronomer / MWAA S3 sync", "astro deploy or S3 DAG folder push"],
    ["Secrets management", "GitHub Secrets + Azure Key Vault", "Zero secrets in code or Airflow DB"],
    ["Deployment notification", "Slack Webhook (curl)", "Alert on deploy success/failure"]
  ],
  "key_takeaways": [
    "One mono-repo for all pipeline code — notebooks, dbt models, Airflow DAGs, infra YAML",
    "CI on every PR: lint + dbt slim compile + bundle validate + pytest — catches 95% of bugs pre-merge",
    "CD to dev automatically on merge to main; CD to prod only on release tag with required reviewer",
    "dbt slim CI with state:modified+ compiles only changed models — keeps CI fast (<5 minutes)",
    "GitHub Environment with required reviewers is the only approval gate you need for prod deployments",
    "All secrets in GitHub Secrets + Azure Key Vault — zero credentials in code, notebooks, or Airflow DB",
    "This full DataOps setup can be built in one day and eliminates all manual deployment steps forever"
  ],
  "linkedin_caption": "🔄 Mini Project: Complete DataOps Setup — GitHub + Databricks + dbt + Airflow!\\n\\nCI/CD for data pipelines. PR checks. Dev/prod approval gates. Slack alerts. dbt slim CI. All connected.\\n\\nThis Thursday's PDF: full repo structure, CI workflow (lint + validate + test), CD workflow (dev auto-deploy, prod approval gate), and production checklist.\\n\\n📥 Download it. Set it up this week. Your future self will thank you.\\n\\nWhat's your current deployment process for data pipelines?",
  "hashtags": "#DataOps #DataEngineering #GitHub #Databricks #dbt #Airflow #CICD #GitOps #DataPlatform #DevOps"
}""",
    },

    # ── Topic 20 ───────────────────────────────────────────────────────────────
    {
        "label": "PySpark Performance Optimization — Deep Dive",
        "prompt": """Generate a comprehensive guide for a 3-4 page LinkedIn PDF about deep PySpark performance optimization for data engineers.

Return ONLY valid JSON (no markdown, no backticks, no extra text outside JSON):
{
  "title": "PySpark Performance Optimization — The Deep Dive Guide",
  "subtitle": "Shuffle · Skew · AQE · Broadcast · Caching · Photon · Cheat Sheet",
  "week_label": "Thursday Deep Dive | PySpark Mastery Series",
  "introduction": "2-3 sentences: Most PySpark performance problems come from 5 root causes — data skew, excessive shuffles, wrong join strategy, missing partition pruning, and poor caching decisions. This deep dive covers each root cause with before/after code and the exact Spark configs that fix them. Apply these and your Spark jobs will typically run 3-10x faster.",
  "sections": [
    {
      "heading": "Root Cause 1 — Shuffle & Partitioning",
      "content": "3-4 sentences: Shuffles (groupBy, join, distinct, repartition) are the most expensive Spark operation — data moves across the network between executors. The default partition count is 200 (spark.sql.shuffle.partitions) — too few for large data, too many for small data. Rule: aim for 100-200 MB per partition after shuffle. With AQE (Adaptive Query Execution) enabled, Spark auto-tunes partition count.",
      "code": "# WRONG: default 200 shuffle partitions for a 2 TB dataset = 10GB/partition\ndf.groupBy('customer_id').agg(sum('amount'))\n\n# RIGHT: set shuffle partitions based on data size\n# 2 TB / 200 MB target = ~10,000 partitions\nspark.conf.set('spark.sql.shuffle.partitions', '10000')\n\n# BEST: Enable AQE — Spark auto-calculates optimal partitions\nspark.conf.set('spark.sql.adaptive.enabled', 'true')\nspark.conf.set('spark.sql.adaptive.coalescePartitions.enabled', 'true')\nspark.conf.set('spark.sql.adaptive.advisoryPartitionSizeInBytes', '200MB')\n\n# AQE also auto-switches join strategies and handles skew\n# Enable it for every Spark job — it's on by default in Spark 3.2+\n\n# Coalesce small output files (after filter reduces data significantly)\nresult_df = filtered_df.coalesce(10).write.format('delta').save('/mnt/output/')\n# Use coalesce (no shuffle) not repartition (shuffle) when reducing partitions",
      "code_label": "Python — Shuffle partition tuning and AQE configuration"
    },
    {
      "heading": "Root Cause 2 — Data Skew",
      "content": "3-4 sentences: Data skew is when one partition has 100x more data than others — one executor runs for hours while the rest finish in minutes. Diagnose via Spark UI: look for tasks with vastly different durations in the same stage. Fix with AQE skew join hint, salting (add random prefix to join key), or filtering the skewed key and processing separately.",
      "code": "from pyspark.sql.functions import col, rand, concat_ws, floor\n\n# WRONG: join on skewed customer_id — one partition gets 80% of the data\norders.join(customers, 'customer_id', 'left')\n\n# RIGHT Option 1: AQE skew join handling (Spark 3.x with AQE enabled)\nspark.conf.set('spark.sql.adaptive.skewJoin.enabled', 'true')\nspark.conf.set('spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes', '256MB')\n# AQE automatically splits skewed partitions — no code change needed\n\n# RIGHT Option 2: Salting for known skewed key (e.g. customer_id = 'AMAZON')\nSALT = 10  # number of salt buckets\norders_salted = orders.withColumn(\n    'salt_key',\n    concat_ws('_', col('customer_id'), (floor(rand() * SALT)).cast('string'))\n)\ncustomers_exploded = customers.withColumn(\n    'salt_bucket', explode(array([lit(i) for i in range(SALT)]))\n).withColumn('salt_key', concat_ws('_', col('customer_id'), col('salt_bucket').cast('string')))\norders_salted.join(customers_exploded, 'salt_key', 'left').drop('salt_key', 'salt_bucket')",
      "code_label": "Python — AQE skew join and manual salting for data skew"
    },
    {
      "heading": "Root Cause 3 — Wrong Join Strategy",
      "content": "3-4 sentences: Spark chooses sort-merge join by default (requires shuffle of both tables). If the smaller table fits in memory (< 8 MB default, up to 1-2 GB for large clusters), use broadcast join — the small table is broadcast to all executors, eliminating the shuffle entirely. Force broadcast with the broadcast() hint when Spark's auto-detection misses it.",
      "code": "from pyspark.sql.functions import broadcast\n\n# WRONG: sort-merge join — both tables shuffled (expensive)\norders.join(region_lookup, 'region_code', 'left')\n\n# RIGHT: broadcast join — region_lookup (small) broadcast to all executors\norders.join(broadcast(region_lookup), 'region_code', 'left')\n\n# Set broadcast threshold — auto-broadcast tables under this size\nspark.conf.set('spark.sql.autoBroadcastJoinThreshold', '512MB')\n# Databricks with Photon and large clusters: safe up to 2 GB\n\n# Check join strategy in explain():\norders.join(broadcast(region_lookup), 'region_code').explain()\n# Look for BroadcastHashJoin in the plan — confirms broadcast is used\n\n# Disable broadcast for specific joins (if broadcast causes OOM):\norders.join(big_table.hint('SHUFFLE_HASH'), 'key', 'left')",
      "code_label": "Python — Broadcast join vs sort-merge join with explain() verification"
    },
    {
      "heading": "Photon, Caching & Partition Pruning",
      "content": "3-4 sentences: Photon (Databricks-native vectorized execution engine) gives 2-5x speedup on Delta Lake workloads — enable it on the cluster, it's transparent to PySpark code. Cache DataFrames that are reused multiple times in the same job (df.cache()), but unpersist after use to free memory. Partition pruning: always filter on the partition column first so Spark reads only relevant files from Delta — if you filter on a non-partition column, Spark scans everything.",
      "code": "",
      "code_label": ""
    }
  ],
  "cheat_sheet_rows": [
    ["Performance Issue", "Root Cause", "Fix"],
    ["Long shuffle stage", "Too few/many shuffle partitions", "AQE + spark.sql.adaptive.advisoryPartitionSizeInBytes=200MB"],
    ["One slow task in stage", "Data skew on join/group key", "AQE skewJoin.enabled=true or salting"],
    ["Slow large table join", "Sort-merge join instead of broadcast", "broadcast() hint or autoBroadcastJoinThreshold=512MB"],
    ["Full table scan on Delta", "Filter not on partition column", "Add partition column to WHERE clause"],
    ["OOM on executor", "Caching too much, large broadcast", "unpersist() after use, reduce broadcast threshold"],
    ["Slow repeated DataFrame reads", "Recomputing same DataFrame multiple times", "df.cache() then df.unpersist() when done"],
    ["Small file problem", "Too many tiny output files", "coalesce(N) before write or Delta OPTIMIZE"],
    ["Slow aggregation on billions of rows", "No AQE, wrong partition count", "AQE on + shuffle.partitions tuned to data size"],
    ["UDF performance", "Python UDF row-by-row (GIL bound)", "Replace with native Spark SQL functions or pandas_udf"],
    ["Photon not accelerating", "Non-Delta source or unsupported operator", "Use Delta format + check Photon-supported operators"],
    ["Schema mismatch at join", "Column type difference between tables", "Cast to same type before join — avoids implicit cast shuffle"]
  ],
  "key_takeaways": [
    "Enable AQE (spark.sql.adaptive.enabled=true) on every job — it auto-fixes shuffle partitions and skew",
    "Broadcast joins eliminate shuffle — always broadcast the smaller table when it fits in memory",
    "Data skew: use AQE skewJoin detection first; fall back to salting for extreme skew cases",
    "Always filter on Delta partition columns first — Spark skips non-matching files entirely (file pruning)",
    "Cache DataFrames reused multiple times, then unpersist() immediately after — don't leave caches dangling",
    "Replace Python UDFs with native Spark SQL functions — UDFs serialize data row-by-row through the Python GIL",
    "Enable Photon on Databricks — it's a free 2-5x speedup on Delta workloads with zero code changes"
  ],
  "linkedin_caption": "⚡ PySpark Performance — The Deep Dive Your Team Needs!\\n\\nShuffle hell. Data skew. Wrong join strategy. These 3 issues cause 80% of slow Spark jobs — and all 3 have clean fixes.\\n\\nThis Thursday's PDF: AQE configuration, broadcast joins, skew salting, Photon, partition pruning — with before/after code and a full cheat sheet.\\n\\n📥 Download it. Share it with every PySpark developer on your team.\\n\\nWhat's the worst Spark performance problem you've debugged?",
  "hashtags": "#PySpark #Spark #DataEngineering #Databricks #Performance #BigData #DeltaLake #Python #AQE #DataOptimization"
}""",
    },
]


# ── TOPIC ROTATION TRACKER ────────────────────────────────────────────────────
def load_tracker() -> dict:
    if os.path.exists(TRACKER_FILE):
        try:
            with open(TRACKER_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"weekly_tech_used": [], "weekly_tech_last": None}


def save_tracker(data: dict) -> None:
    with open(TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)


def pick_next_topic() -> dict:
    tracker = load_tracker()
    used: list = tracker.get("weekly_tech_used", [])
    all_labels = [t["label"] for t in WEEKLY_TECH_TOPICS]

    # Reset rotation when all topics have been used
    remaining = [t for t in WEEKLY_TECH_TOPICS if t["label"] not in used]
    if not remaining:
        used = []
        remaining = list(WEEKLY_TECH_TOPICS)
        print(f"All {len(WEEKLY_TECH_TOPICS)} topics used — restarting rotation")

    topic = remaining[0]
    used.append(topic["label"])
    tracker["weekly_tech_used"] = used
    tracker["weekly_tech_last"] = topic["label"]
    save_tracker(tracker)

    print(f"Selected topic: {topic['label']}  "
          f"({len(used)}/{len(all_labels)} in current rotation)")
    return topic


# ── GEMINI CONTENT GENERATION ─────────────────────────────────────────────────
GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-pro-latest",
]


def call_gemini(prompt: str) -> dict:
    """Call Gemini API with fallback models, return parsed JSON."""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 4000, "temperature": 0.7},
    }
    for model in GEMINI_MODELS:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={GEMINI_KEY}"
        )
        for attempt in range(1, 3):
            try:
                print(f"Trying {model} — attempt {attempt}/2 …")
                resp = requests.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=90,
                )
                if resp.status_code == 200:
                    raw = (
                        resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                        .strip()
                    )
                    print(f"Generated content with {model} ✓")
                    # Strip markdown fences if present
                    for fence in ("```json", "```"):
                        if raw.startswith(fence):
                            raw = raw[len(fence):]
                    if raw.endswith("```"):
                        raw = raw[:-3]
                    return json.loads(raw.strip())
                if resp.status_code == 429:
                    wait = 65 if attempt == 1 else 0
                    print(f"{model} rate-limited (429) — waiting {wait}s before {'retry' if wait else 'next model'} …")
                    if wait:
                        time.sleep(wait)
                        continue   # retry same model
                    break          # move to next model
                if resp.status_code in (503, 404):
                    print(f"{model} unavailable ({resp.status_code}) — next model …")
                    time.sleep(3)
                    break
                print(f"Gemini error: {resp.status_code} — {resp.text[:200]}")
                break  # unexpected error — try next model
            except requests.exceptions.Timeout:
                print(f"Timeout on {model} attempt {attempt}")
                if attempt == 2:
                    break
                time.sleep(10)
            except json.JSONDecodeError as e:
                print(f"JSON parse failed: {e}")
                raise

    print("All Gemini models failed.")
    sys.exit(1)


# ── PDF STYLES ────────────────────────────────────────────────────────────────
def build_styles():
    base = getSampleStyleSheet()

    def add(name, **kwargs):
        try:
            base.add(ParagraphStyle(name=name, **kwargs))
        except KeyError:
            # Style already defined — update its attributes in place
            existing = base[name]
            for k, v in kwargs.items():
                setattr(existing, k, v)

    add("CoverTitle",
        parent=base["Normal"], fontName="Helvetica-Bold",
        fontSize=22, textColor=C_WHITE, alignment=TA_CENTER,
        spaceAfter=6, leading=26)
    add("CoverSub",
        parent=base["Normal"], fontName="Helvetica",
        fontSize=11, textColor=C_LBLUE, alignment=TA_CENTER,
        spaceAfter=4, leading=14)
    add("CoverDate",
        parent=base["Normal"], fontName="Helvetica-Oblique",
        fontSize=9, textColor=C_GRAY, alignment=TA_CENTER, spaceAfter=0)
    add("SectionHead",
        parent=base["Normal"], fontName="Helvetica-Bold",
        fontSize=13, textColor=C_NAVY, spaceBefore=12, spaceAfter=3, leading=16)
    add("BodyText",
        parent=base["Normal"], fontName="Helvetica",
        fontSize=10, textColor=C_TEXT, leading=14, spaceAfter=6,
        alignment=TA_JUSTIFY)
    add("CodeLabel",
        parent=base["Normal"], fontName="Helvetica-Oblique",
        fontSize=8, textColor=C_GRAY, spaceAfter=2)
    add("CodeText",
        parent=base["Normal"], fontName="Courier",
        fontSize=8, textColor=colors.HexColor("#1A1A1A"), leading=11)
    add("TakeawayItem",
        parent=base["Normal"], fontName="Helvetica",
        fontSize=10, textColor=C_TEXT, leading=14, leftIndent=10, spaceAfter=4)
    add("CheatHead",
        parent=base["Normal"], fontName="Helvetica-Bold",
        fontSize=12, textColor=C_NAVY, spaceBefore=12, spaceAfter=6)
    add("Footer",
        parent=base["Normal"], fontName="Helvetica-Oblique",
        fontSize=8, textColor=C_GRAY, alignment=TA_CENTER)

    return base


# ── PDF ELEMENT BUILDERS ──────────────────────────────────────────────────────
def cover_block(data: dict, styles, col_w: float) -> list:
    """Dark navy cover header rendered as a colored table."""
    title_p  = Paragraph(data.get("title", "Weekly Tech Guide"), styles["CoverTitle"])
    sub_p    = Paragraph(data.get("subtitle", ""), styles["CoverSub"])
    date_str = f"{data.get('week_label', '')}  |  {DATE}"
    date_p   = Paragraph(date_str, styles["CoverDate"])

    tbl = Table([[title_p], [sub_p], [date_p]], colWidths=[col_w])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_NAVY),
        ("TOPPADDING",    (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
        ("LEFTPADDING",   (0, 0), (-1, -1), 20),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 20),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_NAVY]),
    ]))
    return [tbl, Spacer(1, 0.18 * inch)]


def section_heading(text: str, styles) -> list:
    return [
        Paragraph(text, styles["SectionHead"]),
        HRFlowable(width="100%", thickness=0.8, color=C_BLUE, spaceAfter=4),
    ]


def code_block(code: str, label: str, styles, col_w: float) -> list:
    """Render a code snippet with gray background."""
    if not code or not code.strip():
        return []
    elements = []
    if label:
        elements.append(Paragraph(label, styles["CodeLabel"]))
    code_p = Preformatted(code.strip(), styles["CodeText"])
    tbl = Table([[code_p]], colWidths=[col_w])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_CODE_BG),
        ("BOX",           (0, 0), (-1, -1), 0.5, C_CODE_BD),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    elements.append(tbl)
    elements.append(Spacer(1, 0.08 * inch))
    return elements


def cheat_sheet_table(rows: list, styles, col_w: float) -> list:
    """Render the cheat sheet as a styled table."""
    if not rows:
        return []
    n_cols = len(rows[0])

    # Distribute column widths
    if n_cols == 3:
        col_widths = [col_w * 0.28, col_w * 0.38, col_w * 0.34]
    elif n_cols == 4:
        col_widths = [col_w * 0.22, col_w * 0.28, col_w * 0.28, col_w * 0.22]
    else:
        col_widths = [col_w / n_cols] * n_cols

    # Convert cells to Paragraphs
    body_style = ParagraphStyle(
        "CheatCell", fontName="Helvetica", fontSize=8.5,
        textColor=C_TEXT, leading=11
    )
    header_style = ParagraphStyle(
        "CheatHeaderCell", fontName="Helvetica-Bold", fontSize=9,
        textColor=C_WHITE, leading=12
    )
    table_data = []
    for r_idx, row in enumerate(rows):
        st = header_style if r_idx == 0 else body_style
        table_data.append([Paragraph(str(cell), st) for cell in row])

    tbl = Table(table_data, colWidths=col_widths, repeatRows=1)

    # Alternating row colors
    style_cmds = [
        ("BACKGROUND",    (0, 0), (-1, 0),   C_BLUE),
        ("TEXTCOLOR",     (0, 0), (-1, 0),   C_WHITE),
        ("BOX",           (0, 0), (-1, -1),  0.5, C_BLUE),
        ("INNERGRID",     (0, 0), (-1, -1),  0.25, C_LBLUE),
        ("TOPPADDING",    (0, 0), (-1, -1),  5),
        ("BOTTOMPADDING", (0, 0), (-1, -1),  5),
        ("LEFTPADDING",   (0, 0), (-1, -1),  6),
        ("RIGHTPADDING",  (0, 0), (-1, -1),  6),
        ("VALIGN",        (0, 0), (-1, -1),  "TOP"),
    ]
    for r_idx in range(1, len(rows)):
        if r_idx % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, r_idx), (-1, r_idx), C_STRIPE))

    tbl.setStyle(TableStyle(style_cmds))
    return [tbl, Spacer(1, 0.15 * inch)]


def takeaways_block(items: list, styles, col_w: float) -> list:
    """Render key takeaways in a green-tinted box."""
    if not items:
        return []

    header = Paragraph("✅  Key Takeaways", ParagraphStyle(
        "TakeHeader", fontName="Helvetica-Bold", fontSize=11,
        textColor=C_GREEN, spaceAfter=6
    ))
    item_style = ParagraphStyle(
        "TakeItem", fontName="Helvetica", fontSize=9.5,
        textColor=C_TEXT, leading=14, leftIndent=4
    )
    rows = [[header]]
    for item in items:
        rows.append([Paragraph(f"▸  {item}", item_style)])

    tbl = Table(rows, colWidths=[col_w])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_GBKG if False else C_GBG),
        ("BOX",           (0, 0), (-1, -1), 0.75, C_GREEN),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    return [tbl, Spacer(1, 0.12 * inch)]


# ── MAIN PDF BUILDER ──────────────────────────────────────────────────────────
def create_pdf(data: dict) -> bytes:
    """Build the complete 3-4 page PDF and return bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
    )
    styles  = build_styles()
    col_w   = letter[0] - 1.5 * inch   # usable content width
    story   = []

    # ── Cover ──────────────────────────────────────────────────────────────
    story += cover_block(data, styles, col_w)

    # ── Introduction ───────────────────────────────────────────────────────
    intro = data.get("introduction", "")
    if intro:
        story.append(Paragraph(intro, styles["BodyText"]))
        story.append(Spacer(1, 0.1 * inch))

    # ── Sections ───────────────────────────────────────────────────────────
    for sec in data.get("sections", []):
        heading  = sec.get("heading", "")
        content  = sec.get("content", "")
        code     = sec.get("code", "")
        code_lbl = sec.get("code_label", "")

        story += section_heading(heading, styles)
        if content:
            story.append(Paragraph(content, styles["BodyText"]))
        story += code_block(code, code_lbl, styles, col_w)
        story.append(Spacer(1, 0.05 * inch))

    # ── Cheat Sheet (new page) ──────────────────────────────────────────────
    story.append(PageBreak())
    cs_title = data.get("cheat_sheet_title",
                        data.get("title", "Quick Reference") + " — Cheat Sheet")
    story.append(Paragraph(cs_title, styles["CheatHead"]))
    story += cheat_sheet_table(data.get("cheat_sheet_rows", []), styles, col_w)

    # ── Key Takeaways ──────────────────────────────────────────────────────
    story += takeaways_block(data.get("key_takeaways", []), styles, col_w)

    # ── Footer ─────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.1 * inch))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_GRAY))
    story.append(Spacer(1, 0.04 * inch))
    hashtags = data.get("hashtags", "#DataEngineering")
    story.append(Paragraph(
        f"📌  Follow for weekly data engineering deep dives every Thursday 7 PM IST  |  {hashtags}",
        styles["Footer"]
    ))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


# ── LINKEDIN PDF UPLOAD & POST ────────────────────────────────────────────────
def post_pdf_to_linkedin(pdf_bytes: bytes, data: dict) -> None:
    """Register upload, upload PDF, create LinkedIn post using new REST API."""
    headers = {
        "Authorization": f"Bearer {LINKEDIN_TOKEN}",
        "LinkedIn-Version": "202604",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
    }

    # Step 1 — Initialize upload (new REST API)
    print("Step 1: Initializing PDF upload with LinkedIn …")
    resp = requests.post(
        "https://api.linkedin.com/rest/documents?action=initializeUpload",
        headers=headers,
        json={"initializeUploadRequest": {"owner": PERSON_URN}},
        timeout=30,
    )
    if resp.status_code != 200:
        print(f"Initialize upload failed: {resp.status_code} — {resp.text}")
        sys.exit(1)

    upload_url = resp.json()["value"]["uploadUrl"]
    document_urn = resp.json()["value"]["document"]
    print(f"Upload initialized. Document URN: {document_urn}")

    # Step 2 — Upload PDF binary
    print("Step 2: Uploading PDF …")
    resp = requests.put(
        upload_url,
        headers={"Content-Type": "application/octet-stream"},
        data=pdf_bytes,
        timeout=120,
    )
    if resp.status_code not in (200, 201):
        print(f"PDF upload failed: {resp.status_code} — {resp.text}")
        sys.exit(1)
    print("PDF uploaded ✓")

    # Step 3 — Create the LinkedIn post using new REST posts API
    print("Step 3: Creating LinkedIn post …")
    caption = data.get("linkedin_caption", "New weekly data engineering guide! 📥")
    post_payload = {
        "author": PERSON_URN,
        "commentary": caption,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": []
        },
        "content": {
            "media": {
                "title": data.get("title", "Weekly Tech Guide"),
                "id": document_urn
            }
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False
    }
    resp = requests.post(
        "https://api.linkedin.com/rest/posts",
        headers=headers,
        json=post_payload,
        timeout=30,
    )
    if resp.status_code == 201:
        print("✅ SUCCESS — Weekly Tech PDF posted to LinkedIn!")
    else:
        print(f"Post failed: {resp.status_code} — {resp.text}")
        sys.exit(1)


# ── ENTRY POINT ───────────────────────────────────────────────────────────────
def main():
    # 1. Pick next topic from rotation
    topic = pick_next_topic()
    print(f"\n{'='*60}\nTOPIC: {topic['label']}\n{'='*60}\n")

    # 2. Generate content via Gemini
    print("Generating PDF content with Gemini AI …")
    data = call_gemini(topic["prompt"])
    print(f"Content ready — Title: {data.get('title', 'N/A')}")

    # 3. Build PDF
    print("\nBuilding PDF with ReportLab …")
    pdf_bytes = create_pdf(data)
    print(f"PDF created — {len(pdf_bytes):,} bytes")

    # 4. Post to LinkedIn
    post_pdf_to_linkedin(pdf_bytes, data)
    print(f"\nDone — {topic['label']} posted on {DATE}")


if __name__ == "__main__":
    main()
