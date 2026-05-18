from bit_io import BitReader
from huffman_logic import get_canonical_map
from symbolizing import LENGTH_CODES, DISTANCE_CODES

def rebuild_codes(lengths):
    """Rebuild canonical codes from lengths."""
    if not lengths or max(lengths) == 0:
        return {}
    
    code_map = get_canonical_map(lengths)
    # Reverse map: code string -> symbol
    return {v: k for k, v in code_map.items()}


def decompress_logic(data):
    """Decompress data and return original bytes."""
    reader = BitReader(data)
    
    # Read header
    l_bw = reader.read_bits(4)
    d_bw = reader.read_bits(4)
    
    print(f"[Debug] l_bw={l_bw}, d_bw={d_bw}")
    
    # Read literal/length code lengths
    lit_lengths = []
    for i in range(286):
        lit_lengths.append(reader.read_bits(l_bw))
    
    # Read distance code lengths
    dist_lengths = []
    for i in range(30):
        dist_lengths.append(reader.read_bits(d_bw))
    
    # Debug: Show non-zero code lengths
    print(f"[Debug] Non-zero literal/length code lengths: {[(i, l) for i, l in enumerate(lit_lengths) if l > 0][:10]}")
    print(f"[Debug] Non-zero distance code lengths: {[(i, l) for i, l in enumerate(dist_lengths) if l > 0]}")
    
    # Rebuild code maps
    lit_codes = rebuild_codes(lit_lengths)  # string -> symbol
    dist_codes = rebuild_codes(dist_lengths)  # string -> symbol
    
    print(f"[Debug] Literal codes built: {len(lit_codes)} entries")
    print(f"[Debug] Distance codes built: {len(dist_codes)} entries")
    
    # Prepare lookup tables for lengths and distances
    len_table = {}
    for c in LENGTH_CODES:
        code, extra_bits, min_val, max_val = c
        len_table[code] = (extra_bits, min_val)
    
    dist_table = {}
    for c in DISTANCE_CODES:
        code, extra_bits, min_val, max_val = c
        dist_table[code] = (extra_bits, min_val)
    
    output = bytearray()
    total_bits = len(reader.bits)
    
    while reader.pos < total_bits:
        # Read literal/length symbol
        curr = ""
        max_bits = min(15, total_bits - reader.pos)  # Max code length is 15
        found = False
        
        for _ in range(max_bits):
            bit = reader.read_bit()
            if bit is None:
                break
            curr += bit
            if curr in lit_codes:
                found = True
                break
        
        if not found:
            print(f"[Debug] Could not find code: {curr}")
            break
            
        sym = lit_codes[curr]
        
        if 0 <= sym <= 255:
            # Literal
            output.append(sym)
        elif sym == 256:
            # EOB
            break
        elif 257 <= sym <= 285:
            # Match - decode length
            extra_bits, base_len = len_table[sym]
            length = base_len
            if extra_bits > 0:
                extra_val = reader.read_bits(extra_bits)
                length += extra_val
            
            # Decode distance
            curr_d = ""
            max_bits_d = min(15, total_bits - reader.pos)
            found_d = False
            
            for _ in range(max_bits_d):
                bit = reader.read_bit()
                if bit is None:
                    break
                curr_d += bit
                if curr_d in dist_codes:
                    found_d = True
                    break
            
            if not found_d:
                print(f"[Debug] Could not find distance code: {curr_d}")
                break
                
            dist_sym = dist_codes[curr_d]
            d_extra_bits, base_dist = dist_table[dist_sym]
            distance = base_dist
            if d_extra_bits > 0:
                extra_val = reader.read_bits(d_extra_bits)
                distance += extra_val
            
            # Copy match (supporting overlapping)
            # Ensure distance is valid
            if distance > len(output):
                print(f"[Debug] Invalid distance: {distance} > output size {len(output)}")
                print(f"[Debug] dist_sym={dist_sym}, base_dist={base_dist}, extra_bits={d_extra_bits}")
                # This indicates a bug - maybe we misread
                # Return what we have so far for debugging
                return output
            
            for i in range(length):
                output.append(output[-distance])
        else:
            # Invalid symbol
            print(f"[Debug] Invalid symbol: {sym}")
            break
    
    return output