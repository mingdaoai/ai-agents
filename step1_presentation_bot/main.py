import asyncio
import os

from agents import set_default_openai_key
#from examples.research_bot.manager import ResearchManager
from manager import ResearchManager


async def main() -> None:
    query = input("What would you like to research? ")
    await ResearchManager().run(query)


if __name__ == "__main__":
    with open(os.path.expanduser('~/.mingdaoai/openai.key')) as f:
        os.environ['OPENAI_API_KEY'] = f.read().strip()
        set_default_openai_key(os.environ['OPENAI_API_KEY'])
    asyncio.run(main())
