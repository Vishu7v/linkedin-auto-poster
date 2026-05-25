# ─────────────────────────────────────────────────────────────
# post_pdf_qa.py — LinkedIn PDF Q&A Poster using Gemini + ReportLab
# Posts Q&A PDFs twice per week (Tuesday & Friday)
# Uses reportlab to create beautiful PDFs
# ─────────────────────────────────────────────────────────────
import requests, os, sys, json, time, io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# ── CREDENTIALS ───────────────────────────────────────────────
LINKEDIN_TOKEN = os.environ.get("LINKEDIN_TOKEN")
PERSON_URN     = os.environ.get("PERSON_URN")
GEMINI_KEY     = os.environ.get("GEMINI_KEY")

print(f"LinkedIn PDF Q&A Poster starting - {datetime.now():%A, %d %B %Y %H:%M}")
print("-" * 50)

# ── GENERATE Q&A CONTENT WITH GEMINI ──────────────────────────
def generate_qa_content() -> dict:
    """Generate Q&A content for PDF"""
    
    prompt = """Generate a comprehensive Q&A guide for data engineers with real-world problems.

Format the response as ONLY valid JSON (no markdown, no backticks, no explanation):
{
    "title": "Data Engineering Interview Guide - [specific topic]",
    "week": "Week of [date]",
    "topic": "[Main Topic]",
    "description": "[1-2 line description]",
    "questions": [
        {
            "question": "Q1: [specific technical question]",
            "answer": "[detailed answer with reasoning]",
            "code_snippet": "[relevant code or pseudocode if applicable]",
            "real_world": "[Real-world scenario where this matters]",
            "difficulty": "Intermediate"
        },
        {
            "question": "Q2: [another specific technical question]",
            "answer": "[detailed answer with reasoning]",
            "code_snippet": "[relevant code or pseudocode if applicable]",
            "real_world": "[Real-world scenario where this matters]",
            "difficulty": "Advanced"
        },
        {
            "question": "Q3: [practical problem statement]",
            "answer": "[detailed answer with reasoning]",
            "code_snippet": "[relevant code or pseudocode if applicable]",
            "real_world": "[Real-world scenario where this matters]",
            "difficulty": "Intermediate"
        }
    ]
}

Topics to choose from (pick ONE):
- Spark Performance Optimization
- Incremental Data Load Patterns
- Data Quality & Validation Strategies
- Handling Late-Arriving Data
- Pipeline Idempotency Design
- Schema Evolution in Data Lakes
- Cost Optimization in Cloud Data Platforms
- Error Handling & Retry Logic
- Stream Processing vs Batch
- Data Lineage & Observability

Make answers practical, not theoretical. Include code when relevant.
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 8192,
            "temperature": 0.7
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
                    text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                    print(f"Generated Q&A content using {model}")

                    # Strip markdown fences (```json, ```, etc.)
                    import re
                    json_str = re.sub(r'^```(?:json)?\s*', '', text, flags=re.IGNORECASE)
                    json_str = re.sub(r'\s*```$', '', json_str).strip()

                    # Parse JSON response
                    try:
                        qa_data = json.loads(json_str)
                        return qa_data
                    except json.JSONDecodeError:
                        # Gemini returned truncated JSON — trim to last complete question
                        print("JSON parse failed, attempting recovery...")
                        # Find last complete closing brace for a question object
                        last_good = json_str.rfind('},\n        {')
                        if last_good == -1:
                            last_good = json_str.rfind('},')
                        if last_good != -1:
                            trimmed = json_str[:last_good + 1] + "\n    ]\n}"
                            try:
                                qa_data = json.loads(trimmed)
                                print("JSON recovered successfully")
                                return qa_data
                            except json.JSONDecodeError:
                                pass
                        print(f"JSON recovery failed, trying next model...")
                        break
                        
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
                    break
                time.sleep(10)

    print("All models failed. Exiting.")
    sys.exit(1)

# ── CREATE PDF FROM Q&A DATA ──────────────────────────────────
def create_qa_pdf(qa_data: dict) -> bytes:
    """Create a beautiful PDF from Q&A data using ReportLab"""
    
    # Create PDF in memory
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#003366'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#006699'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    question_style = ParagraphStyle(
        'Question',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#003366'),
        spaceAfter=6,
        spaceBefore=6,
        fontName='Helvetica-Bold'
    )
    
    answer_style = ParagraphStyle(
        'Answer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=4,
        leftIndent=20,
        alignment=TA_JUSTIFY
    )
    
    # Title
    story.append(Paragraph(qa_data.get('title', 'Data Engineering Q&A'), title_style))
    story.append(Paragraph(f"<i>{qa_data.get('week', '')}</i>", styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))
    
    # Description
    if qa_data.get('description'):
        story.append(Paragraph(qa_data['description'], styles['Normal']))
        story.append(Spacer(1, 0.15 * inch))
    
    # Questions
    for idx, q in enumerate(qa_data.get('questions', []), 1):
        # Question
        story.append(Paragraph(
            f"<b>Q{idx}: {q.get('question', '').replace('Q' + str(idx) + ': ', '')}</b>",
            question_style
        ))
        
        # Difficulty badge
        difficulty = q.get('difficulty', 'Intermediate')
        difficulty_color = {
            'Beginner': '#90EE90',
            'Intermediate': '#FFD700',
            'Advanced': '#FF6347'
        }.get(difficulty, '#FFD700')
        story.append(Paragraph(
            f"<font color='{difficulty_color}'><i>Difficulty: {difficulty}</i></font>",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.05 * inch))
        
        # Answer
        answer_text = q.get('answer', '').replace('\n', '<br/>')
        story.append(Paragraph(answer_text, answer_style))
        story.append(Spacer(1, 0.08 * inch))
        
        # Code snippet if available
        if q.get('code_snippet'):
            code_text = q['code_snippet'].replace('\n', '<br/>')
            story.append(Paragraph("<b>Code Example:</b>", styles['Normal']))
            story.append(Paragraph(
                f"<font name='Courier' size='9'><i>{code_text}</i></font>",
                styles['Normal']
            ))
            story.append(Spacer(1, 0.08 * inch))
        
        # Real-world scenario
        if q.get('real_world'):
            real_world_text = q['real_world'].replace('\n', '<br/>')
            story.append(Paragraph(
                f"<b>🔍 Real-World:</b> <i>{real_world_text}</i>",
                styles['Normal']
            ))
        
        story.append(Spacer(1, 0.15 * inch))
        
        # Page break after every 2 questions
        if idx % 2 == 0 and idx < len(qa_data.get('questions', [])):
            story.append(PageBreak())
    
    # Footer
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(
        "<i>📌 Save this guide for your next interview prep session!</i>",
        styles['Normal']
    ))
    
    # Build PDF
    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

# ── POST PDF TO LINKEDIN ──────────────────────────────────────
def post_pdf_to_linkedin(pdf_bytes: bytes, qa_data: dict):
    """Upload PDF as document and post to LinkedIn using new REST API"""

    print("Uploading PDF to LinkedIn...")

    headers = {
        "Authorization": f"Bearer {LINKEDIN_TOKEN}",
        "LinkedIn-Version": "202501",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
    }

    # Step 1: Initialize upload (new REST API)
    print("Step 1: Initializing PDF upload...")
    resp = requests.post(
        "https://api.linkedin.com/rest/documents?action=initializeUpload",
        headers=headers,
        json={"initializeUploadRequest": {"owner": PERSON_URN}},
        timeout=30
    )
    if resp.status_code != 200:
        print(f"Failed to initialize upload: {resp.status_code} - {resp.text}")
        sys.exit(1)

    upload_url = resp.json()["value"]["uploadUrl"]
    document_urn = resp.json()["value"]["document"]
    print(f"Upload initialized. Document URN: {document_urn}")

    # Step 2: Upload PDF binary
    print("Step 2: Uploading PDF file...")
    resp = requests.put(
        upload_url,
        headers={"Content-Type": "application/octet-stream"},
        data=pdf_bytes,
        timeout=120
    )
    if resp.status_code not in [200, 201]:
        print(f"Failed to upload PDF: {resp.status_code} - {resp.text}")
        sys.exit(1)
    print("PDF uploaded successfully")

    # Step 3: Create post with new REST posts API
    print("Step 3: Creating LinkedIn post with PDF...")
    post_text = f"""📚 {qa_data.get('title', 'New Q&A Guide')}

{qa_data.get('description', '')}

This week's guide covers {qa_data.get('topic', 'important data engineering concepts')} with real-world scenarios and technical depth.

Perfect for interview prep or leveling up your skills! 🚀

#DataEngineering #InterviewPrep #SQL #PySpark #DataPipelines #CareerGrowth"""

    post_payload = {
        "author": PERSON_URN,
        "commentary": post_text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": []
        },
        "content": {
            "media": {
                "title": qa_data.get('title', 'Data Engineering Q&A'),
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
        timeout=30
    )
    if resp.status_code == 201:
        print("✅ SUCCESS - PDF Posted to LinkedIn!")
    else:
        print(f"LinkedIn failed: {resp.status_code} - {resp.text}")
        sys.exit(1)

# ── MAIN ──────────────────────────────────────────────────────
if __name__ == "__main__":
    qa_data = generate_qa_content()

    print("\n" + "=" * 50)
    print(f"GENERATED Q&A: {qa_data.get('title', 'New Q&A Guide')}")
    print(f"Topic: {qa_data.get('topic', 'Data Engineering')}")
    print(f"Questions: {len(qa_data.get('questions', []))}")
    print("=" * 50 + "\n")

    pdf_bytes = create_qa_pdf(qa_data)
    print(f"PDF created: {len(pdf_bytes)} bytes")

    post_pdf_to_linkedin(pdf_bytes, qa_data)

    print("Done! PDF posted to LinkedIn.")
