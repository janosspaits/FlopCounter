import json

# swap json file name for the file that you want to order (desc)

with open('three_point_counts.json', 'r') as file:
    data = json.load(file)

sorted_data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))

with open('three_point_counts.json', 'w') as file:
    json.dump(sorted_data, file, indent=4)