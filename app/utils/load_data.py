import json

def load_data():
  file = open('data.json')
  data = json.load(file)

  return data