from summary.summary import compact
import json


with open("summary/test.json", "r", encoding="utf-8") as f:
    messages = json.load(f)
    compact(messages)
    print(messages)

    # compact(messages)
    # print(messages)
