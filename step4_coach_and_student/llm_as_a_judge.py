from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Literal

from agents import Agent, ItemHelpers, Runner, TResponseInputItem, trace, set_default_openai_key

"""
This example shows the LLM as a judge pattern. The first agent generates an outline for a story.
The second agent judges the outline and provides feedback. We loop until the judge is satisfied
with the outline.
"""

story_outline_generator = Agent(
    name="story_outline_generator",
    instructions=(
        "You generate a short story based on the user's input."
        "Can be a real story if the user's input is related to real person or event."
        "If there is any feedback provided, use it to improve the outline."
    ),
)


@dataclass
class EvaluationFeedback:
    score: Literal["pass", "needs_improvement", "fail"]
    feedback: str


evaluator = Agent[None](
    name="evaluator",
    instructions=(
        "You evaluate a story and decide if it's good enough."
        "If it's not good enough, you provide feedback on what needs to be improved."
        "Use the outline of a hero of a thousand faces to evaluate the outline."
        "Never give it a pass on the first try."
    ),
    output_type=EvaluationFeedback,
)


async def main() -> None:
    with open(os.path.expanduser('~/.mingdaoai/openai.key')) as f:
        os.environ['OPENAI_API_KEY'] = f.read().strip()
        set_default_openai_key(os.environ['OPENAI_API_KEY'])

    msg = input("What kind of story would you like to hear? ")
    input_items: list[TResponseInputItem] = [{"content": msg, "role": "user"}]

    latest_outline: str | None = None

    # We'll run the entire workflow in a single trace
    with trace("LLM as a judge"):
        while True:
            story_outline_result = await Runner.run(
                story_outline_generator,
                input_items,
            )

            input_items = story_outline_result.to_input_list()
            latest_outline = ItemHelpers.text_message_outputs(story_outline_result.new_items)
            print("================================================")
            print("Story generated")
            print(f"Story: {latest_outline}")

            print("================================================")

            evaluator_result = await Runner.run(evaluator, input_items)
            result: EvaluationFeedback = evaluator_result.final_output

            print(f"Evaluator score: {result.score}")
            print(f"Evaluator feedback: {result.feedback}")

            if result.score == "pass":
                print("Story outline is good enough, exiting.")
                break

            print("================================================")
            print("================================================")
            print("")
            print("Re-running with feedback")

            input_items.append({"content": f"Feedback: {result.feedback}", "role": "user"})

    print("================================================")
    print(f"Final story: {latest_outline}")
    print("================================================")


if __name__ == "__main__":
    asyncio.run(main())
