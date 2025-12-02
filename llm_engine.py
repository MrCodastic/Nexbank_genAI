import os
import ollama
from openai import AzureOpenAI

class BankingLLM:
    def __init__(self, provider="ollama"):
        self.provider = provider
        
        # --- CONFIGURATION: UPDATE THESE IF USING AZURE ---
        self.azure_client = None
        if provider == "azure":
            self.azure_client = AzureOpenAI(
                api_key="YOUR_AZURE_KEY_HERE",  
                api_version="2024-02-15-preview",
                azure_endpoint="https://YOUR_RESOURCE_NAME.openai.azure.com/"
            )
            self.deployment_name = "gpt-4o" 

    def generate_response(self, system_prompt, user_input):
        """
        Universal wrapper to switch between Local Llama 3 and Azure GPT-4
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        if self.provider == "ollama":
            # Uses your local machine (Must have 'ollama run llama3' running)
            response = ollama.chat(model='llama3', messages=messages)
            return response['message']['content']
            
        elif self.provider == "azure":
            # Uses Cloud Enterprise model
            response = self.azure_client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content

# Test it immediately
if __name__ == "__main__":
    ai = BankingLLM(provider="ollama") # Change to 'azure' to test cloud
    print("Test Response:", ai.generate_response("You are a bot.", "Say hello."))