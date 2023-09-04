import json

def get_notifications():
    with open("notifications.json", mode='r', encoding="utf-8") as file:
        json_data = file.read()
        data = json.loads(json_data)
        return data

def write_notifications(data):
    json_data = json.dumps(data, indent=4, ensure_ascii=False)
    with open('notifications.json', mode='w', encoding="utf-8") as file:
        file.write(json_data)