WINDOW_SIZE = 32768  
MIN_MATCH   = 3       
MAX_MATCH   = 258     
MAX_CANDIDATES = 64   


def get_key(data, pos):
    return (data[pos], data[pos + 1], data[pos + 2])  # 3 byte key hash_table


def insert_position(hash_table, data, pos):
    if pos + MIN_MATCH <= len(data):
        key = get_key(data, pos)
        if key not in hash_table:
            hash_table[key] = []
        hash_table[key].append(pos)


def find_match(data, pos, hash_table):
    
    if pos + MIN_MATCH > len(data):  # least 3 bytes to form a key
        return None

    key = get_key(data, pos)
    candidates = hash_table.get(key, [])

    best_length   = 0
    best_distance = 0

    start_idx = max(0, len(candidates) - MAX_CANDIDATES)
    for candidate_pos in reversed(candidates[start_idx:]):
        distance = pos - candidate_pos

        if distance > WINDOW_SIZE:
            break

        length = 0
        while (length < MAX_MATCH and
               pos + length < len(data) and
               data[candidate_pos + length] == data[pos + length]):
            length += 1

        
        if length > best_length or (length == best_length and distance < best_distance):
            best_length   = length
            best_distance = distance

    if best_length >= MIN_MATCH:
        return (best_length, best_distance)

    return None


def make_literal(byte_value):

    return ("Literal", byte_value)


def make_match(length, distance):

    return ("Match", length, distance)


def lz77_compress(data):
    hash_table  = {}   
    tokens = []
    pos    = 0

    while pos < len(data):
        result = find_match(data, pos, hash_table)

        if result is not None:
            length, distance = result

            
            tokens.append(make_match(length, distance))

            for k in range(length):
                insert_position(hash_table, data, pos + k)

            pos += length

        else:
            tokens.append(make_literal(data[pos]))
            insert_position(hash_table, data, pos)
            pos += 1

    return tokens


def lz77_decompress(tokens):
    
    output = bytearray()

    for token in tokens:
        if token[0] == "Literal":
            output.append(token[1])

        elif token[0] == "Match":
            length   = token[1]
            distance = token[2]

           
            start = len(output) - distance
            for i in range(length):
                
                output.append(output[start + i])

    return output