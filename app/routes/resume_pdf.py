from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from dotenv import load_dotenv
import os, json, io, re
from groq import Groq
from pdfminer.high_level import extract_text

router = APIRouter()

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@router.post("/upgrade/resume_pdf")
async def upgrade_resume_pdf(
    file: UploadFile = File(...),
    current_role: str = Form(...),
    target_role: str = Form(...),
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Validate file size (limit to 10MB for serverless)
    file_content = await file.read()
    if len(file_content) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
    
    # Reset file pointer and read content
    await file.seek(0)
    file_content = await file.read()
    
    # Create a BytesIO object for serverless processing
    pdf_file = io.BytesIO(file_content)
    
    try:
        # Extract text directly from memory without saving to disk
        text = extract_text(pdf_file)
        if not text.strip():
            raise HTTPException(status_code=400, detail="PDF file is empty or not readable.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")
    finally:
        # Clean up memory
        pdf_file.close()

    
    user_prompt = f"""
RESUME_TEXT:
\"\"\"
{text}
\"\"\"

CURRENT_ROLE: \"{current_role}\"
TARGET_ROLE:  \"{target_role}\"
"""

    # LLM call
    completion = client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an elite ATS evaluator, LaTeX résumé re-writer, and project mentor.\n\n"
                    "INPUT\n------\n"
                    "RESUME_TEXT: (see user message)\n"
                    "CURRENT_ROLE: (see user message)\n"
                    "TARGET_ROLE:  (see user message)\n\n"
                    "TASKS\n"
                    "1. Evaluate how well the résumé matches the CURRENT_ROLE and return an integer 0-100 in the key \"current_ats_score\".\n"
                    "2. List 5 actionable improvements that would raise the candidate’s chances of landing the TARGET_ROLE. Return these in the key \"suggestions\" (array of strings).\n"
                    "3. Suggest 3 unique, advanced, and portfolio-worthy project ideas that are highly relevant to the TARGET_ROLE. For each project, provide:\n   - A creative, descriptive project title\n   - A concise 2-3 line description focused on real-world impact or innovation\n   - The most in-demand technologies, frameworks, or skills for the target role\n   - A one-line explanation of how this project will impress recruiters for the TARGET_ROLE\nReturn these in the key \"project_ideas\" (array of objects).\n"
                    "4. Rewrite the résumé in compile-ready LaTeX, fully tailored to the TARGET_ROLE, and return the code in the key \"modified_latex\".  \n"
                    "   • Use the article class with `hyperref` and `enumitem`.  \n"
                    "   • Keep it one column, bullet-driven, keyword-rich, and Overleaf-compatible.  \n"
                    "5. Estimate the résumé’s ATS score **after** your modifications and return it in \"target_ats_score\".\n"
                    "   - IMPORTANT: The target_ats_score must always be strictly greater than the current_ats_score. If not, revise your suggestions and LaTeX until this is true.\n\n"
                    "OUTPUT FORMAT  \nRespond **exactly** with this JSON object—no extra keys, markdown, or prose:\n\n"
                    "{\n  \"current_ats_score\": <integer>,\n  \"target_ats_score\":  <integer>,\n  \"suggestions\": [\"<string>\", \"...\"],\n  \"project_ideas\": [\n    {\"title\": \"<string>\", \"description\": \"<string>\", \"technologies\": [\"<string>\", ...], \"recruiter_impact\": \"<string>\"},\n    ...\n  ],\n  \"modified_latex\": \"<string>\"\n}\n"
                )
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0.6,
        max_completion_tokens=4096,
        top_p=0.95,
        stream=False,
        stop=None,
    )

    
    try:
        response = completion.choices[0].message.content
        # Fallback: extract JSON object from any extra text using regex
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            response = json_match.group(0)
        
        # Double-escape backslashes in the LaTeX string for valid JSON
        def escape_latex_in_json(s):
            return re.sub(
                r'("modified_latex"\s*:\s*")((?:[^"\\]|\\.)*)(")',
                lambda m: m.group(1) + m.group(2).replace("\\", "\\\\") + m.group(3),
                s,
                flags=re.DOTALL
            )
        response = escape_latex_in_json(response)
        result = json.loads(response)
        
        # Validate that all required keys are present
        required_keys = ["current_ats_score", "target_ats_score", "suggestions", "modified_latex"]
        missing = [k for k in required_keys if k not in result]
        if missing:
            raise HTTPException(status_code=500, detail=f"Missing keys in LLM response: {missing}")
        
        # Validate ATS scores
        if not isinstance(result["current_ats_score"], int) or not isinstance(result["target_ats_score"], int):
            raise HTTPException(status_code=500, detail="ATS scores must be integers")
        
        if result["target_ats_score"] <= result["current_ats_score"]:
            raise HTTPException(status_code=500, detail="Target ATS score must be higher than current score")
        
        return result
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response from LLM: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing LLM response: {str(e)}")
    finally:
        # Clean up any remaining resources
        if 'pdf_file' in locals():
            pdf_file.close()