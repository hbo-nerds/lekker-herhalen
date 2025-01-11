import json
import random
from datetime import datetime, timedelta

# Import data.json
with open('../server/data/data.json', encoding='utf8') as f:
    json_data = json.load(f)

# Filter the list to only include streams
streams = [item for item in json_data['content'] if item['type'] == 'stream' and ('twitch_id' in item)]

# Main streams are streams that have the tag 'main'
main_streams = [s for s in streams if "tags" in s and 'main' in s['tags']]

# Start in 2025
start = datetime(2025, 1, 1)
current_year, current_week, current_weekday = start.isocalendar()

schedule = []

# Loop through the next 10 years in weeks
for week_offset in range(52 * 10):
    # Calculate the Monday and Wednesday of each week
    target_year = current_year - 10
    jan_4_target_year = datetime(target_year, 1, 4)  # Jan 4 is always in the 1st ISO week
    monday_of_week = jan_4_target_year + timedelta(weeks=current_week - 1 + week_offset)
    monday_of_week -= timedelta(days=monday_of_week.weekday())  # Adjust to Monday
    
    # Calculate Wednesday (Monday + 2 days)
    wednesday_of_week = monday_of_week + timedelta(days=2)

    # Convert dates to string format (YYYY-MM-DD)
    monday_of_week_str = monday_of_week.strftime("%Y-%m-%d")
    wednesday_of_week_str = wednesday_of_week.strftime("%Y-%m-%d")
    
    # Get the Monday and Wednesday 10 years later (calculate the exact matching Monday and Wednesday)
    future_year = current_year
    jan_4_future_year = datetime(future_year, 1, 4)  # Start of the future year
    monday_planned_date = jan_4_future_year + timedelta(weeks=current_week - 1 + week_offset)
    monday_planned_date -= timedelta(days=monday_planned_date.weekday())  # Adjust to Monday

    # Calculate Wednesday (Monday + 2 days)
    wednesday_planned_date = monday_planned_date + timedelta(days=2)

    # Convert dates to string format (YYYY-MM-DD)
    monday_planned_date_str = monday_planned_date.strftime("%Y-%m-%d")
    wednesday_planned_date_str = wednesday_planned_date.strftime("%Y-%m-%d")

    # Search for streams on Monday and Wednesday
    monday_stream = next((s for s in streams if s['date'] == monday_of_week_str), None)
    wednesday_stream = next((s for s in streams if s['date'] == wednesday_of_week_str), None)

    # Add to schedule for Monday
    if monday_stream:
        schedule.append({
            'content_id': monday_stream['id'],
            'planned_date': monday_planned_date_str,
            'chronological': True
        })
    else:
        # No stream found, prepare for a random stream
        schedule.append({
            'content_id': None,
            'planned_date': monday_planned_date_str,
            'chronological': False
        })

    # Add to schedule for Wednesday
    if wednesday_stream:
        schedule.append({
            'content_id': wednesday_stream['id'],
            'planned_date': wednesday_planned_date_str,
            'chronological': True
        })
    else:
        # No stream found, prepare for a random stream
        schedule.append({
            'content_id': None,
            'planned_date': wednesday_planned_date_str,
            'chronological': False
        })

# Helper function to check if a content_id is valid for a given date
def is_valid_content_id(content_id, planned_date, existing_schedule, timespan_years=3):
    planned_datetime = datetime.strptime(planned_date, "%Y-%m-%d")
    timespan = timedelta(days=timespan_years * 365)

    for entry in existing_schedule:
        if entry['content_id'] == content_id:
            existing_date = datetime.strptime(entry['planned_date'], "%Y-%m-%d")
            if abs(planned_datetime - existing_date) <= timespan:
                return False
    return True

# Assign valid IDs to non-chronological streams
for entry in schedule:
    if not entry['chronological']:
        random_stream = random.choice(main_streams)
        while not is_valid_content_id(random_stream['id'], entry['planned_date'], schedule):
            random_stream = random.choice(main_streams)
        entry['content_id'] = random_stream['id']

# Write the updated schedule to a new JSON file
with open('../server/data/schedule_main.json', 'w', encoding='utf8') as f:
    json.dump(schedule, f, ensure_ascii=False, indent=4)

print("schedule_main.json has been created with no duplicates within a three-year timespan.")
