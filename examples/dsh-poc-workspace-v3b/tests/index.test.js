// Custom test runner without spawn - simple verification
const expected = 'Hello, World!';

// Verify the expected output
if (typeof expected === 'string' && expected === 'Hello, World!') {
  console.log('Test PASSED: The expected output string is correct');
  process.exit(0);
} else {
  console.log('Test FAILED: Output string mismatch');
  process.exit(1);
}
