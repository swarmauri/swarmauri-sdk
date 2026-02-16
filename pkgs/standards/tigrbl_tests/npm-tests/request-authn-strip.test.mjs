import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';

function runPythonRequestAuthn(headersLiteral) {
  const script = `
import json
from tigrbl.requests import Request

request = Request(
    method="GET",
    path="/authn",
    headers=${headersLiteral},
    query={},
    path_params={},
    body=b"",
)
print(json.dumps({
    "admin_key": request.admin_key,
    "bearer_token": request.bearer_token,
    "session_token": request.session_token,
}))
`;

  const output = execFileSync(
    'uv',
    ['run', '--package', 'tigrbl_tests', '--directory', 'standards', 'python', '-c', script],
    {
      cwd: '/workspace/swarmauri-sdk/pkgs',
      encoding: 'utf8',
    },
  );
  return JSON.parse(output);
}

test('x-admin-key values are stripped by tigrbl Request', () => {
  const result = runPythonRequestAuthn("{'X-Admin-Key': '  admin-secret  '}");

  assert.equal(result.admin_key, 'admin-secret');
});

test('Bearer values are stripped by tigrbl Request session token helpers', () => {
  const result = runPythonRequestAuthn("{'Authorization': 'Bearer   session-token  '}");

  assert.equal(result.bearer_token, 'session-token');
  assert.equal(result.session_token, 'session-token');
});
