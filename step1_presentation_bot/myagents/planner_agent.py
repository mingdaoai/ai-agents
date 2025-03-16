from pydantic import BaseModel

from agents import Agent

from datetime import datetime

PROMPT = (
    "You are a helpful research assistant. Given a query, come up with a set of web searches "
    #"to perform to best answer the query. Output between 5 and 20 terms to query for."
    "to perform to best answer the query. Output at most 5 terms to query for."
    f"Search up to date information. Current date is {datetime.now().strftime('%Y-%m-%d')}."
)


class WebSearchItem(BaseModel):
    reason: str
    "Your reasoning for why this search is important to the query."

    query: str
    "The search term to use for the web search."


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem]
    """A list of web searches to perform to best answer the query."""


planner_agent = Agent(
    name="PlannerAgent",
    instructions=PROMPT,
    model="gpt-4o",
    output_type=WebSearchPlan,
)
