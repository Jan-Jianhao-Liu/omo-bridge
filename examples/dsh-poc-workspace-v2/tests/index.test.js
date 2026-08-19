import { test, describe } from 'node:test';
import { execSync } from 'child_process';

const expectedOutput = "Hello, World!";

describe('Hello World', () => {
  test('should output Hello, World!', () => {
    const output = execSync('node src/index.js', { encoding: 'utf8', cwd: 'D:\\Workbuddy_Projects\\2026-08-19-21-56-47\\omo-bridge\\examples\\dsh-poc-workspace-v2' });
    
    if (output.trim() !== expectedOutput) {
      throw new Error('Expected "' + expectedOutput + '" but got "' + output.trim() + '"');
    }
  });
});
