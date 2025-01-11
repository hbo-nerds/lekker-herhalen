import json
from datetime import datetime, timedelta
from collections import defaultdict

# Load JSON data from a file or directly
with open("data/schedule_main.json") as file:
    json_data = json.load(file)

# Convert dates and group by content_id
def find_duplicates_within_year(data):
    content_dates = defaultdict(list)

    # Parse the data
    for entry in data:
        content_id = entry["content_id"]
        planned_date = datetime.strptime(entry["planned_date"], "%Y-%m-%d")
        content_dates[content_id].append(planned_date)

    # Check for duplicates within one year
    duplicates = []
    for content_id, dates in content_dates.items():
        dates.sort()  # Sort dates for easier comparison
        for i in range(len(dates)):
            for j in range(i + 1, len(dates)):
                if dates[j] - dates[i] <= timedelta(days=365 * 3):
                    duplicates.append(content_id)
                    break  # No need to check further for this content_id

    return list(set(duplicates))

# Call the function and print the result
duplicates = find_duplicates_within_year(json_data)
print("Content IDs with duplicates within three years:", duplicates)