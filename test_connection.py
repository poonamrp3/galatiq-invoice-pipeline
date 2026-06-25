# test_connection.py
import os
from dotenv import load_dotenv

# Load environmental variables from your local .env file
load_dotenv()

def test_raw_connection():
    print("Checking active environment configurations...", flush=True)
    
    # 1. New Priority: Test Routing for Docker Gemini Web API Bridge
    if os.getenv("USE_DOCKER_PROXY") == "TRUE":
        print("Detected USE_DOCKER_PROXY=TRUE. Initializing Docker API Bridge container loop...", flush=True)
        from openai import OpenAI
        client = OpenAI(
            api_key="none",  # Default fallback key inside the container's config.json
            base_url="http://localhost:8081/v1"
        )
        
        # Using the exact model verified via curl
        target_model = "gemini-3.5-flash-thinking"
        print(f"Sending ping request to Docker proxy via {target_model}...", flush=True)
        
        completion = client.chat.completions.create(
            model=target_model,
            messages=[
                {"role": "user", "content": "Hello! Confirming connection. Respond with a quick greeting."}
            ]
        )
        print("\n--- Docker Proxy Response Success ---")
        print(completion.choices[0].message.content)
        print("---------------------------------")

    # 2. Test Routing for xAI Grok (Galatiq's Production Setup)
    elif os.getenv("XAI_API_KEY"):
        print("Detected XAI_API_KEY. Initializing Grok connection loop...", flush=True)
        from openai import OpenAI
        client = OpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1"
        )
        
        print("Sending ping request to grok-3...", flush=True)
        completion = client.chat.completions.create(
            model="grok-3",
            messages=[
                {"role": "user", "content": "Hello! Confirming connection. Respond with a quick greeting."}
            ]
        )
        print("\n--- Provider Response Success ---")
        print(completion.choices[0].message.content)
        print("---------------------------------")

    # 3. Test Routing for Google Gemini (Your Local Development Cloud API)
    elif os.getenv("GEMINI_API_KEY"):
        print("Detected GEMINI_API_KEY. Initializing Gemini connection loop...", flush=True)
        from google import genai
        client = genai.Client()
        
        print("Sending ping request to gemini-2.5-flash...", flush=True)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Hello! Confirming connection. Respond with a quick greeting."
        )
        print("\n--- Provider Response Success ---")
        print(response.text)
        print("---------------------------------")
        
    else:
        print("\n❌ CONNECTION ERROR: No API keys or active proxy flags found inside your .env file.", flush=True)
        print("Ensure USE_DOCKER_PROXY=TRUE, GEMINI_API_KEY, or XAI_API_KEY is defined.", flush=True)

if __name__ == "__main__":
    test_raw_connection()