import os
from langchain_core.utils.uuid import uuid7
from langchain_ollama import ChatOllama

from langgraph.checkpoint.memory import InMemorySaver
from deepagents.backends import LocalShellBackend
from deepagents.backends import StateBackend
from deepagents import create_deep_agent
from dotenv import load_dotenv


from langchain_daytona import DaytonaSandbox

from tools import generate_plot, slack_send_message

backend = LocalShellBackend(root_dir=".", env={"PATH":"/usr/bin:/bin"}, virtual_mode=False)
model = ChatOllama(
    model="gemma4:e2b",
    temperature=0,
)

checkpointer = InMemorySaver()

SYSTEM_PROMPT = """You are a data analysis agent. You have access to these tools:
- generate_plot: reads a CSV and saves a PNG chart to the sandbox
- _slack_send_message: sends a message (and optionally a file) to Slack

Rules:
1. NEVER use `execute` or `requests` to send Slack messages — always use _slack_send_message.
2. NEVER construct raw HTTP requests — use the provided tools only.
3. To send a plot to Slack, first call generate_plot to get the output_path, then call _slack_send_message with that path as file_path.
4. Do not claim success unless the tool returned a successful result.
"""

agent = create_deep_agent(
    model=model,
    tools=[generate_plot(backend), slack_send_message(backend)],
    backend=backend,
    checkpointer=checkpointer,
    system_prompt=SYSTEM_PROMPT,
)

thread_id = str(uuid7())
config = {"configurable": {"thread_id": thread_id}}

input_message = {
    "role": "user",
    "content": (
        "Analyze ./bin/sales_data.csv in the current dir and generate a beautiful plot."
        "When finished, send your analysis and the plot to Slack using the tool."
    ),
}

for step in agent.stream(
    {"messages": [input_message]},
    config=config,
    stream_mode="updates"
):
    for _, update in step.items():
        if update and (messages := update.get("messages")) and isinstance(messages, list):
            for message in messages:
                message.pretty_print()