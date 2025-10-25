# This is the code for: backend/main_server.py

import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import httpx 
import asyncio
from contextlib import asynccontextmanager
import os # NEW: To load environment variables

# --- NEW: Imports for Gemini ---
import google.generativeai as genai
from dotenv import load_dotenv # NEW: To load .env file

# --- NEW: Load .env file ---
# This reads your .env file and makes the API key available
load_dotenv()

# --- NEW: Global state for Gemini Model ---
gemini_model = None

# --- NEW: Startup Event to Load Model ---
# This runs once when you start the server
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading Google Gemini model...")
    global gemini_model
    
    # --- NEW: Configure Gemini API Key ---
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not found in .env file.")
        # You could raise an exception here to stop the server
    else:
        genai.configure(api_key=api_key)
        
        # --- NEW: Initialize the model ---
        # Using 1.5-flash for speed, which is good for chat
        gemini_model = genai.GenerativeModel('models/gemini-pro-latest')
        print("Gemini model loaded. Server is ready.")
    
    yield
    # Code to run on shutdown (if any)
    print("Server shutting down.")


# --- Configuration ---
app = FastAPI(
    title="AI Dermatologist App Server (M4)",
    description="Handles business logic, enrichment, and chat.",
    lifespan=lifespan # NEW: Use the startup/shutdown handler
)

# --- CORS ---
origins = ["http://localhost:3000", "http://localhost"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- (Pydantic Models are unchanged) ---
class ChatRequest(BaseModel):
    message: str
    context: str | None = None

class ChatResponse(BaseModel):
    reply: str

class TriageResponse(BaseModel):
    condition: str
    confidence: float


# --- (Root Endpoint is unchanged) ---
@app.get("/")
def read_root():
    return {"status": "AI App Server is running"}


# --- (Quick Analysis Endpoint is unchanged) ---
@app.post("/analyze/quick", response_model=TriageResponse)
async def quick_analysis(image: UploadFile = File(...)):
    print(f"Received image: {image.filename}. Running mock analysis...")
    await asyncio.sleep(1.5)
    mock_conditions = [
        {"condition": "Eczema", "confidence": 0.71},
        {"condition": "Psoriasis", "confidence": 0.88}
    ]
    # Randomly pick one for testing
    mock_data = mock_conditions[1] # Forcing Psoriasis for test
    if (mock_data["condition"] == "Eczema"):
        mock_data = mock_conditions[0]
    
    print("Mock analysis complete. Sending response.")
    return TriageResponse(**mock_data)


@app.post("/chat", response_model=ChatResponse)
async def handle_chat(request: ChatRequest):
    """
    --- MODIFIED: This function now calls the Gemini API ---
    """
    global gemini_model
    user_message = request.message
    context = request.context or "an un-analyzed image" # Default context

    print(f"Chat message received: '{user_message}' with context: '{context}'")

    if not gemini_model:
        raise HTTPException(status_code=500, detail="Gemini model is not initialized. Check API key.")

    # --- NEW: Prompt Engineering ---
    # This is how we make the bot smart and safe.
    # We give it a role, rules, and context.
    # Inside the handle_chat function

    # --- NEW: More Focused Prompt Engineering ---
    system_prompt = (
        "You are DermaAI, an AI assistant for a dermatology app. You are NOT a doctor. "
        "Your purpose is to answer the user's *specific question* with general, educational information about skin conditions. "
        "Always recommend consulting a healthcare professional for diagnosis and treatment."
        "Keep answers concise and directly related to the user's question."
        "**ABSOLUTELY DO NOT answer any questions unrelated to the skin condition context.** This includes math problems, general knowledge, creative writing, or any other topic. "
        "If the user asks an off-topic question, politely state that you can only discuss the provided skin condition analysis and cannot answer unrelated questions. "
    )

    # Handle simple greetings/closings directly without context overload
    simple_reply = None
    if user_message.lower() in ['hi', 'hello', 'hey', 'greetings']:
        simple_reply = "Hello! How can I help you today regarding your analysis?"
    elif user_message.lower() in ['thanks', 'thank you', 'ok thanks', 'bye']:
        simple_reply = "You're welcome! Remember to consult a doctor for any medical concerns."

    if simple_reply:
        reply = simple_reply
        print(f"Handling simple message directly: '{reply}'")
    else:
        # If it's not a simple greeting, build the full prompt for Gemini
        full_prompt = (
            f"{system_prompt}\n\n"
            f"CONTEXT: The preliminary analysis result is '{context}'.\n"
            f"USER'S SPECIFIC QUESTION: '{user_message}'\n\n"
            f"INSTRUCTIONS: Answer *only* the user's specific question concisely, using the context '{context}' if relevant. "
            f"Do NOT give a general overview of '{context}' unless explicitly asked (e.g., 'Tell me about Psoriasis'). "
            f"If discussing treatments/remedies, mention only general categories (like moisturizers, OTC types if applicable, lifestyle) and strongly emphasize consulting a doctor. Do not suggest prescriptions or dosages. "
            f"Use Markdown for formatting (headings `##`, bullets `- `) if needed for clarity on complex answers, but keep it minimal for simple questions."
        )

        try:
            # --- Call the Gemini API ---
            print("Sending focused prompt to Gemini...")
            # Make sure gemini_model is initialized before calling this
            if not gemini_model:
                 raise HTTPException(status_code=500, detail="Gemini model is not initialized.")

            response = await gemini_model.generate_content_async(full_prompt)
            reply = response.text
            print(f"Gemini reply received: '{reply[:50]}...'")

        except Exception as e:
            print(f"ERROR: Gemini API call failed: {e}")
            raise HTTPException(status_code=500, detail="Error communicating with the AI model.")

    # --- Return the reply (either simple or from Gemini) ---
    return ChatResponse(reply=reply)

# Make sure this return is outside the try/except block if it was moved
# This part below should NOT be inside the handle_chat function, it's the server run command

# # --- Run the server ---
# if __name__ == "__main__":
#  print("Starting FastAPI server on http://localhost:8001...")
#  uvicorn.run("main_server:app", host="0.0.0.0", port=8001, reload=True)

    try:
        # --- NEW: Call the Gemini API ---
        print("Sending prompt to Gemini...")
        response = await gemini_model.generate_content_async(full_prompt)
        
        reply = response.text
        print(f"Gemini reply received: '{reply[:50]}...'")
        
        return ChatResponse(reply=reply)

    except Exception as e:
        print(f"ERROR: Gemini API call failed: {e}")
        raise HTTPException(status_code=500, detail="Error communicating with the AI model.")


# --- Run the server ---
if __name__ == "__main__":
    print("Starting FastAPI server on http://localhost:8001...")
    # reload=True is great for development. It auto-restarts the server when you save.
    uvicorn.run("main_server:app", host="0.0.0.0", port=8001, reload=True)