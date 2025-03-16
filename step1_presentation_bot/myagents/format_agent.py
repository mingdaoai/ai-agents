# Agent used to synthesize a final report from the individual summaries.
from pydantic import BaseModel

from agents import Agent

PROMPT = (
   "You are a presentation assistant. You are given a report and you need to format it into a PDF file. "
)

@function_tool
def format_report_to_pdf(markdown_content: str) -> str:
    """Format the report into a PDF file, and return the path to the file."""
    import markdown
    import pdfkit
    import os
    import uuid
    # Convert markdown to HTML
    html_content = markdown.markdown(markdown_content)

    # Generate a unique filename
    filename = f"report_{uuid.uuid4()}.pdf"
    path = os.path.join(os.getcwd(), filename)

    # Convert HTML to PDF
    pdfkit.from_string(html_content, path)

    return path

class ReportLocation(BaseModel):
    """The location of the report."""
    path: str
    """The path to the report."""


format_agent = Agent(
    name="WriterAgent",
    instructions=PROMPT,
    model="o4-mini",
    output_type=ReportLocation,
    tools=[format_report_to_pdf],
)
