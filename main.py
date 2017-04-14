import argparse
import os
from subprocess import CalledProcessError, check_output

import fire
from pigar.reqs import file_import_modules, is_stdlib
from pyminifier.minification import minify
from pyminifier.token_utils import listified_tokenizer


dockerfile = """
FROM python:3.6

MAINTAINER {maintainer}

WORKDIR /app

RUN pip install {requirements}


ENV PY_EXEC "{body}"

CMD python -c "import os;b=os.getenv('PY_EXEC');b=b.replace('1l', '\\n');exec(b)"

"""


def read_from(path):
    with open(path, "r") as fp:
        return fp.read()


def write_to(path, data):
    with open(path, "w") as fp:
        return fp.write(data)


def maintainer():
    try:
        name = check_output('git config user.name', shell=True).decode('utf-8').strip(' \n')
        email = check_output('git config user.email', shell=True).decode('utf-8').strip(' \n')
        return '{} <{}>'.format(name, email)
    except CalledProcessError:
        user = os.getenv('USER')
        return '{user} <{user}@localhost>'.format(user=user)


def generate(module, tag=None):
    """
    Pack a python module into Dockerfile one liner
    Build it if tag specified.
    """
    source = read_from(module)
    modules = file_import_modules('', source)[0]
    req = [m for m, v in modules.items() if not is_stdlib(m)]
    req = ' '.join(req)
    tokens = listified_tokenizer(source)
    compressed = minify(tokens, argparse.Namespace(tabs=False))
    compressed = compressed.replace('\"', '\'').replace('\n', '1l')
    artifact = dockerfile.format(requirements=req, body=compressed, maintainer=maintainer())
    if not tag:
        print(artifact)
    else:
        docker_name = 'Docker.gen'
        write_to(docker_name, artifact)
        os.system('docker build -t {tag} -f {docker_name} .'.format(tag=tag, docker_name=docker_name))
        os.remove(docker_name)


fire.Fire(generate)
