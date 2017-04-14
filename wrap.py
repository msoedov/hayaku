import argparse

import fire
from pigar.reqs import file_import_modules, is_stdlib
from pyminifier.minification import minify
from pyminifier.token_utils import listified_tokenizer


dockerfile = """
FROM python:3.6

# MAINTAINER {{maintainer}}

WORKDIR /app

RUN pip install {requirements}


ENV PY_EXEC "{body}"

CMD python -c "import os;b=os.getenv('PY_EXEC');b=b.replace('1l', '\\n');exec(b)"

"""

def read_from(path):
    with open(path, "r") as fp:
        return fp.read()



def generate(module):

    source = read_from(module)
    modules = file_import_modules('', source)[0]
    req = [m for m, v in modules.items() if not is_stdlib(m)]
    req = ' '.join(req)
    tokens = listified_tokenizer(source)
    compressed = minify(tokens, argparse.Namespace(tabs=False))
    compressed = compressed.replace('\"', '\'').replace('\n', '1l')
    print(dockerfile.format(requirements=req, body=compressed))


fire.Fire(generate)
