import ThreadManager
from datetime import datetime
import json
import os

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

        if word in phonetic_alphabet:
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


def parse_taxi_command(line):
    keyword = "this"
    parts = line.split(keyword, 1)  # Split the string into two parts at the first occurrence of the keyword
    if len(parts) == 1:
        # Keyword not found, return the entire string
        return line, None
    else:
        return {
            "date": str(datetime.now()),
            "flight": parts[0],
            "instruction": parts[1]
        }



def save_to_JSON(result_parsed):
    json_commands = json.dumps(result_parsed, indent=2)

    file_path = 'JSON_Taxi_Commands.json'
    with open(file_path, 'w') as file:
        file.write(json_commands)

text = phonetic_command_translator("Delta one two three this is ground control please head to runway thirty three taxi via Delta Bravo Zulu")
print(text)
print(parse_taxi_command(text))