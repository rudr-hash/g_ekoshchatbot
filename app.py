def chat_with_gemini(prompt, context=""):
    try:
        # Prepare the request to the Gemini API
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"{context}\n\n{prompt}"
                        }
                    ]
                }
            ]
        }

        # Call the Gemini API
        response = requests.post(endpoint, headers=headers, json=data)

        # Check for a successful response
        if response.status_code == 200:
            response_json = response.json()
            # Debugging: print the full response to check structure
            st.write("Full API Response:", response_json)

            # Extracting the text from response
            contents = response_json.get("contents", [])
            if contents:
                parts = contents[0].get("parts", [])
                if parts:
                    return parts[0].get("text", "No response text found.")
            return "No response text found."
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"An error occurred during API call: {str(e)}"
