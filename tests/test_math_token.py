import re

def tokenize_math(text: str):
    pattern = re.compile(
        r'(\$\$([\s\S]*?)\$\$)'
        r'|(\\\[([\s\S]*?)\\\])'
        r'|((?<!\\)\$((?:\\\$|[^\$])+?)\$)'
        r'|(\\\(([\s\S]*?)\\\))'
    )
    pos = 0
    tokens = []
    for m in pattern.finditer(text):
        start, end = m.span()
        if start > pos:
            tokens.append(('text', text[pos:start]))
        if m.group(1): # $$...$$
            tokens.append(('display_math', m.group(2)))
        elif m.group(3): # \[...\]
            tokens.append(('display_math', m.group(4)))
        elif m.group(5): # $...$
            tokens.append(('inline_math', m.group(6)))
        elif m.group(7): # \(...\)
            tokens.append(('inline_math', m.group(8)))
        pos = end

    if pos < len(text):
        tokens.append(('text', text[pos:]))
    return tokens

if __name__ == '__main__':
    q = r"If $\begin{vmatrix} x & 2 \\ 8 & x \end{vmatrix} = 0$, what is the value of $x$?"
    tokens = tokenize_math(q)
    for t in tokens:
        print(t)
