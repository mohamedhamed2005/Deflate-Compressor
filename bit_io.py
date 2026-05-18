class BitWriter:
    def __init__(self):
        self.bits = ""

    def write_bits(self, value, count):
        """Writes 'count' bits of 'value' in MSB order."""
        # Ensure value fits in count bits
        value = value & ((1 << count) - 1)
        self.bits += bin(value)[2:].zfill(count)

    def write_raw_string(self, bit_str):
        self.bits += bit_str

    def get_bytes(self):
        """Pads the end of the bitstream with zeros to reach a full byte."""
        while len(self.bits) % 8 != 0:
            self.bits += "0"
        return bytes(int(self.bits[i:i+8], 2) for i in range(0, len(self.bits), 8))


class BitReader:
    def __init__(self, data):
        self.bits = "".join(bin(b)[2:].zfill(8) for b in data)
        self.pos = 0

    def read_bits(self, count):
        if self.pos + count > len(self.bits):
            return 0
        val = int(self.bits[self.pos:self.pos + count], 2)
        self.pos += count
        return val

    def read_bit(self):
        if self.pos >= len(self.bits):
            return None
        bit = self.bits[self.pos]
        self.pos += 1
        return bit
    
    def read_raw_bits(self, count):
        if self.pos + count > len(self.bits):
            return ""
        bits = self.bits[self.pos:self.pos + count]
        self.pos += count
        return bits
    
    def bits_remaining(self):
        return len(self.bits) - self.pos