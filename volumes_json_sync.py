import json

# BIG VOLUMES
def read_json():
    with open("big_volumes.json", mode='r', encoding="utf-8") as file:
        json_data = file.read()
        data = json.loads(json_data)
        return data

def write_json(data):
    json_data = json.dumps(data, indent=4)
    with open('big_volumes.json', mode='w', encoding="utf-8") as file:
        file.write(json_data)

def clear_json():
    write_json([])

# AVG VOLUMES
def read_json_file():
    with open('volumes_avg_prev.json', mode="r", encoding='utf-8') as file:
        data = file.read()
        return json.loads(data)

def write_json_file(data):
    with open('volumes_avg_prev.json', mode="w", encoding='utf-8') as file:
        file.write(json.dumps(data, indent=4))

def update_json_data(key, value):
    data = read_json_file()
    data[key] = value
    write_json_file(data)

# Синхронная функция для очистки JSON-файла
def clear_json_file():
    write_json_file({})
