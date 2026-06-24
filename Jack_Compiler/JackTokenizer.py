import re
import os

KEYWORDS = {'class', 'constructor', 'method', 'function','field', 'static', 'var','int', 'char', 'boolean', 'void','true', 'false', 'null', 'this',
            'let', 'do', 'if', 'else', 'while', 'return'}

SYMBOLS = set('{}()[].,;+-*/&|<>=~')

ESCAPE = {'<':  '&lt;','>':  '&gt;','&':  '&amp;','"':  '&quot;',"'":  '&apos;',}


def xml_escape(text):
    for ch, esc in ESCAPE.items():
        text = text.replace(ch, esc)
    return text

class JackTokenizer:

    def __init__(self, filepath):
        self.filepath = filepath
        self.tokens = [] 


    def tokenize(self) :
 
        with open(self.filepath, 'r', encoding='utf-8') as fh:
            source = fh.read()

        cleaned = self.strip_comments(source)
        self.tokens = self.scan(cleaned)
        self.write_xml()
        return self.tokens

    def strip_comments(self, src):

        result = []
        i = 0
        n = len(src)

        IN_CODE       = 0
        IN_LINE_CMT   = 1
        IN_BLOCK_CMT  = 2
        IN_STRING     = 3

        state = IN_CODE

        while i < n:
            ch = src[i]

            if state == IN_CODE:
                if ch == '"':
                    state = IN_STRING
                    result.append(ch)
                    i += 1
                elif ch == '/' and i + 1 < n and src[i + 1] == '/':
                    state = IN_LINE_CMT
                    i += 2
                elif ch == '/' and i + 1 < n and src[i + 1] == '*':
                    state = IN_BLOCK_CMT
                    i += 2
                else:
                    result.append(ch)
                    i += 1

            elif state == IN_LINE_CMT:
                if ch == '\n':
                    result.append('\n')  
                    state = IN_CODE
                i += 1

            elif state == IN_BLOCK_CMT:
                if ch == '*' and i + 1 < n and src[i + 1] == '/':
                    state = IN_CODE
                    i += 2
                else:
                    if ch == '\n':
                        result.append('\n')
                    i += 1

            elif state == IN_STRING:
                result.append(ch)
                if ch == '"':
                    state = IN_CODE
                i += 1

        return ''.join(result)


    def scan(self, src):

        token_pattern = re.compile(
            r'"([^"\n]*)"'          # group 1 – string constant 
            r'|(\d+)'               # group 2 – integer constant
            r'|([A-Za-z_]\w*)'     # group 3 – identifier or keyword
            r'|([{}()\[\].,;+\-*/&|<>=~])'  # group 4 – symbol
            )

        tokens = []

        for m in token_pattern.finditer(src):
            g1, g2, g3, g4 = m.group(1), m.group(2), m.group(3), m.group(4)
            if g1 is not None:
                tokens.append(('stringConstant', g1))
            elif g2 is not None:
                val = int(g2)
                if val > 32767:
                    raise ValueError(f'Integer constant {val} out of range [0, 32767]')
                tokens.append(('integerConstant', g2))
            elif g3 is not None:
                if g3 in KEYWORDS:
                    tokens.append(('keyword', g3))
                else:
                    tokens.append(('identifier', g3))
            elif g4 is not None:
                tokens.append(('symbol', g4))
        return tokens


    def write_xml(self):

        basename   = os.path.splitext(os.path.basename(self.filepath))[0]
        out_dir    = os.path.dirname(self.filepath)
        xml_path   = os.path.join(out_dir, basename + 'T.xml')

        lines = ['<tokens>']
        for tok_type, value in self.tokens:
            safe = xml_escape(value)
            lines.append(f'  <{tok_type}> {safe} </{tok_type}>')
        lines.append('</tokens>')

        with open(xml_path, 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(lines) + '\n')

        self._xml_path = xml_path
