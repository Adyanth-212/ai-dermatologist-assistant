
# Minimal chatbot placeholder - this could be a small rule-based symptom assistant,
# or a wrapper to a hosted LLM.
def simple_chatbot(symptoms_text):
    # Very simple rules-based response (expand later)
    if "itch" in symptoms_text.lower():
        return "It might be dermatitis or eczema — please take clear photos and consult a doctor."
    return "Please provide more symptoms or upload an image for better diagnosis."
