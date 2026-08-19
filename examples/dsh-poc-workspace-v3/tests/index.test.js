import { test, describe } from 'node:test';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = fileURLToPath(new URL('.', import.meta.url));

describe('Hello World tests', () => {
  test('Hello World should output expected text', () => {
    const result = spawn('node', ['src/index.js'], {
      cwd: `${__dirname}/..`
    });

    let output = '';
    result.stdout.on('data', (data) => {
      output += data.toString();
    });

    result.on('close', (code) => {
      if (output === 'Hello, World!') {
        result.exitCode === 0 ? test.pass() : test.fail();
      }
    });

    result.on('error', () => {
      test.fail('Failed to execute process');
    });
  });
});
