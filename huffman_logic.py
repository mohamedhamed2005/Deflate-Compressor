# huffman_logic.py
import heapq

def build_huffman_lengths(freqs, limit):
    """Build Huffman code lengths from frequencies using priority queue."""
    class Node:
        def __init__(self, freq, symbol=None, left=None, right=None):
            self.freq = freq
            self.symbol = symbol
            self.left = left
            self.right = right
        
        def __lt__(self, other):
            if self.freq != other.freq:
                return self.freq < other.freq
            # Tie-break by smallest symbol in subtree
            return self._min_symbol() < other._min_symbol()
        
        def _min_symbol(self):
            if self.symbol is not None:
                return self.symbol
            left_min = self.left._min_symbol() if self.left else float('inf')
            right_min = self.right._min_symbol() if self.right else float('inf')
            return min(left_min, right_min)

    # Count used symbols
    used_count = sum(1 for f in freqs if f > 0)
    
    if used_count == 0:
        return [0] * limit
    
    if used_count == 1:
        # Special case: only one symbol, assign length 1
        return [1 if f > 0 else 0 for f in freqs]
    
    # Build heap with leaf nodes
    heap = []
    nodes = [None] * limit
    
    for i, f in enumerate(freqs):
        if f > 0:
            node = Node(f, i)
            nodes[i] = node
            heapq.heappush(heap, node)
    
    # Build Huffman tree
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        parent = Node(left.freq + right.freq, None, left, right)
        heapq.heappush(heap, parent)
    
    root = heap[0]
    
    # Extract code lengths via DFS
    lengths = [0] * limit
    
    def dfs(node, depth):
        if not node:
            return
        if node.symbol is not None:
            lengths[node.symbol] = depth
            return
        dfs(node.left, depth + 1)
        dfs(node.right, depth + 1)
    
    dfs(root, 0)
    
    return lengths


def get_canonical_map(lengths):
    """
    Convert code lengths to canonical Huffman codes.
    Returns a dict mapping symbol -> binary string.
    """
    if not lengths:
        return {}
    
    # Get symbols that have non-zero length
    symbols_with_length = [(symbol, length) for symbol, length in enumerate(lengths) if length > 0]
    if not symbols_with_length:
        return {}
    
    # Sort by length, then by symbol
    symbols_with_length.sort(key=lambda x: (x[1], x[0]))
    
    # Count how many symbols have each length
    max_len = max(lengths)
    count = [0] * (max_len + 2)
    for _, length in symbols_with_length:
        count[length] += 1
    
    # Compute first code for each length
    next_code = [0] * (max_len + 2)
    code = 0
    for bits in range(1, max_len + 1):
        code = (code + count[bits - 1]) << 1
        next_code[bits] = code
    
    # Assign codes to symbols
    code_map = {}
    for symbol, length in symbols_with_length:
        code_map[symbol] = format(next_code[length], f'0{length}b')
        next_code[length] += 1
    
    return code_map