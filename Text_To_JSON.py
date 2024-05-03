import ThreadManager
from datetime import datetime
import json
import os
import spacy
import re

# Load the English NLP model from spaCy
nlp = spacy.load("en_core_web_sm")

airlines = {
    "Delta", "Southwest", "Hawaiian", "Alaska", "United", "American", "JetBlue", "Spirit", "Frontier", "Allegiant",
    "Ryanair", "Lufthansa", "Air France", "KLM", "British Airways", "Turkish Airlines", "Emirates", "Qatar Airways",
    "Etihad Airways", "Singapore Airlines", "Cathay Pacific", "ANA", "Japan Airlines", "Air Canada", "Aeroflot",
    "China Southern Airlines", "China Eastern Airlines", "Air China", "Hainan Airlines", "IndiGo", "SpiceJet",
    "Qantas", "Virgin Australia", "LATAM", "Gol Transportes Aéreos", "Azul", "EasyJet", "Iberia", "Vueling",
    "SAS Scandinavian Airlines", "Finnair", "Thai Airways", "Korean Air", "Malaysia Airlines", "Garuda Indonesia",
    "Philippine Airlines", "Vietnam Airlines", "Aeromexico", "Saudi Arabian Airlines", "Ethiopian Airlines"
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
        'alpha': 'A', 'bravo': 'B', 'charlie': 'C', 'delta': 'D', 'echo': 'E', 'foxtrot': 'F',
        'golf': 'G', 'hotel': 'H', 'india': 'I', 'juliett': 'J', 'kilo': 'K', 'lima': 'L',
        'mike': 'M', 'november': 'N', 'oscar': 'O', 'papa': 'P', 'quebec': 'Q', 'romeo': 'R',
        'sierra': 'S', 'tango': 'T', 'uniform': 'U', 'victor': 'V', 'whiskey': 'W', 'x-ray': 'X',
        'yankee': 'Y', 'zulu': 'Z'
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
        if word in phonetic_alphabet.keys():
            result_list.append(phonetic_alphabet[word.lower()])
        elif (i + 1) < len(words) and (word + " " + words[i + 1].lower()) in number_to_spelled_version:
            result_list.append(number_to_spelled_version[word + " " + words[i + 1].lower()])
            i += 1  # Skip the next word
        elif word in number_to_spelled_version:
            result_list.append(number_to_spelled_version[word])
        else:
            result_list.append(words[i])  # Keep original case for words not in dictionaries
        i += 1
    return ' '.join(result_list)

def find_verbs(text):
    aviation_verbs = ['hold', 'clear', 'taxi', 'depart', 'ascend', 'descend', 'turn', 'climb', 'approach', 'land']

    doc = nlp(text)
    verbs = [token.text for token in doc if token.pos_ == 'VERB']

    words = text.lower().split()
    for verb in aviation_verbs:
        if verb in words and verb not in verbs:
            verbs.append(verb)

    return verbs

def extract_command(line):
    words = line.lower().split()
    verbs = find_verbs(line)
    first_verb_index = next((i for i, word in enumerate(words) if word in verbs), None)

    if first_verb_index is None:
        return ""  
    return ' '.join(words[first_verb_index:])


def extract_flight(line):
    # Regex pattern to match 'D' or full airline name followed by a series of digits
    # Expanded to include handling the single 'D' as an abbreviation for "Delta"
    pattern = r'\b(D|\b' + '|'.join(airlines) + r')\s*(\d+\s*)+\b'
    match = re.search(pattern, line, re.IGNORECASE)

    if match:
        # Extract the airline name or abbreviation and the flight number
        airline = match.group(1)
        flight_numbers = ''.join(re.findall(r'\d+', match.group()))

        # Check if the airline is 'D' and convert it to 'Delta'
        if airline.upper() == 'D':
            airline = 'Delta'
        
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

def extract_terminal(line):
    match = re.search(r"terminal \d{1,2}", line)
    if match:
        return match.group()
    else:
        return None    


def parse_taxi_command(line):
        flight_id = extract_flight(line)
        command = extract_command(line)
        runway = extract_runway(line)
        tower = extract_tower(line)
        terminal = extract_terminal(line)
        return {
            "date": str(datetime.now()),
            "FlightID": flight_id,
            "Command": command,
            "Runway": runway,
            "Tower": tower,
            "Terminal": terminal
        }

def save_to_JSON(result_parsed):
    json_commands = json.dumps(result_parsed, indent=2)
    file_path = 'JSON_Taxi_Commands.json'
    with open(file_path, 'w') as file:
        file.write(json_commands)

text = phonetic_command_translator(" in the event of missed approach head toward taxi the aircraft right of runway twelve near tower five but hold short of terminal two b thank you United six two three")
#text = phonetic_command_translator("")
# print(text)
# print(parse_taxi_command(text))