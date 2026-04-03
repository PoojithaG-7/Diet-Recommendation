# Test frontend time formatting
import datetime

# Sample timestamp from backend
timestamp = "2026-04-02T08:36:53.391981+05:30"

# Convert to Date object (like frontend does)
date_obj = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

# Format like frontend will
formatted_time = date_obj.strftime('%I:%M:%S %p')
print(f"Backend timestamp: {timestamp}")
print(f"Frontend will display: {formatted_time}")

# Test with current time
current_time = datetime.datetime.now()
formatted_current = current_time.strftime('%I:%M:%S %p')
print(f"Current time: {formatted_current}")
