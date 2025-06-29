from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
import os

router = APIRouter()
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class User_Input(BaseModel):
    interest: str

class Topic(BaseModel):
    topic: str

class RoadMap(BaseModel):
    goal: str


@router.post("/career")
async def get_career_suggestion(user_input: User_Input):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a career advisor AI trained to help individuals discover suitable career paths based on their interests, strengths, and goals.\n\n"
                    f"Input from user:\n{user_input.interest}\n\n"
                    "Based on the input, suggest 3 potential career options. For each suggestion:\n"
                    "- Name the career.\n"
                    "- Explain in 2-3 lines why it is a good fit.\n"
                    "- Mention one potential future opportunity or growth in that field.\n\n"
                    "Ensure your recommendations are realistic, encouraging, and tailored to the user's described interests or background."
                )
            },
            {
                "role": "user",
                "content": f"My interests are {user_input.interest}. Please provide detailed career suggestions."
            }
        ],
        temperature=0.9,
        max_completion_tokens=1024,
        top_p=1,
        stream=True,
    )
    suggestion = ""
    for chunk in completion:
        if hasattr(chunk.choices[0].delta, "content") and chunk.choices[0].delta.content:
            suggestion += chunk.choices[0].delta.content
    # Filter out any system prompt or system information from the response
    filtered = "\n".join(
        line for line in suggestion.splitlines()
        if not any(word in line.lower() for word in ["system prompt", "system:", "prompt:", "role:", "as a system", "as an ai", "you are a system", "model:"])
    )
    return {"suggestion": filtered.strip()}


@router.post("/roadmap")
async def get_roadmap(user_input: RoadMap):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional career roadmap advisor.\n\n"
                    f"User goal:\n{user_input.goal}\n\n"
                    "Instructions:\n"
                    "- Break the roadmap into **3 weekly modules**.\n"
                    "- For each week, include:\n"
                    "  - Clear objectives\n"
                    "  - Key skills/topics\n"
                    "  - Recommended resources with URLs\n"
                    "- Be motivational and beginner-friendly.\n"
                    "Only return the roadmap."
                )
            },
            {
                "role": "user",
                "content": f"I want a roadmap for {user_input.goal}."
            }
        ],
        temperature=0.9,
        max_completion_tokens=1024,
        top_p=1,
    )
    result = completion.choices[0].message.content
    filtered = "\n".join(
        line for line in result.splitlines()
        if not any(word in line.lower() for word in ["system prompt", "system:", "prompt:", "role:", "as a system", "as an ai", "you are a system", "model:"])
    )
    return {"roadmap": filtered.strip()}


@router.post("/resource")
async def resource_find(user_input: Topic):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a resource recommendation engine trained to help learners find high-quality materials.\n\n"
                    f"User query:\n{user_input.topic}\n\n"
                    "Suggest 3 top resources:\n"
                    "- Only suggest the names of YouTube playlists or courses, do not provide any URLs.\n"
                    "- For each resource, include: title, topic, platform (e.g., YouTube, Coursera), a short description, and a review/testimonial.\n"
                    "Ensure all resources are relevant and beginner-friendly."
                )
            },
            {
                "role": "user",
                "content": f"Find resources for {user_input.topic}."
            }
        ],
        temperature=0.9,
        max_completion_tokens=1024,
        top_p=1,
    )
    # Filter out any system prompt or system information from the response
    result = completion.choices[0].message.content
    # Remove lines that look like system prompts or contain 'system', 'prompt', or similar keywords
    filtered = "\n".join(
        line for line in result.splitlines()
        if not any(word in line.lower() for word in ["system prompt", "system:", "prompt:", "role:", "as a system", "as an ai", "you are a system", "model:"])
    )
    return {"resources": filtered.strip()}
