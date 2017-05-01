import base64
import os
from subprocess import CalledProcessError, check_output

import fire
from pigar.reqs import file_import_modules, is_stdlib


dockerfile = """
FROM python:{py_version}

MAINTAINER {maintainer}

WORKDIR /app

RUN pip install {requirements}

ENV PY_LIB "{body}"
RUN python -c "import os,base64;b=os.getenv('PY_LIB');b=base64.b64decode(b);print(b.decode('utf-8'))" | tee app.py

CMD python app.py
"""


def read_from(path):
    with open(path, "r") as fp:
        return fp.read()


def write_to(path, data):
    assert not isinstance(data, bytes), "No byte string accepted"
    with open(path, "w") as fp:
        return fp.write(data)


def pack_buffer(buf):
    return base64.b64encode(buf.encode('utf-8')).decode('utf-8')


def maintainer():
    try:
        name = check_output('git config user.name', shell=True).decode('utf-8').strip(' \n')
        email = check_output('git config user.email', shell=True).decode('utf-8').strip(' \n')
        return '{} <{}>'.format(name, email)
    except CalledProcessError:
        user = os.getenv('USER')
        return '{user} <{user}@localhost>'.format(user=user)


def generate(module, tag=None, py_version='3.6'):
    """
    Pack a python module into Dockerfile one liner
    Build it if tag specified.
    """
    source = read_from(module)
    modules = file_import_modules('', source)[0]
    req = [m for m, v in modules.items() if not is_stdlib(m)]
    req = ' '.join(req)
    compressed = pack_buffer(source)
    artifact = dockerfile.format(requirements=req,
                                 body=compressed,
                                 maintainer=maintainer(),
                                 py_version=py_version)
    if not tag:
        print(artifact)
    else:
        docker_name = 'Docker.gen'
        write_to(docker_name, artifact)
        os.system('docker build -t {tag} -f {docker_name} .'.format(tag=tag, docker_name=docker_name))
        os.remove(docker_name)


fire.Fire(generate)
