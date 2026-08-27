import os
import requests
from flask import Blueprint, request, jsonify
from utils.decorators import token_required
from models.student import StudentProfile
from models.drive import PlacementDrive
from models.company import CompanyProfile

ai_bp = Blueprint('ai', __name__)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "meta-llama/llama-3-8b-instruct:free"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

def query_gemini(messages, max_tokens=1000):
    if not GEMINI_API_KEY:
        return "AI features are currently unavailable (Missing API Keys for both OpenRouter and Gemini)."
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    contents = []
    system_instruction = None
    
    for m in messages:
        role = m['role']
        if role == 'system':
            system_instruction = {"parts": [{"text": m['content']}]}
        else:
            gemini_role = "user" if role == "user" else "model"
            contents.append({
                "role": gemini_role,
                "parts": [{"text": m['content']}]
            })
            
    payload = {
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.7
        }
    }
    
    if system_instruction:
        payload["systemInstruction"] = system_instruction
        
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Sorry, the AI service encountered an error and the fallback also failed."

def query_ai(messages, max_tokens=1000):
    if OPENROUTER_API_KEY:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://placement-portal.local", 
            "X-Title": "Placement Portal App"
        }
        payload = {
            "model": DEFAULT_MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        try:
            response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=20)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
        except Exception as e:
            print(f"OpenRouter failed: {e}. Falling back to Gemini...")
    
    # Fallback to Gemini if OpenRouter fails or key is missing
    return query_gemini(messages, max_tokens)

@ai_bp.route('/api/ai/mock-interview', methods=['POST'])
@token_required
def mock_interview():
    data = request.get_json(silent=True) or {}
    interview_type = data.get('type', 'HR')
    student_branch = data.get('branch', 'General')
    student_skills = data.get('skills', 'None')
    chat_history = data.get('history', [])
    
    system_prompt = f"""You are an expert {interview_type} interviewer at a top-tier tech company.
The candidate is a student studying {student_branch} with the following skills: {student_skills}.
Conduct a realistic {interview_type} interview. Ask one question at a time, wait for the candidate's answer, and then provide brief, constructive feedback before asking the next question. Keep your responses under 100 words per turn. Be professional, slightly challenging, but encouraging."""

    messages = [{"role": "system", "content": system_prompt}]
    
    # Add history
    for msg in chat_history[-10:]: # keep last 10 msgs to avoid context limits
        messages.append({"role": msg['role'], "content": msg['content']})
        
    reply = query_ai(messages)
    return jsonify({"reply": reply})

@ai_bp.route('/api/ai/analyze-resume', methods=['POST'])
@token_required
def analyze_resume():
    data = request.get_json(silent=True) or {}
    student_id = data.get('student_id')
    drive_id = data.get('drive_id')
    
    student = StudentProfile.query.get(student_id)
    drive = PlacementDrive.query.get(drive_id)
    
    if not student or not drive:
        return jsonify({'error': 'Student or Drive not found'}), 404
        
    company = CompanyProfile.query.get(drive.company_id)
    company_name = company.company_name if company else "Unknown Company"
    
    student_profile_text = f"Branch: {student.branch}\nSkills: {student.skills}\nProjects: {student.projects}\nExperience: {student.experience}"
    job_description_text = f"Title: {drive.job_title}\nCompany: {company_name}\nDescription: {drive.job_description}\nRequired Skills: {drive.required_skills}"
    
    prompt = f"""You are an expert Career Counselor and ATS AI analyzer. 
Review the following Student Profile against the Job Description.

Student Profile:
{student_profile_text}

Job Description:
{job_description_text}

Provide a concise "Resume Gap Analysis". 
1. State the strengths of the candidate for this role.
2. Identify exactly what skills or experiences are missing from the student's profile compared to the job requirements.
3. Provide 3 highly actionable tips on what the student should quickly brush up on or learn before the interview.
Keep the formatting clean using Markdown."""

    messages = [{"role": "user", "content": prompt}]
    reply = query_ai(messages, max_tokens=1500)
    
    return jsonify({"analysis": reply})

@ai_bp.route('/api/ai/support-bot', methods=['POST'])
@token_required
def support_bot():
    data = request.get_json(silent=True) or {}
    message = data.get('message', '')
    history = data.get('history', [])
    
    system_prompt = """You are the Placement Portal AI Support Bot. 
You help students and companies navigate the web application. 
Key Features of the portal:
- Students can update their profile (skills, projects, experience, upload digital signature) in the 'My Profile' tab.
- Students can browse active placement drives, apply, and view status in the 'My Applications' tab.
- Students can export their auto-generated PDF resumes.
- Companies can post drives, review applications (sorted by AI Match Score), shortlist candidates, schedule interviews (which sends .ics calendar invites), and send test links.
- Everyone can use the real-time chat in the 'Messages' tab.
Keep answers extremely concise, helpful, and friendly."""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-5:]:
        messages.append({"role": msg['role'], "content": msg['content']})
        
    messages.append({"role": "user", "content": message})
    
    reply = query_ai(messages, max_tokens=300)
    return jsonify({"reply": reply})
