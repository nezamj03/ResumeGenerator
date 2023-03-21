import json
import pandas as pd

def read_file(path):
    file = open(path)
    content = json.load(file)
    return content

def collapse(content):
    res = []
    for entry in content:
        res.extend(entry)
    return res

def save_as_csv(content):
    column = pd.Series(content)
    column.to_csv("./res/experiences.csv")

if __name__ == "__main__":
    path = "./res/SWE_1.json"
    content = collapse(read_file(path))
    save_as_csv(content)