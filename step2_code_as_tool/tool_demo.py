import asyncio
import random
from typing import Any
from agents import Agent, Runner, set_default_openai_key
from agents import AgentHooks, RunContextWrapper, Tool, function_tool
from pydantic import BaseModel
import os

@function_tool
def gen_random() -> int:
    """Generate a random number between 1 and 100."""
    try:
        random_num = random.randint(1, 100)
        print(f"Generating random number: {random_num}")
        return random_num
    except Exception as e:
        import traceback
        print(f"Error generating random number: {str(e)}")
        print("Stack trace:")
        print(traceback.format_exc())
        return 0.0

@function_tool
def multiply(x: int, y: int) -> int:
    """Multiply two numbers together."""
    try:
        print(f"Multiplying {x} by {y}")
        return x * y
    except Exception as e:
        import traceback
        print(f"Error multiplying numbers: {str(e)}")
        print("Stack trace:")
        print(traceback.format_exc())
        return 0.0

class Result(BaseModel):
    value: float

agent = Agent(
    name="Random Number Calculator",
    instructions="""You can help with calculations using random numbers. Handle queries like:
    - "What's the total for 50 items?"
    - "Multiply 25 by random"
    
    For each query:
    1. Use gen_random to get a single random number between 1 and 100
    2. Use multiply to calculate the total value by multiplying the random number with the quantity provided""",
    tools=[gen_random, multiply],
    output_type=Result
)

async def main() -> None:
    with open(os.path.expanduser('~/.mingdaoai/openai.key')) as f:
        os.environ['OPENAI_API_KEY'] = f.read().strip()
        set_default_openai_key(os.environ['OPENAI_API_KEY'])
        
    while True:
        print("\nEnter your calculation query (e.g., 'Calculate value for 100 units') or 'quit' to exit:")
        query = input("> ").strip()
        
        if query.lower() == 'quit':
            break
            
        result = await Runner.run(
            agent,
            query
        )
        print(f"Result: {result.final_output.value:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
