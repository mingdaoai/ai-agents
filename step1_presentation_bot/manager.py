from __future__ import annotations

import asyncio
import time
import traceback

from rich.console import Console

from agents import Runner, custom_span, gen_trace_id, trace

from myagents.planner_agent import WebSearchItem, WebSearchPlan, planner_agent
from myagents.search_agent import search_agent
from myagents.writer_agent import ReportData, writer_agent
from printer import Printer
from myagents.format_agent import format_agent, ReportLocation


class ResearchManager:
    def __init__(self):
        self.console = Console()
        self.printer = Printer(self.console)

    async def run(self, query: str) -> None:
        print("\n=== Starting Research Process ===")
        print(f"Input Query: {query}\n")
        
        trace_id = gen_trace_id()
        with trace("Research trace", trace_id=trace_id):
            self.printer.update_item(
                "trace_id",
                f"View trace: https://platform.openai.com/traces/{trace_id}",
                is_done=True,
                hide_checkmark=True,
            )

            self.printer.update_item(
                "starting",
                "Starting research...",
                is_done=True,
                hide_checkmark=True,
            )
            search_plan = await self._plan_searches(query)
            search_results = await self._perform_searches(search_plan)
            report = await self._write_report(query, search_results)

            final_report = f"Report summary\n\n{report.short_summary}"
            self.printer.update_item("final_report", final_report, is_done=True)
            
            # Format the report to PDF
            pdf_location = await self._format_report(report.markdown_report)
            self.printer.update_item(
                "pdf_report",
                f"PDF Report generated at: {pdf_location.path}",
                is_done=True
            )

            self.printer.end()

        print("\n=== Final Results ===")
        print("\n=====REPORT=====\n")
        print(f"Report: {report.markdown_report}")
        print("\n=====FOLLOW UP QUESTIONS=====\n")
        follow_up_questions = "\n".join(report.follow_up_questions)
        print(f"Follow up questions: {follow_up_questions}")
        print("\n=== Research Process Complete ===\n")

    async def _plan_searches(self, query: str) -> WebSearchPlan:
        print("\n=== Planning Searches ===")
        print(f"Planning Input Query: {query}")
        
        self.printer.update_item("planning", "Planning searches...")
        result = await Runner.run(
            planner_agent,
            f"Query: {query}",
        )
        
        print("\nSearch Plan Output:")
        print(f"Number of searches planned: {len(result.final_output.searches)}")
        for idx, search in enumerate(result.final_output.searches, 1):
            print(f"\nSearch {idx}:")
            print(f"Query: {search.query}")
            print(f"Reason: {search.reason}")
        
        self.printer.update_item(
            "planning",
            f"Will perform {len(result.final_output.searches)} searches",
            is_done=True,
        )
        return result.final_output_as(WebSearchPlan)

    async def _perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        print("\n=== Performing Searches ===")
        print("\nSearch Queries to Execute:")
        for idx, search in enumerate(search_plan.searches, 1):
            print(f"\n{idx}. Query: {search.query}")
            print(f"   Reason: {search.reason}")
            
        with custom_span("Search the web"):
            self.printer.update_item("searching", "Searching...")
            num_completed = 0
            tasks = [asyncio.create_task(self._search(item)) for item in search_plan.searches]
            results = []
            for task in asyncio.as_completed(tasks):
                result = await task
                if result is not None:
                    results.append(result)
                    print(f"\nSearch Result {num_completed + 1}:")
                    print("=" * 50)
                    print(f"Result: {result[:500]}...")  # Print first 500 chars of result
                    print("=" * 50)
                num_completed += 1
                print(f"\nCompleted search {num_completed}/{len(tasks)}")
                self.printer.update_item(
                    "searching", f"Searching... {num_completed}/{len(tasks)} completed"
                )
            
            print("\nSearch Results Summary:")
            print(f"Total searches completed: {len(results)}/{len(tasks)}")
            print(f"Successful searches: {len([r for r in results if r is not None])}")
            
            self.printer.mark_item_done("searching")
            return results

    async def _search(self, item: WebSearchItem) -> str | None:
        print(f"\nExecuting search: {item.query}")
        print(f"Search reason: {item.reason}")
        input = f"Search term: {item.query}\nReason for searching: {item.reason}"
        try:
            result = await Runner.run(
                search_agent,
                input,
            )
            print(f"Search completed successfully for: {item.query}")
            return str(result.final_output)
        except Exception:
            print(f"Search failed for: {item.query}")
            print("Error details:")
            traceback.print_exc()
            return None

    async def _write_report(self, query: str, search_results: list[str]) -> ReportData:
        print("\n=== Writing Report ===")
        print(f"Original query: {query}")
        print(f"Number of search results to process: {len(search_results)}")
        
        self.printer.update_item("writing", "Thinking about report...")
        input = f"Original query: {query}\nSummarized search results: {search_results}"
        result = Runner.run_streamed(
            writer_agent,
            input,
        )
        update_messages = [
            "Thinking about report...",
            "Planning report structure...",
            "Writing outline...",
            "Creating sections...",
            "Cleaning up formatting...",
            "Finalizing report...",
            "Finishing report...",
        ]

        last_update = time.time()
        next_message = 0
        async for _ in result.stream_events():
            if time.time() - last_update > 5 and next_message < len(update_messages):
                current_message = update_messages[next_message]
                print(f"\nReport Progress: {current_message}")
                self.printer.update_item("writing", current_message)
                next_message += 1
                last_update = time.time()

        print("\nReport writing completed")
        self.printer.mark_item_done("writing")
        return result.final_output_as(ReportData)

    async def _format_report(self, markdown_report: str) -> ReportLocation:
        print("\n=== Formatting Report to PDF ===")
        self.printer.update_item("formatting", "Converting report to PDF...")
        
        try:
            result = await Runner.run(
                format_agent,
                markdown_report,
            )
            print(f"\nPDF Report generated successfully at: {result.final_output.path}")
            self.printer.mark_item_done("formatting")
            return result.final_output_as(ReportLocation)
        except Exception:
            print("Failed to format report to PDF")
            print("Error details:")
            traceback.print_exc()
            self.printer.update_item(
                "formatting",
                "Failed to generate PDF report",
                is_done=True
            )
            raise
