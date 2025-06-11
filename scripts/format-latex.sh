#!/bin/bash
set -euo pipefail

NODE_ID="${1:-}"
if [ -z "$NODE_ID" ]; then
    echo "Usage: $0 <node-id>"
    exit 1
fi

FILE=$(grep -rl "^:ID:\s*${NODE_ID}$" notes || true)
if [ -z "$FILE" ]; then
    echo "Node not found: ${NODE_ID}"
    exit 1
fi

if ! command -v latexindent >/dev/null 2>&1; then
    echo "Error: latexindent not installed. Install texlive-extra-utils"
    exit 1
fi

python3 - "$FILE" <<'PY'
import sys, re, subprocess, tempfile, os
path = sys.argv[1]
text = open(path).read()

def tidy(code):
    try:
        with tempfile.NamedTemporaryFile('w+', suffix='.tex', delete=False) as tmp:
            tmp.write(code)
            tmp.flush()
            subprocess.run(['latexindent', tmp.name, '-o', tmp.name], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            tmp.seek(0)
            formatted = tmp.read()
        os.unlink(tmp.name)
        return formatted.strip('\n')
    except Exception:
        return code

text = re.sub(r'\$\$(.+?)\$\$', lambda m: '$$'+tidy(m.group(1))+'$$', text, flags=re.S)
text = re.sub(r'\\\[(.+?)\\\]', lambda m: '\['+tidy(m.group(1))+'\]', text, flags=re.S)
pattern = re.compile(r'(#+BEGIN_EXPORT latex\n)(.+?)(#+END_EXPORT)', re.S)
def repl(m):
    return m.group(1)+tidy(m.group(2))+m.group(3)
text = pattern.sub(repl, text)
open(path,'w').write(text)
PY

echo "Formatted LaTeX in: $(basename "$FILE")"

