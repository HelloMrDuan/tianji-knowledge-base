#!/usr/bin/env python3
"""TJ-005.2: assembled smoke suite (local controlled only).

BOUNDARY (read before running or citing this script):
- This is a LOCAL controlled smoke suite: it talks to a backend on
  127.0.0.1 (loopback) and a locally built frontend distribution. It
  contains NO real-domain HTTPS check and is NOT proof of a
  production deployment. A GHCR image build succeeding is not a
  production deployment either; nothing here claims otherwise.
- Two modes, and the difference is load-bearing:
  - full: health probe + six-domain execution + OpenAPI (via the
    existing check_api.py) + frontend probe (via health_check.py) +
    static bundle boundary (via check_public_web_bundle.py) +
    permission smoke (inline). Requires an assembled runtime with
    private knowledge data (the /health and /execute paths 503
    without it). Full mode runs in offline acceptance, never in
    public CI.
  - ci: ONLY the checks executable without private data — the static
    bundle boundary on a freshly built dist plus the permission smoke
    against a backend started from public source. It does NOT run
    health/execution checks, because those need the assembled runtime
    that public CI deliberately does not have. CI mode is real
    execution (a live server, real HTTP status codes, a real built
    bundle), not a compileall pass — but it must never be cited as
    full health/execution coverage; that coverage comes from full
    mode in offline acceptance.
- The role tokens below are SYNTHETIC local-test tokens. They match
  nothing in production and are only fed to the loopback backend this
  script itself starts. Never put a production token here.
- Exit 0 only if every step passes. No step is skipped silently: a
  missing backend, a missing dist, or a failed sub-script is a FAIL.

Usage:
  python scripts/smoke_suite.py --mode full --start-backend \
      --start-frontend --dist web/visual-prototype/dist
  python scripts/smoke_suite.py --mode ci --start-backend \
      --dist web/visual-prototype/dist
  python scripts/smoke_suite.py --mode ci \
      --backend-url http://127.0.0.1:8000 --dist <dist>
"""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# Synthetic local-test tokens only (see boundary header).
TEST_ROLE_TOKENS = (
    'user-token:user,editor-token:editor,'
    'reviewer-token:reviewer,publisher-token:publisher'
)

# (label, method, path, token, body, expected_status, expected_code)
PERMISSION_CASES = [
    ('no token -> 401', 'GET', '/api/v1/admin/drafts', None, None,
     401, 'admin_unauthorized'),
    ('invalid token -> 401', 'GET', '/api/v1/admin/drafts',
     'bad-token', None, 401, 'admin_unauthorized'),
    ('user write -> 403', 'POST', '/api/v1/admin/drafts',
     'user-token', {'title': 't', 'body': 'b'}, 403, 'admin_forbidden'),
    ('unknown draft GET -> 404', 'GET', '/api/v1/admin/drafts/D-999999',
     'publisher-token', None, 404, 'draft_not_found'),
    ('unknown draft rollback -> 404', 'POST',
     '/api/v1/admin/drafts/D-999999/rollback',
     'publisher-token', {'version': 1}, 404, 'draft_not_found'),
]


def _http(method, url, token=None, body=None):
    """One HTTP call. Returns (status, parsed_json_dict).

    A dead server raises (connection error), which the caller treats
    as FAIL — never as a skip. A non-JSON body (e.g. the frontend
    preview's HTML) yields {} instead of raising: callers that need a
    JSON code (the permission smoke) then fail honestly on the code
    mismatch, and readiness probes only need the status.
    """
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('Content-Type', 'application/json')
    if token is not None:
        req.add_header('Authorization', f'Bearer {token}')

    def _parse(raw):
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, _parse(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, _parse(exc.read())


def _permission_smoke(backend_url):
    """Real permission responses from a live backend. No mocks."""
    failures = []
    for label, method, path, token, body, want_status, want_code in \
            PERMISSION_CASES:
        try:
            status, payload = _http(
                method, backend_url.rstrip('/') + path, token, body)
        except OSError as exc:
            failures.append(f'{label}: connection failed ({exc})')
            continue
        code = (payload.get('detail') or {}).get('code')
        if status != want_status or code != want_code:
            failures.append(
                f'{label}: got HTTP {status} code {code!r}, '
                f'want HTTP {want_status} code {want_code!r}')
    return failures


def _run_script(script, args, cwd):
    """Run a sub-script. Returns (ok, combined_output)."""
    proc = subprocess.run(
        [sys.executable, str(script)] + args,
        cwd=str(cwd), capture_output=True, text=True, timeout=300)
    output = (proc.stdout + proc.stderr).strip()
    return proc.returncode == 0, output


def _stop(proc):
    """Stop a started server AND its children.

    Servers are started in their own process group (start_new_session)
    because wrappers like `npm run preview` spawn children (sh, node)
    that would otherwise survive a plain terminate() and leak a
    listener into later runs. SIGTERM the group, then SIGKILL it.
    """
    if proc is None or proc.poll() is not None:
        return
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            proc.kill()
        proc.wait(timeout=10)


def _start_backend(repo_root, backend_url):
    """Start uvicorn from public source with synthetic role tokens.

    Returns the Popen object. Readiness is proven by the admin
    endpoint answering 401 without a token (a dead server gives a
    connection error, not a 401). /health is deliberately NOT the
    readiness probe: it 503s without the assembled runtime.
    """
    port = urllib.parse.urlsplit(backend_url).port or 8000
    env = dict(os.environ)
    env['TIANJI_ADMIN_ROLE_TOKENS'] = TEST_ROLE_TOKENS
    env['PYTHONPATH'] = str(repo_root / 'src')
    proc = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'tianji_kb.api:app',
         '--host', '127.0.0.1', '--port', str(port)],
        cwd=str(repo_root), env=env, start_new_session=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    deadline = time.time() + 60
    last_error = None
    while time.time() < deadline:
        if proc.poll() is not None:
            out = proc.stdout.read() if proc.stdout else ''
            raise RuntimeError(
                f'backend exited during startup: {out[-2000:]}')
        try:
            status, _ = _http('GET', backend_url.rstrip('/') +
                              '/api/v1/admin/drafts')
            if status == 401:
                return proc
        except OSError as exc:
            last_error = exc
        time.sleep(1)
    proc.terminate()
    raise RuntimeError(
        f'backend did not answer within 60s (last: {last_error})')


def _start_frontend_preview(repo_root, frontend_url):
    """Start `vite preview` serving the built dist (full mode only)."""
    port = urllib.parse.urlsplit(frontend_url).port or 4174
    proc = subprocess.Popen(
        ['npm', 'run', 'preview', '--', '--port', str(port),
         '--strictPort'],
        cwd=str(repo_root / 'web' / 'visual-prototype'),
        start_new_session=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    deadline = time.time() + 60
    while time.time() < deadline:
        if proc.poll() is not None:
            out = proc.stdout.read() if proc.stdout else ''
            raise RuntimeError(
                f'frontend preview exited during startup: {out[-2000:]}')
        try:
            status, _ = _http('GET', frontend_url.rstrip('/') + '/')
            if status == 200:
                return proc
        except OSError:
            pass
        time.sleep(1)
    proc.terminate()
    raise RuntimeError('frontend preview did not answer within 60s')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['full', 'ci'], required=True,
                        help='full: all checks (needs assembled runtime); '
                             'ci: only checks executable without private data')
    parser.add_argument('--backend-url', default='http://127.0.0.1:8000')
    parser.add_argument('--frontend-url', default='http://127.0.0.1:4174')
    parser.add_argument('--dist', default='web/visual-prototype/dist',
                        help='built frontend distribution directory')
    parser.add_argument('--start-backend', action='store_true',
                        help='start a loopback backend from public source')
    parser.add_argument('--start-frontend', action='store_true',
                        help='start vite preview (full mode only)')
    parser.add_argument('--repo-root', type=Path, default=None)
    args = parser.parse_args()

    repo_root = (args.repo_root or
                 Path(__file__).resolve().parent.parent)
    scripts = repo_root / 'scripts'
    dist = (args.dist if Path(args.dist).is_absolute()
            else repo_root / args.dist)
    results = []  # (name, ok, detail)

    backend_proc = None
    frontend_proc = None
    try:
        if args.start_backend:
            backend_proc = _start_backend(repo_root, args.backend_url)
            results.append(('backend startup (loopback, synthetic '
                            'role tokens)', True, 'answered 401'))
        if args.mode == 'full' and args.start_frontend:
            frontend_proc = _start_frontend_preview(
                repo_root, args.frontend_url)
            results.append(('frontend preview startup', True,
                            'answered 200'))
        if args.mode == 'full':
            ok, out = _run_script(
                scripts / 'check_api.py',
                ['--base-url', args.backend_url], repo_root)
            results.append(('check_api: health + six-domain execution '
                            '+ OpenAPI', ok, out.splitlines()[-1]
                            if out else ''))
            ok, out = _run_script(
                scripts / 'health_check.py',
                ['--api', args.backend_url,
                 '--frontend', args.frontend_url], repo_root)
            results.append(('health_check probe (api + frontend + '
                            'gateway)', ok, out.replace('\n', ' | ')))
        ok, out = _run_script(
            scripts / 'check_public_web_bundle.py', [str(dist)], repo_root)
        results.append(('static bundle boundary', ok, out.splitlines()[-1]
                        if out else ''))
        failures = _permission_smoke(args.backend_url)
        results.append(('permission smoke (401/403/404, live backend)',
                        not failures, '; '.join(failures)))
    except (RuntimeError, OSError) as exc:
        results.append(('smoke harness', False, str(exc)))
    finally:
        for proc in (frontend_proc, backend_proc):
            _stop(proc)

    failed = [r for r in results if not r[1]]
    for name, ok, detail in results:
        print(f'SMOKE {"PASS" if ok else "FAIL"}: {name}'
              + (f' — {detail}' if detail else ''))
    if args.mode == 'ci':
        print('NOTE: ci mode covers bundle + permission checks only; '
              'health/execution checks need the assembled runtime and '
              'run in full mode (offline acceptance), never in public CI.')
    print(f'SMOKE VERDICT: {"PASS" if not failed else "FAIL"} '
          f'({len(results) - len(failed)}/{len(results)})')
    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main())
