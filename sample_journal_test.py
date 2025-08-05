import openai
import os
from datetime import datetime

# Sample data for testing
sample_summary = "Today I had a stressful meeting at work but then went for a walk in the park and felt much better. Had coffee with Sarah and we talked about her new job. Feeling tired but accomplished."

sample_answers = """Q1: How did you feel about the stressful meeting?
A1: I was really anxious beforehand but it went better than expected. Still drained though.

Q2: What was the highlight of your day?
A2: Definitely the walk in the park - the fresh air really cleared my head and I saw some cute dogs.

Q3: What are you grateful for today?
A3: I'm grateful for Sarah's friendship and that I have a job that challenges me, even if it's stressful sometimes."""

def generate_sample_journal():
    """Generate a sample journal entry using the same prompts as the app"""
    
    # You'll need to set your API key here for testing
    # api_key = "your-api-key-here"
    # client = openai.OpenAI(api_key=api_key)
    
    # For demonstration, I'll show what the prompt and expected output would be
    print("=== SAMPLE QUICK JOURNAL ENTRY ===\n")
    
    print("INPUT SUMMARY:")
    print(sample_summary)
    print("\n" + "="*50 + "\n")
    
    print("QUICK QUESTIONS GENERATED:")
    print("1. How did you feel about the stressful meeting?")
    print("2. What was the highlight of your day?")
    print("3. What are you grateful for today?")
    print("\n" + "="*50 + "\n")
    
    print("USER ANSWERS:")
    print(sample_answers)
    print("\n" + "="*50 + "\n")
    
    print("EXPECTED JOURNAL OUTPUT:")
    print("December 15, 2024")
    print()
    print("Today was a bit of a rollercoaster. The meeting at work had me stressed out all morning - I was really anxious about it, but it actually went better than I expected. Still, I was pretty drained afterward.")
    print()
    print("The highlight of my day was definitely the walk in the park. I needed to clear my head, and the fresh air really helped. Saw some cute dogs too, which always puts me in a better mood. Sometimes you just need that little break to reset.")
    print()
    print("Had coffee with Sarah and caught up on her new job situation. It's nice to have good friends to talk to. I'm grateful for her friendship and honestly grateful for my job too, even though it can be stressful. It challenges me and keeps me growing.")
    print()
    print("Feeling tired but accomplished. Tomorrow's another day.")
    print("\n" + "="*50 + "\n")
    
    print("KEY FEATURES OF THIS OUTPUT:")
    print("✅ Natural, conversational tone")
    print("✅ Only includes details actually mentioned")
    print("✅ Captures genuine emotions")
    print("✅ Concise (200-300 words)")
    print("✅ Includes date naturally")
    print("✅ Sounds like the person actually wrote it")
    print("✅ No overly formal or polished language")
    print("✅ Focuses on actual experience, not generic journaling")

if __name__ == "__main__":
    generate_sample_journal() 