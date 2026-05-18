# symbolizing.py
# Format: (code, extra_bits, min_length, max_length)
LENGTH_CODES = [
    (257, 0, 3, 3), (258, 0, 4, 4), (259, 0, 5, 5), (260, 0, 6, 6),
    (261, 0, 7, 7), (262, 0, 8, 8), (263, 0, 9, 9), (264, 0, 10, 10),
    (265, 1, 11, 12), (266, 1, 13, 14), (267, 1, 15, 16), (268, 1, 17, 18),
    (269, 2, 19, 22), (270, 2, 23, 26), (271, 2, 27, 30), (272, 2, 31, 34),
    (273, 3, 35, 42), (274, 3, 43, 50), (275, 3, 51, 58), (276, 3, 59, 66),
    (277, 4, 67, 82), (278, 4, 83, 98), (279, 4, 99, 114), (280, 4, 115, 130),
    (281, 5, 131, 162), (282, 5, 163, 194), (283, 5, 195, 226), (284, 5, 227, 257),
    (285, 0, 258, 258)
]

# Format: (code, extra_bits, min_dist, max_dist)
DISTANCE_CODES = [
    (0, 0, 1, 1), (1, 0, 2, 2), (2, 0, 3, 3), (3, 0, 4, 4),
    (4, 1, 5, 6), (5, 1, 7, 8), (6, 2, 9, 12), (7, 2, 13, 16),
    (8, 3, 17, 24), (9, 3, 25, 32), (10, 4, 33, 48), (11, 4, 49, 64),
    (12, 5, 65, 96), (13, 5, 97, 128), (14, 6, 129, 192), (15, 6, 193, 256),
    (16, 7, 257, 384), (17, 7, 385, 512), (18, 8, 513, 768), (19, 8, 769, 1024),
    (20, 9, 1025, 1536), (21, 9, 1537, 2048), (22, 10, 2049, 3072), (23, 10, 3073, 4096),
    (24, 11, 4097, 6144), (25, 11, 6145, 8192), (26, 12, 8193, 12288), (27, 12, 12289, 16384),
    (28, 13, 16385, 24576), (29, 13, 24577, 32768)
]

def get_length_symbol(length):
    """Finds the Deflate length code and extra bits for a given LZ77 length."""
    for code, extra_bits, min_val, max_val in LENGTH_CODES:
        if min_val <= length <= max_val:
            extra_val = length - min_val
            return code, extra_bits, extra_val
    raise ValueError(f"Invalid length: {length}")

def get_distance_symbol(distance):
    """Finds the Deflate distance code and extra bits for a given LZ77 distance."""
    for code, extra_bits, min_val, max_val in DISTANCE_CODES:
        if min_val <= distance <= max_val:
            extra_val = distance - min_val
            return code, extra_bits, extra_val
    raise ValueError(f"Invalid distance: {distance}")

def symbolize_deflate(lz77_tokens):
    """
    Converts a list of LZ77 tokens into DEFLATE symbols ready for Huffman encoding.
    """
    deflate_symbols = []
    
    for token in lz77_tokens:
        if token[0] == "Literal":
            deflate_symbols.append(("LIT", token[1]))
            
        elif token[0] == "Match":
            # Token format: ("Match", length, distance)
            length = token[1]
            distance = token[2]
            
            # Process Length
            len_code, len_ext_bits, len_ext_val = get_length_symbol(length)
            deflate_symbols.append(("LEN", len_code, len_ext_bits, len_ext_val))
            
            # Process Distance
            dist_code, dist_ext_bits, dist_ext_val = get_distance_symbol(distance)
            deflate_symbols.append(("DIST", dist_code, dist_ext_bits, dist_ext_val))
    
    # Append End of Block (EOB) symbol
    deflate_symbols.append(("EOB", 256))
    
    return deflate_symbols