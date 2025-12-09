from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
import os

import requests
from ddgs import DDGS

PERSONA_PROMPTS = {
    "travel":  ( 
        "You are Travel Ellie, an organized, fun, practical travel planner."
        "You help with all things trips, flights, itineraries, packing, budgets, and recommendations."
        "You speak clearly and specifically, and you like making checklists, day plans, and night plans."
        "You can access real-time information by calling the `web_search` tool whenever "
        "the user asks about locations, activities, flights, events, weather, or news. "
        "Always use tools when needed."
    ), 
    "fitness": ( 
        "You are Fitness Ellie, a supportive and realistic fitness and wellness coach."
        "You help with workouts, nutrition, routines, habit-building, period-aware training."
        "Your tone is never harsh, always big-sister encouraging."
        "You can use the `web_search` tool to look up exercises, fitness research, "
        "nutrition info, or trends when helpful. Always use tools if the user asks "
        "for latest data or factual information."

    ),
    "study":(
        "You are Study Ellie, a focused but kind study coach."
        "You help with breaking down assignements, creating study schedules, explain concepts."
        "You know the user is balancing life and studies, so keep things calm and structured."
        'Use the `web_search` tool for researching topics, definitions, scholarly info, '
        "news, or anything requiring external information."
    ), 
    "chat": (
        "You are Chat Ellie, a warm, emotionally intelligent friend. "
        "You help the user process feelings, relationships, decisions, and everyday life. "
        "You validate emotions, ask gentle questions, and avoid sounding robotic."
        "If the user asks for factual information, news, or anything requiring "
        "external knowledge, you MUST call the `web_search` tool before answering."
    ),
}

# Load environment variables from .env
load_dotenv()
@tool 
def calculator(a:float, b:float) -> str: 
    """Useful for perfmorning basic arithmetic calculations with numbers"""
    print("tool has been called")
    return f"The sum of {a} and {b} is {a+b}" 
@tool 
def web_search(query: str, provider: str = "duckduckgo") -> str: 
    """Search the internet in real time using DuckDuckGo.
    
    Args:
        query: What to search for.
        provider: Currently only 'duckduckgo' is supported in this version.
    """
    print("web_search tool has been called with:", query)

    provider = provider.lower().strip()

    if provider != "duckduckgo":
        return "Right now I only support the 'duckduckgo' provider."

    try:
        # ddgs default search
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
    except Exception as e:
        return f"Error using DuckDuckGo: {e}"

    if not results:
        return f"No results found for '{query}' using DuckDuckGo."

    lines = [f"Top DuckDuckGo results for: {query}\n"]
    for r in results:
        title = r.get("title", "No title")
        url = r.get("href", r.get("url", ""))
        snippet = r.get("body", r.get("description", ""))
        lines.append(f"- {title}\n  {snippet}\n  {url}")
    return "\n".join(lines)

print("DEBUG: FOUND KEY?", os.getenv("OPENAI_API_KEY") is not None)

def choose_mode() -> str: 
    print("Which Ellie do you want to use today?\n")
    print("1. ✈️ Travel Ellie")
    print("2. 🧘‍♀️ Fitness Ellie")
    print("3. 📚 Study Ellie")
    print("4. 💬 Chat Ellie\n")
    print("\n* If at any point you want to change Ellies just type '/mode' ")

    mapping = {
        "1": "travel",
        "2": "fitness",
        "3": "study",
        "4": "chat",
    }
    while True: 
        choice = input("Please Enter 1, 2, 3, 4, or 'quit' to QUIT: ").strip()
        if choice in mapping: 
            mode = mapping[choice]
            print(f"\nPerfect! You are now talking to {mode.capitalize()} Ellie. \n")
            return mode

        elif choice.lower() == "quit":
            print("Goodbye! Exiting program.")
            exit ()
        else: 
            print("Invalid choice, please type 1, 2, 3, 4 or quit.")


def main():
    model = ChatOpenAI(
        model="gpt-4o-mini",  
        temperature=0,
    )


    tools = [calculator, web_search]
    agent_executor = create_react_agent(model, tools)

    print()
    print()
    print("Welcome! I'm Ellie, your AI assistant. Type 'quit' to exit.")
    print("Type '/mode' at any time to switch which Ellie you’re using.")
    print("Lets Chat!")

#the function is called to ask which mode to use 
    current_mode = choose_mode()

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() == "quit":
            break
        if user_input.lower().startswith("/mode"): 
            print("\nSwitching Ellies…\n")
            current_mode = choose_mode()
            continue

 #Wrap the user input with the selected persona
        persona = PERSONA_PROMPTS[current_mode]
        wrapped_input = f"{persona}\n\nUser: {user_input}"

        print("\nEllie: ", end="")
        for chunk in agent_executor.stream(
            {"messages": [HumanMessage(content=wrapped_input)]}
        ):
            if "agent" in chunk and "messages" in chunk["agent"]:
                for message in chunk["agent"]["messages"]:
                    print(message.content, end="")
        print() 


if __name__ == "__main__":
    main()











