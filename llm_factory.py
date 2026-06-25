# llm_factory.py
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Keep keys active at the top of the workspace framework per request
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GROK_API_KEY = os.environ.get("GROK_API_KEY", "")

class LLMProviderEngine:
    def __init__(self):
        self.provider = None
        self.client = None
        self.model_name = None

        # 1. OPTION A-1: Docker Gemini Web API Bridge (New Integration Layer)
        if os.getenv("USE_DOCKER_PROXY") == "TRUE":
            self.provider = "GEMINI_DOCKER_PROXY"
            self.model_name = "gemini-3.5-flash-thinking"
            self.client = OpenAI(
                base_url="http://localhost:8081/v1",
                api_key="sk-your-key"  # Default fallback API string in config.json
            )
            print(f"[SYSTEM] Active Client Engine: Docker Gemini Web API Bridge ({self.model_name})", flush=True)
            return

        # 1. OPTION A: Local Gemini Web Proxy Route (Cost-Saving Mode)
        if os.getenv("USE_WEB_PROXY") == "TRUE":
            self.provider = "GEMINI_PROXY"
            self.model_name = "gemini-advanced"
            #self.model_name = "gemini-1.5-flash"
            self.client = OpenAI(
                api_key="mock-cookie-key", # Required by the client shell, proxy uses browser cookies
                base_url="http://localhost:4981/openai/v1"
            )
            print(f"[SYSTEM] Active Client Engine: Local Gemini Web Proxy ({self.model_name})", flush=True)
            return

        # 2. OPTION B: Production xAI Grok-3 Cloud Route
        if os.getenv("XAI_API_KEY"):
            self.provider = "GROK"
            self.client = OpenAI(api_key=os.getenv("XAI_API_KEY"), base_url="https://api.x.ai/v1")
            self.model_name = "grok-3"
            print("[SYSTEM] Active Client Engine: xAI Grok-3", flush=True)

        # 3. OPTION C: Production Google Gemini Cloud API Route
        elif os.getenv("GEMINI_API_KEY"):
            from google import genai
            self.client = genai.Client()
            self.provider = "GEMINI"
            self.model_name = "gemini-2.5-flash"
            print("[SYSTEM] Active Client Engine: Google Gemini 2.5 (Official API)", flush=True)
            
        else:
            raise ValueError("Configuration Error: No active engine route detected. Verify your .env keys.")

    def get_structured_json_from_file(self, file_path: str, system_instruction: str, user_prompt: str, response_schema) -> dict:
        """
        Routes processing intelligently based on the active provider type.
        """
        ext = os.path.splitext(file_path)[1].lower()

        # --- BRANCH A: TEXT/FALLBACK PROCESSING (Used by Grok, Docker Bridge, and the Web Proxy) ---
        if self.provider in ["GEMINI_DOCKER_PROXY", "GEMINI_PROXY", "GROK"] or ext in ['.json', '.txt', '.csv', '.xml']:
            if ext == '.pdf':
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    text_data = "\n".join([p.extract_text() or "" for p in pdf.pages])
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_data = f.read()

            combined_prompt = (
                f"System Instructions:\n{system_instruction}\n\n"
                f"You MUST format your final response strictly as a single, valid JSON object matching this schema structure:\n"
                f"{json.dumps(response_schema.model_json_schema(), indent=2)}\n\n"
                f"Document Data:\n{text_data}\n\n"
                f"Task: {user_prompt}"
            )

            # Route through the OpenAI-compatible client wrapper
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": combined_prompt}],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            raw_text = completion.choices[0].message.content
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0].strip()
                
            return json.loads(raw_text)

        # --- BRANCH B: NATIVE BINARY MULTIMODAL PROCESSING (Official Gemini Cloud Only) ---
        elif self.provider == "GEMINI":
            from google.genai import types
            print(f"[SYSTEM] Uploading file asset context directly to Gemini storage...", flush=True)
            uploaded_file = self.client.files.upload(file=file_path)
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[uploaded_file, user_prompt],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    temperature=0.1
                )
            )
            self.client.files.delete(name=uploaded_file.name)
            return json.loads(response.text)