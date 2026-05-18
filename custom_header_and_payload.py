import math
from bit_io import BitWriter
from huffman_logic import get_canonical_map

def get_bw(lengths):
    """Section 5.3: floor(log2(M)) + 1"""
    max_len = max(lengths) if lengths else 0
    if max_len == 0:
        return 0
    # Note: If max_len is 1, log2(1)=0, floor=0, +1 = 1 (correct)
    return math.floor(math.log2(max_len)) + 1


def generate_huffman_codes(lengths):
    """Generate canonical Huffman codes from lengths."""
    return get_canonical_map(lengths)


def generate_compressed_data(events, lit_lengths, dist_lengths):
    """
    Generate compressed data from events and code lengths.
    
    Args:
        events: List of events from symbolize_deflate
        lit_lengths: Code lengths for literal/length symbols (size 286)
        dist_lengths: Code lengths for distance symbols (size 30)
    
    Returns:
        bytes: Compressed data
    """
    writer = BitWriter()
    
    # Generate canonical codes
    lit_codes = get_canonical_map(lit_lengths)
    dist_codes = get_canonical_map(dist_lengths)
    
    # Compute bit-widths
    l_bw = get_bw(lit_lengths)
    d_bw = get_bw(dist_lengths)
    
    # Write header
    writer.write_bits(l_bw, 4)
    writer.write_bits(d_bw, 4)
    
    # Write literal/length code lengths
    for length in lit_lengths:
        writer.write_bits(length, l_bw)
    
    # Write distance code lengths
    for length in dist_lengths:
        writer.write_bits(length, d_bw)
    
    # Write payload
    for ev in events:
        if ev[0] == "LIT":
            # Literal byte
            writer.write_raw_string(lit_codes[ev[1]])
            
        elif ev[0] == "LEN":
            # Length symbol
            len_code, len_ext_bits, len_ext_val = ev[1], ev[2], ev[3]
            writer.write_raw_string(lit_codes[len_code])
            if len_ext_bits > 0:
                writer.write_bits(len_ext_val, len_ext_bits)
                
        elif ev[0] == "DIST":
            # Distance symbol
            dist_code, dist_ext_bits, dist_ext_val = ev[1], ev[2], ev[3]
            writer.write_raw_string(dist_codes[dist_code])
            if dist_ext_bits > 0:
                writer.write_bits(dist_ext_val, dist_ext_bits)
                
        elif ev[0] == "EOB":
            # End of block
            writer.write_raw_string(lit_codes[256])
    
    return writer.get_bytes()