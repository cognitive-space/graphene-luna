from pathlib import Path

import pytest

from python_graphql_client import GraphqlClient
from xprocess import ProcessStarter


@pytest.fixture
def ws_client(xprocess):
    class Starter(ProcessStarter):
        # startup pattern
        pattern = "Application startup complete"

        # command to start process
        args = ['gunicorn', 'lunastarter.asgi:application', '-k', 'uvicorn.workers.UvicornWorker']

        popen_kwargs = {
            "cwd": str(Path(__file__).parent.parent)
        }

    # ensure process is running and return its logfile
    pid, logpath = xprocess.ensure("gunicorn", Starter)

    client = GraphqlClient(endpoint="ws://localhost:8000/graphql")
    yield client

    # clean up whole process tree afterwards
    xprocess.getinfo("gunicorn").terminate()
