import ThreadManager
from datetime import datetime
import json
import os
import spacy
import re

# Load the English NLP model from spaCy
nlp = spacy.load("en_core_web_sm")

airlines = {
    "Delta",
    "Southwest",
    "Hawaiian",
    "Alaska",
    "United",
    "American",
    "JetBlue",
    "Spirit",
    "Frontier",
    "Allegiant"
}

atc_taxi_keywords = [
    "HOLD",
    "HOLD POSITION",
    "HOLD FOR",
    "CROSS",
    "TAXI",
    "CONTINUE TAXIING",
    "PROCEED VIA",
    "ON",
    "TO",
    "ACROSS RUNWAY",
    "VIA",
    "HOLD SHORT OF",
    "FOLLOW",
    "BEHIND"
]

def phonetic_command_translator(line):
    phonetic_alphabet = {
        'Alpha': 'A',
        'Bravo': 'B',
        'Charlie': 'C',
        'Delta': 'D',
        'Echo': 'E',
        'Foxtrot': 'F',
        'Golf': 'G',
        'Hotel': 'H',
        'India': 'I',
        'Juliett': 'J',
        'Kilo': 'K',
        'Lima': 'L',
        'Mike': 'M',
        'November': 'N',
        'Oscar': 'O',
        'Papa': 'P',
        'Quebec': 'Q',
        'Romeo': 'R',
        'Sierra': 'S',
        'Tango': 'T',
        'Uniform': 'U',
        'Victor': 'V',
        'Whiskey': 'W',
        'X-ray': 'X',
        'Yankee': 'Y',
        'Zulu': 'Z'
    }
    number_to_spelled_version = {
        'one': '1',
        'two': '2',
        'three': '3',
        'four': '4',
        'five': '5',
        'six': '6',
        'seven': '7',
        'eight': '8',
        'nine': '9',
        'ten': '10',
        'eleven': '11',
        'twelve': '12',
        'thirteen': '13',
        'fourteen': '14',
        'fifteen': '15',
        'sixteen': '16',
        'seventeen': '17',
        'eighteen': '18',
        'nineteen': '19',
        'twenty': '20',
        'twenty one': '21',
        'twenty two': '22',
        'twenty three': '23',
        'twenty four': '24',
        'twenty five': '25',
        'twenty six': '26',
        'twenty seven': '27',
        'twenty eight': '28',
        'twenty nine': '29',
        'thirty': '30',
        'thirty one': '31',
        'thirty two': '32',
        'thirty three': '33',
        'thirty four': '34',
        'thirty five': '35',
        'thirty six': '36',
        'thirty seven': '37',
        'thirty eight': '38',
        'thirty nine': '39',
        'forty': '40',
        'forty one': '41',
        'forty two': '42',
        'forty three': '43',
        'forty four': '44',
        'forty five': '45',
        'forty six': '46',
        'forty seven': '47',
        'forty eight': '48',
        'forty nine': '49',
        'fifty': '50',
        'fifty one': '51',
        'fifty two': '52',
        'fifty three': '53',
        'fifty four': '54',
        'fifty five': '55',
        'fifty six': '56',
        'fifty seven': '57',
        'fifty eight': '58',
        'fifty nine': '59',
        'sixty': '60',
        'sixty one': '61',
        'sixty two': '62',
        'sixty three': '63',
        'sixty four': '64',
        'sixty five': '65',
        'sixty six': '66',
        'sixty seven': '67',
        'sixty eight': '68',
        'sixty nine': '69',
        'seventy': '70',
        'seventy one': '71',
        'seventy two': '72',
        'seventy three': '73',
        'seventy four': '74',
        'seventy five': '75',
        'seventy six': '76',
        'seventy seven': '77',
        'seventy eight': '78',
        'seventy nine': '79',
        'eighty': '80',
        'eighty one': '81',
        'eighty two': '82',
        'eighty three': '83',
        'eighty four': '84',
        'eighty five': '85',
        'eighty six': '86',
        'eighty seven': '87',
        'eighty eight': '88',
        'eighty nine': '89',
        'ninety': '90',
        'ninety one': '91',
        'ninety two': '92',
        'ninety three': '93',
        'ninety four': '94',
        'ninety five': '95',
        'ninety six': '96',
        'ninety seven': '97',
        'ninety eight': '98',
        'ninety nine': '99',
        'one hundred': '100'
    }

    result_list = []
    words = line.split()
    i = 0

    while i < len(words):
        word = words[i]
        if word == "delta":
            result_list.append(word)
        elif word in phonetic_alphabet:
            result_list.append(phonetic_alphabet[word])
        elif (i + 1) < len(words) and (word + " " + words[i + 1]) in number_to_spelled_version:
            result_list.append(number_to_spelled_version[word + " " + words[i + 1]])
            i += 1  # Skip the next word
        elif word in number_to_spelled_version:
            result_list.append(number_to_spelled_version[word])
        else:
            result_list.append(word)
        i += 1
    return ' '.join(result_list)

def extract_command(line):
    aviation_verbs = ['hold', 'clear', 'taxi', 'depart', 'ascend', 'descend', 'turn', 'climb', 'approach', 'land']
    words = line.lower().split()
    last_verb_index = -1

    for i, word in enumerate(words):
        if word in aviation_verbs:
            last_verb_index = i

    if last_verb_index == -1:
        return ""  # No aviation verb found
    return ' '.join(words[last_verb_index:])


def extract_flight(line):
    # Regex pattern to match the airline name followed by a series of digits separated by spaces
    match = re.search(r'\b(' + '|'.join(airlines) + r')\s(\d+\s*)+\b', line, re.IGNORECASE)

    if match:
        # Extract the airline name and the flight number
        airline = match.group(1)
        flight_numbers = ''.join(re.findall(r'\d+', match.group()))

        return f'{airline} {flight_numbers}'
    else:
        return None


def extract_runway(line):
    match = re.search(r"runway \d{1,2}", line)
    if match:
        return match.group()
    else:
        return None

def extract_tower(line):
    match = re.search(r"tower \d{1,2}", line)
    if match:
        return match.group()
    else:
        return None

def parse_taxi_command(line):
        flight_id = extract_flight(line)
        command = extract_command(line)
        runway = extract_runway(line)
        tower = extract_tower(line)
        return {
            "date": str(datetime.now()),
            "FlightID": flight_id,
            "Command": command,
            "Runway": runway,
            "Tower": tower
        }

def save_to_JSON(result_parsed):
    json_commands = json.dumps(result_parsed, indent=2)
    file_path = 'JSON_Taxi_Commands.json'
    with open(file_path, 'w') as file:
        file.write(json_commands)

#text = phonetic_command_translator("delta six two three in the event of missed approach taxi aircraft right of runway one near tower ten")
text1 = phonetic_command_translator("Charlie Foxtrot Bravo after landing, vacate runway to the left via taxiway Bravo, hold short of taxiway Echo for incoming traffic, then proceed to gate Alpha 3 under marshalling guidance")
print(text1)
print(parse_taxi_command(text1))
