import json

with open('data/data.json', 'r', encoding='utf8') as file:
    data = json.load(file)['content']

def find_by_id(id):
    for item in data:
        if item['id'] == id:
            return item
    return None

def get_schedule():
    with open('data/schedule_main.json', 'r') as file:
        schedule = json.load(file)

    with open('data/index.json', 'r') as file:
        index_data = json.load(file)

    index = index_data['main']

    response = []

    for i in range(index, 20):
        if i >= len(schedule):
            break

        schedule_item = schedule[i]
        content = find_by_id(schedule_item['content_id'])
        if schedule_item.get('chronological'):
            response.append({
                'id': content['id'],
                'title': content['titles'][0],
                'chronological': True,
                'planned_date': schedule_item['planned_date']
            })
        else:
            response.append({
                'chronological': False,
                'planned_date': schedule_item['planned_date']
            })

    return response