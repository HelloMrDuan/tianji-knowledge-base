def transform(bits: str, operation: str, changing_lines=()) -> str:
    """All six-line strings are bottom to top; no interpretation is generated."""
    if len(bits) != 6 or set(bits) - {'0', '1'}:
        raise ValueError('Expected six binary characters')
    lines = tuple(changing_lines)
    if len(set(lines)) != len(lines) or any(type(n) is not int or not 1 <= n <= 6 for n in lines):
        raise ValueError('Changing lines must be unique integers 1..6')
    if operation != 'change' and lines:
        raise ValueError('Changing lines only apply to change')
    if operation == 'compose':
        return bits  # lower three + upper three, already concatenated
    if operation == 'opposite':
        return ''.join('0' if c == '1' else '1' for c in bits)
    if operation == 'inverse':
        return bits[::-1]
    if operation == 'nuclear':
        return bits[1:4] + bits[2:5]
    if operation == 'change':
        return ''.join(('0' if c == '1' else '1') if i + 1 in lines else c for i, c in enumerate(bits))
    raise ValueError('Unknown operation')
