import json
from datetime import datetime

# method to parse a single line of the text file, will only work as single line currently
def parse_taxi_command(line):
    parts = line.split(' ', 1)
    if len(parts) == 2:
        return {"date": str(datetime.now()),"flight": parts[0], "instruction": parts[1].strip()}
    else:
        return None

# method to read the entire text file and parse each line using previous method
taxi_commands = []
with open('commands.txt', 'r') as file:
    for line in file:
        parsed_command = parse_taxi_command(line)
        if parsed_command:
            taxi_commands.append(parsed_command)

# converts dictionary lists to json
json_commands = json.dumps(taxi_commands, indent=2)

file_path = 'JSON_Taxi_Commands.txt'

# writes the data to file 
with open(file_path, 'w') as file:
    file.write(json_commands)
