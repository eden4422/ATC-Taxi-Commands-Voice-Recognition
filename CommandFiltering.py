import re


def split_terms(split_words: list, dictionary: dict):
    split_result: list = []
    split_words.reverse()
    words_so_far: list = []

    print(split_words)

    for word in split_words:
        print(word)

        if word in dictionary:
            words_so_far.reverse()
            tuple_to_add = (word,words_so_far)
            print(tuple_to_add)
            split_result.append(tuple_to_add)

            words_so_far = []

        else:
            words_so_far.append(word)
            print(words_so_far)

    split_result.reverse()
    return split_result


# Example usage:

def remove_before_target_phrase(input_list, target_phrase):
    # Find the index of the target phrase in the list
    index_of_target = next((i for i, phrase in enumerate(input_list) if target_phrase in phrase), None)

    if index_of_target is not None:
        # Remove elements before the target phrase
        result_list = input_list[index_of_target:]
        return result_list
    else:
        # If the target phrase is not found, return the original list
        return input_list

def split_string_by_phrases(input_string, split_phrases):
    # Create a regular expression pattern for splitting
    pattern = '|'.join(map(re.escape, split_phrases))
    
    # Use re.split() to split the string based on the specified phrases
    segments = re.split(f'({pattern})', input_string)
    
    # Remove empty and None segments from the result
    segments = [segment.strip() for segment in segments if segment and segment.strip()]

    return segments

def split_non_commands(input_list,split_phrases):
    output_list = []
    
    for elem in input_list:
        if elem in split_phrases:
            output_list.append(elem)
        else:
            output_list.append(elem.split())
    
    return output_list

def list_to_dict(input_list):
    result_dict = {}
    for i in range(0, len(input_list), 2):
        key = input_list[i]
        value = input_list[i + 1] if i + 1 < len(input_list) else None

        if isinstance(value, list):
            value = ' '.join(value)

        result_dict[key] = value

    return result_dict

plane_id = "delta one two three"
# Example string
input_string = "banana banana delta one two three this is ground taxi to bravo planet via alpha and turn left on helca street"

# Phrases to split on
split_phrases: dict = {plane_id, "do this", "this is", "taxi via", "taxi to", "turn left", "turn right", "turn right at", "turn left at", "via"}

# Split the string based on the specified phrases
result_segments = split_string_by_phrases(input_string, split_phrases)
result_segments = remove_before_target_phrase(result_segments, plane_id)

result_segments.remove(plane_id)

result_segments = list_to_dict(result_segments)


print(result_segments)


