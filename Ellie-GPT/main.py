# Imports (what + why)


# HumanMessage is the LangChain message type for user input.
# I wrap my input as a HumanMessage before sending it into the agent.
from langchain_core.messages import HumanMessage

# ChatOpenAI is LangChain's wrapper for OpenAI chat models.
# This gives me a consistent interface for calling the model.
from langchain_openai import ChatOpenAI

# @tool lets me register normal Python functions as "tools"
# the agent is allowed to call while reasoning (like a calculator or web search).
from langchain.tools import tool

# create_react_agent creates a ReAct-style agent ("Reason + Act").
# That means the model can decide when to call tools.
from langgraph.prebuilt import create_react_agent

# dotenv helps me load environment variables from a .env file locally
from dotenv import load_dotenv

import os

# requests isn't currently used here (I can remove later), but it’s commonly used
# when I want to call APIs directly.
import requests

# DDGS is DuckDuckGo search library (unofficial) for simple web search results.
from ddgs import DDGS


# Persona prompts (my “Ellies”)


# This is a dictionary of persona system-style instructions.
# I’m basically creating different "personalities" by changing the prompt.
# Each persona also includes tool-use guidance (important for reliability).
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



# Env setup (API key loading)

# Load variables from a local .env file into environment variables.
# This is how I keep secrets out of my code.
load_dotenv()


# Tools (functions the agent can call)


@tool 
def calculator(a: float, b: float) -> str: 
    """
    Useful for performing basic arithmetic calculations with numbers.
    I’m keeping it simple: this tool just adds two numbers.
    """
    # This print is mainly for debugging so I can see that the tool was used.
    print("calculator tool has been called")
    return f"The sum of {a} and {b} is {a+b}" 


@tool 
def web_search(query: str, provider: str = "duckduckgo") -> str: 
    """
    Search the internet in real time using DuckDuckGo.

    Args:
        query: What to search for.
        provider: currently only duckduckgo is supported.
    """
    # Debug print so I can tell when the agent actually used this tool.
    print("web_search tool has been called with:", query)

    # Normalize provider string.
    provider = provider.lower().strip()

    # If user tries another provider, I block it.
    if provider != "duckduckgo":
        return "Right now I only support the 'duckduckgo' provider."

    try:
        # Use DuckDuckGo search to get up to 5 text results.
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
    except Exception as e:
        # If DDGS fails (network, rate limit, etc), I return an error message.
        return f"Error using DuckDuckGo: {e}"

    # If no results come back, return a clear message.
    if not results:
        return f"No results found for '{query}' using DuckDuckGo."

    # Build a readable string of the results to feed back to the agent.
    lines = [f"Top DuckDuckGo results for: {query}\n"]
    for r in results:
        title = r.get("title", "No title")

        # Different ddgs versions may use different keys for the url.
        url = r.get("href", r.get("url", ""))

        # Same with snippet body/description.
        snippet = r.get("body", r.get("description", ""))

        lines.append(f"- {title}\n  {snippet}\n  {url}")

    return "\n".join(lines)


# Quick debug check: do I have the key loaded correctly?
print("DEBUG: FOUND KEY?", os.getenv("OPENAI_API_KEY") is not None)



# CLI Mode chooser (user picks persona)


def choose_mode() -> str: 
    # I’m printing a menu so this can run in the terminal as a simple CLI app.
    print("Which Ellie do you want to use today?\n")
    print("1. ✈️ Travel Ellie")
    print("2. 🧘‍♀️ Fitness Ellie")
    print("3. 📚 Study Ellie")
    print("4. 💬 Chat Ellie\n")
    print("\n* If at any point you want to change Ellies just type '/mode' ")

    # Map numeric choices to persona keys.
    mapping = {
        "1": "travel",
        "2": "fitness",
        "3": "study",
        "4": "chat",
    }

    # Keep asking until user chooses a valid option or quits.
    while True: 
        choice = input("Please Enter 1, 2, 3, 4, or 'quit' to QUIT: ").strip()

        if choice in mapping: 
            mode = mapping[choice]
            print(f"\nPerfect! You are now talking to {mode.capitalize()} Ellie. \n")
            return mode

        elif choice.lower() == "quit":
            print("Goodbye! Exiting program.")
            exit()

        else: 
            print("Invalid choice, please type 1, 2, 3, 4 or quit.")


# Main program (agent + chat loop)

def main():
    # This creates the LLM object the agent will use.
    # temperature=0 makes responses more deterministic and less “creative”.
    model = ChatOpenAI(
        model="gpt-4o-mini",  
        temperature=0,
    )

    # These are the only tools the agent is allowed to call.
    # If it needs math, it can call calculator.
    # If it needs current info, it can call web_search.
    tools = [calculator, web_search]

    # This creates the actual ReAct agent executor.
    # Under the hood the model will decide:
    # - respond directly OR
    # - call a tool and then respond.
    agent_executor = create_react_agent(model, tools)

    # Friendly CLI greeting.
    print("\n\nWelcome! I'm Ellie, your AI assistant. Type 'quit' to exit.")
    print("Type '/mode' at any time to switch which Ellie you’re using.")
    print("Lets Chat!")

    # First thing: ask the user which persona mode they want.
    current_mode = choose_mode()

    # Chat loop runs until user types quit.
    while True:
        user_input = input("\nYou: ").strip()

        # Exit condition
        if user_input.lower() == "quit":
            break

        # Mode switching command
        if user_input.lower().startswith("/mode"): 
            print("\nSwitching Ellies…\n")
            current_mode = choose_mode()
            continue


        # Persona wrapping (key)

        # I grab the persona prompt text for current mode.
        persona = PERSONA_PROMPTS[current_mode]

        # I "wrap" the user message by prepending persona instructions.
        # This is basically me faking a system prompt by injecting it in the user message.
        # (If I wanted stronger control, I'd send persona as a SystemMessage instead.)
        wrapped_input = f"{persona}\n\nUser: {user_input}"

        # Stream output so it feels like a live chatbot.
        print("\nEllie: ", end="")

        # agent_executor.stream yields chunks as the agent runs.
        # I pass in a LangChain messages list (HumanMessage).
        for chunk in agent_executor.stream(
            {"messages": [HumanMessage(content=wrapped_input)]}
        ):
            # The stream returns different kinds of events.
            # I’m specifically printing the agent messages.
            if "agent" in chunk and "messages" in chunk["agent"]:
                for message in chunk["agent"]["messages"]:
                    print(message.content, end="")
        print() 


# Standard Python entry point
if __name__ == "__main__":
    main()







