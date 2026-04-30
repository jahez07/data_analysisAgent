import os
from dotenv import load_dotenv
from langchain.tools import tool
from slack_sdk import WebClient

load_dotenv()
slack_token = os.getenv('SLACK_USER_TOKEN')
slack_client = WebClient(token=slack_token)

DEFAULT_CHANNEL = "C08MNFG5Y8L"
FILE_CHANNEL = "C08JBKQVBL5"

def generate_plot(backend):
    @tool(parse_docstring=True)
    def _generate_plot(csv_path: str, output_path: str = "/home/daytona/plot.png") -> str:
        """Read a CSV file and generate a bar chart saved as a PNG image.

        Args:
            csv_path: Path to the CSV file in the sandbox filesystem.
            output_path: Path where the PNG plot will be saved in the sandbox filesystem.
        """
        script = f"""
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

df = pd.read_csv('{csv_path}')
numeric_cols = df.select_dtypes(include='number').columns.tolist()
label_col = df.columns[0]

fig, ax = plt.subplots(figsize=(10, 6))
for col in numeric_cols:
    ax.bar(df[label_col].astype(str), df[col], label=col)

ax.set_xlabel(label_col)
ax.legend()
ax.set_title('Sales Data Analysis')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('{output_path}')
print('Plot saved to {output_path}')
"""
        backend.process.exec(f"python -c \"{script.strip()}\"")
        return output_path
    return _generate_plot


def slack_send_message(backend):
    @tool(parse_docstring=True)
    def _slack_send_message(text: str, file_path: str | None = None) -> str:
        """Send message to Slack, optionally including attachments such as images.

        Args:
            text: Text content of the message.
            file_path: File path of attachment in the sandbox filesystem.
        """
        if not file_path:
            slack_client.chat_postMessage(channel=DEFAULT_CHANNEL, text=text)
        else:
            fp = backend.download_files([file_path])
            slack_client.files_upload_v2(
                channel=FILE_CHANNEL,
                content=fp[0].content,
                initial_comment=text,
            )
        return "Message sent."
    return _slack_send_message