# Agent used to synthesize a final report from the individual summaries.
from pydantic import BaseModel

from agents import Agent
import asyncio
import random
from typing import Any
from agents import Agent, Runner, set_default_openai_key
from agents import AgentHooks, RunContextWrapper, Tool, function_tool
from pydantic import BaseModel
import os

PROMPT = (
   "You are a presentation assistant. You are given a report and you need to format it into a PDF file. "
)

@function_tool
def format_report_to_pdf(markdown_content: str) -> str:
    print(f"Formatting report to PDF: {markdown_content}")
    """Format the report into a PDF file, and return the path to the file."""
    import markdown
    import pdfkit
    import os
    import uuid
    
    print("[DEBUG] Converting markdown to HTML...")
    # Convert markdown to HTML
    html_content = markdown.markdown(markdown_content)
    print(f"[DEBUG] Generated HTML content: {html_content[:200]}...")

    print("[DEBUG] Generating unique filename...")
    # Generate a unique filename
    filename = f"report_{uuid.uuid4()}.pdf"
    path = os.path.join(os.getcwd(), filename)
    print(f"[DEBUG] File will be saved to: {path}")

    print("[DEBUG] Converting HTML to PDF...")
    # Convert HTML to PDF
    pdfkit.from_string(html_content, path)
    print(f"[DEBUG] PDF successfully generated at: {path}")

    return path
class ReportLocation(BaseModel):
    """The location of the report."""
    path: str
    """The path to the report."""


format_agent = Agent(
    name="WriterAgent",
    instructions=PROMPT,
    #model="o3-mini",
    output_type=ReportLocation,
    tools=[format_report_to_pdf],
)
