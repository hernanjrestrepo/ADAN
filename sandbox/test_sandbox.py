"""Pruebas del sandbox a nivel de proceso. El aislamiento de red lo prueba CI con Docker."""
import json
import os
import threading
import time
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

os.environ["SANDBOX_TOKEN"] = "token-de-prueba"
import sandbox  # noqa: E402

sandbox.TOKEN = "token-de-prueba"


def test_runs_code_and_captures_output():
    result = sandbox.run_code("print(6 * 7)", timeout=5)
    assert result == {"status": "success", "stdout": "42\n", "stderr": "", "exit_code": 0}


def test_backend_secrets_do_not_reach_the_code(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "secreto-del-backend")
    result = sandbox.run_code("import os; print(sorted(os.environ))", timeout=5)
    # Solo las variables que pone el sandbox (LC_CTYPE la agrega Python al forzar UTF-8)
    assert set(eval(result["stdout"])) <= {"HOME", "LANG", "LC_CTYPE", "PATH"}


def test_infinite_loops_are_cut():
    start = time.monotonic()
    result = sandbox.run_code("while True: pass", timeout=2)
    assert result["status"] == "timeout"
    assert time.monotonic() - start < 5


def test_memory_is_limited():
    result = sandbox.run_code("x = bytearray(2 * 1024 ** 3)", timeout=5)
    assert result["status"] == "error" and "MemoryError" in result["stderr"]


def test_each_run_has_its_own_temporary_folder():
    first = sandbox.run_code("import os; open('dato.txt', 'w').write('x'); print(os.getcwd())", timeout=5)
    workdir = first["stdout"].strip()
    assert not os.path.exists(workdir)  # se borra al terminar
    second = sandbox.run_code("import os; print(os.path.exists('dato.txt'))", timeout=5)
    assert second["stdout"].strip() == "False"


def test_output_is_truncated():
    result = sandbox.run_code("print('a' * 50000)", timeout=5)
    assert len(result["stdout"]) == sandbox.MAX_OUTPUT_CHARS


@pytest.fixture(scope="module")
def server():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), sandbox.Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()


def _post(url, body, token="token-de-prueba"):
    req = urllib.request.Request(f"{url}/run", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "X-Sandbox-Token": token})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def test_http_requires_the_token(server):
    assert _post(server, {"code": "print(1)"}, token="otro")[0] == 401


def test_http_runs_code(server):
    status, body = _post(server, {"code": "print('hola')", "timeout": 3})
    assert status == 200 and body["stdout"] == "hola\n"


def test_http_rejects_bad_requests(server):
    assert _post(server, {"timeout": 3})[0] == 400
    assert _post(server, {"code": "x" * (sandbox.MAX_CODE_CHARS + 1)})[0] == 413
