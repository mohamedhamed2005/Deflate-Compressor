# main.py
import sys
import os
from lz77 import lz77_compress
from symbolizing import symbolize_deflate
from custom_header_and_payload import generate_compressed_data, get_bw
from decompression import decompress_logic
from huffman_logic import build_huffman_lengths, get_canonical_map
from bit_io import BitWriter


def load_bytes(filepath):
    with open(filepath, "rb") as f:
        return bytearray(f.read())


def compute_frequencies(deflate_symbols):
    """Compute frequencies from deflate symbols."""
    lit_freq = [0] * 286
    dist_freq = [0] * 30
    
    for token in deflate_symbols:
        if token[0] == "LIT":
            lit_freq[token[1]] += 1
        elif token[0] == "LEN":
            lit_freq[token[1]] += 1
        elif token[0] == "DIST":
            dist_freq[token[1]] += 1
        elif token[0] == "EOB":
            lit_freq[256] += 1
    
    return lit_freq, dist_freq


def get_payload_bits_only(events, lit_lengths, dist_lengths):
    """
    Generate ONLY the payload bits (no header) for display purposes.
    """
    writer = BitWriter()
    
    # Generate canonical codes
    lit_codes = get_canonical_map(lit_lengths)
    dist_codes = get_canonical_map(dist_lengths)
    
    # Write payload only
    for ev in events:
        if ev[0] == "LIT":
            writer.write_raw_string(lit_codes[ev[1]])
        elif ev[0] == "LEN":
            writer.write_raw_string(lit_codes[ev[1]])
            if ev[2] > 0:
                writer.write_bits(ev[3], ev[2])
        elif ev[0] == "DIST":
            writer.write_raw_string(dist_codes[ev[1]])
            if ev[2] > 0:
                writer.write_bits(ev[3], ev[2])
        elif ev[0] == "EOB":
            writer.write_raw_string(lit_codes[256])
    
    return writer.bits


def compress(input_path):
    """Compress a file and display event stream and payload bits."""
    print(f"Compressing: {input_path}")
    
    # Load input
    data = load_bytes(input_path)
    print(f"Input size: {len(data)} bytes")
    
    # Stage 1: LZ77
    print("\n[Stage 1] Running LZ77 compression...")
    tokens = lz77_compress(data)
    print(f"LZ77 tokens: {len(tokens)}")
    
    # Display LZ77 tokens
    print("\n[LZ77 Tokens]:")
    for i, token in enumerate(tokens):
        if token[0] == "Literal":
            print(f"  {i}: Literal({token[1]})")
        else:
            print(f"  {i}: Match(length={token[1]}, distance={token[2]})")
    
    # Stage 2: Symbolize
    print("\n[Stage 2] Converting to DEFLATE symbols...")
    deflate_symbols = symbolize_deflate(tokens)
    print(f"DEFLATE symbols: {len(deflate_symbols)}")
    
    # Display event stream
    print("\n[Event Stream]:")
    for ev in deflate_symbols:
        if ev[0] == "LIT":
            print(f"  LiteralEvent({ev[1]})")
        elif ev[0] == "LEN":
            print(f"  MatchEvent(len_sym={ev[1]}, len_extra={ev[3] if ev[2] > 0 else ''}, bits={ev[2]})")
        elif ev[0] == "DIST":
            print(f"    dist_sym={ev[1]}, dist_extra={ev[3] if ev[2] > 0 else ''}, bits={ev[2]}")
        elif ev[0] == "EOB":
            print(f"  EndEvent(256)")
    
    # Stage 3: Build Huffman codes
    print("\n[Stage 3] Building Huffman codes...")
    lit_freq, dist_freq = compute_frequencies(deflate_symbols)
    
    print("\n[Frequencies] Literal/Length:")
    for sym, freq in enumerate(lit_freq):
        if freq > 0:
            if sym <= 255:
                print(f"  {sym}: {freq}")
            elif sym == 256:
                print(f"  EOB(256): {freq}")
            else:
                print(f"  Length {sym}: {freq}")
    
    print("\n[Frequencies] Distance:")
    for sym, freq in enumerate(dist_freq):
        if freq > 0:
            print(f"  {sym}: {freq}")
    
    lit_lengths = build_huffman_lengths(lit_freq, 286)
    dist_lengths = build_huffman_lengths(dist_freq, 30)
    
    print("\n[Code Lengths] Literal/Length:")
    for sym, length in enumerate(lit_lengths):
        if length > 0:
            if sym <= 255:
                print(f"  {sym}: {length}")
            elif sym == 256:
                print(f"  EOB(256): {length}")
            else:
                print(f"  Length {sym}: {length}")
    
    print("\n[Code Lengths] Distance:")
    for sym, length in enumerate(dist_lengths):
        if length > 0:
            print(f"  {sym}: {length}")
    
    # Generate canonical codes
    lit_codes = get_canonical_map(lit_lengths)
    dist_codes = get_canonical_map(dist_lengths)
    
    print("\n[Canonical Codes] Literal/Length:")
    sorted_codes = sorted(lit_codes.items(), key=lambda x: (len(x[1]), x[0]))
    for sym, code in sorted_codes:
        if sym <= 255:
            print(f"  {sym}: {code}")
        elif sym == 256:
            print(f"  EOB(256): {code}")
        else:
            print(f"  Length {sym}: {code}")
    
    print("\n[Canonical Codes] Distance:")
    for sym, code in dist_codes.items():
        print(f"  {sym}: {code}")
    
    # Stage 4: Show payload bits
    print("\n[Stage 4] Payload bits:")
    payload_bits = get_payload_bits_only(deflate_symbols, lit_lengths, dist_lengths)
    print(f"  {payload_bits}")
    print(f"  Total payload bits: {len(payload_bits)}")
    
    # Show payload construction
    print("\n[Payload Construction]:")
    lit_codes_display = get_canonical_map(lit_lengths)
    dist_codes_display = get_canonical_map(dist_lengths)
    
    for ev in deflate_symbols:
        if ev[0] == "LIT":
            code = lit_codes_display[ev[1]]
            print(f"  LiteralEvent({ev[1]}) → {code}")
        elif ev[0] == "LEN":
            code = lit_codes_display[ev[1]]
            extra = f" + {ev[3]:0{ev[2]}b}" if ev[2] > 0 else ""
            print(f"  MatchEvent(len_sym={ev[1]}) → {code}{extra}")
        elif ev[0] == "DIST":
            code = dist_codes_display[ev[1]]
            extra = f" + {ev[3]:0{ev[2]}b}" if ev[2] > 0 else ""
            print(f"    dist_sym={ev[1]} → {code}{extra}")
        elif ev[0] == "EOB":
            code = lit_codes_display[256]
            print(f"  EndEvent(256) → {code}")
    
    # Generate full compressed file
    print("\n[Generating compressed file...]")
    compressed_data = generate_compressed_data(deflate_symbols, lit_lengths, dist_lengths)
    
    # Write compressed file
    output_path = input_path + ".sdfl"
    with open(output_path, "wb") as f:
        f.write(compressed_data)
    
    print(f"\n[Success] Successfully compressed!")
    print(f"  Input:  {len(data)} bytes")
    print(f"  Output: {len(compressed_data)} bytes")
    print(f"  Saved to: {output_path}")


def decompress(input_path):
    """Decompress a file and display information."""
    print(f"Decompressing: {input_path}")
    
    # Load compressed data
    data = load_bytes(input_path)
    print(f"Compressed size: {len(data)} bytes")
    
    # Decompress
    original = decompress_logic(data)
    
    # Write output
    output_path = input_path.replace(".sdfl", "")
    if output_path == input_path:
        output_path = input_path + ".decompressed"
    
    with open(output_path, "wb") as f:
        f.write(original)
    
    print(f"\n[Success] Successfully decompressed!")
    print(f"  Input:  {len(data)} bytes")
    print(f"  Output: {len(original)} bytes")
    print(f"  Saved to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py -c <file> OR python main.py -d <file>")
        print("  -c : compress file")
        print("  -d : decompress file (.sdfl expected)")
        sys.exit(1)
    
    mode = sys.argv[1]
    path = sys.argv[2]
    
    if mode == "-c":
        compress(path)
    elif mode == "-d":
        decompress(path)
    else:
        print(f"Unknown mode: {mode}")
        print("Use -c for compression or -d for decompression")
        sys.exit(1)