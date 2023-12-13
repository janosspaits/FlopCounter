import json

def sort_flopping_counts_descending(filepath):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print("File not found.")
        return
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return

    items = list(data.items())
    sorted_items = sorted(items, key=lambda x: x[1]['count'] if isinstance(x[1], dict) else x[1], reverse=True)
    
    with open(filepath, 'w') as file:
        file.write("{\n")
        for i, (player, details) in enumerate(sorted_items):
            json_string = f'"{player}": {json.dumps(details)}'
            if i < len(sorted_items) - 1:
                json_string += ","
            file.write(json_string + "\n")
        file.write("}\n")

    print("Flopping counts sorted and saved.")

# Example usage
sort_flopping_counts_descending('flopping_counts.json')

