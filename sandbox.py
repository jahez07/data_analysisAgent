import os
import io
import csv
from dotenv import load_dotenv
from daytona import Daytona, DaytonaConfig

from langchain_daytona import DaytonaSandbox

load_dotenv()
daytona_api_key = os.getenv('DAYTONA_API_KEY')
daytona_sandbox_id = os.getenv('DAYTONA_SANDBOX_ID')


# Setting up Sanboxed backend
config = DaytonaConfig(api_key=daytona_api_key)
daytona = Daytona(config)

sandbox = daytona.get(daytona_sandbox_id)
# sandbox = daytona.create()
backend = DaytonaSandbox(sandbox=sandbox)

# Testing if the sandbox is up and running
# result = backend.execute("echo ready")
# print(result)

# Create sample sales data
data = [
    ["Date", "Product", "Units Sold", "Revenue"],
    ["2025-08-01", "Widget A", 10, 250],
    ["2025-08-02", "Widget B", 5, 125],
    ["2025-08-03", "Widget A", 7, 175],
    ["2025-08-04", "Widget C", 3, 90],
    ["2025-08-05", "Widget B", 8, 200],
]

# Convert to CSV bytes
text_buf = io.StringIO()
writer = csv.writer(text_buf)
writer.writerows(data)
csv_bytes = text_buf.getvalue().encode("utf-8")
text_buf.close()

backend.upload_files([("/home/daytona/data/sales_data.csv", csv_bytes)])