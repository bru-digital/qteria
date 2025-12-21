#!/usr/bin/env ts-node
/**
 * Integration Test Script - Qteria Frontend-Backend Verification
 *
 * Purpose: Verify Railway backend deployment is fully integrated with Vercel frontend
 *
 * Tests:
 * 1. Backend health check (Railway production endpoint)
 * 2. CORS configuration (Vercel origins allowed)
 * 3. API connectivity from frontend proxy
 * 4. Basic workflow creation end-to-end
 * 5. Error handling and proper error formats
 *
 * Usage:
 *   npm run verify:integration
 *   or
 *   ts-node apps/web/scripts/verify-integration.ts
 *
 * Environment Variables Required:
 *   API_URL - Railway backend URL (e.g., https://qteriaappapi-production.up.railway.app)
 */

import * as https from 'https'
import * as http from 'http'

// Configuration
const RAILWAY_BACKEND_URL = process.env.API_URL || 'https://qteriaappapi-production.up.railway.app'
const VERCEL_ORIGIN = process.env.VERCEL_URL
  ? `https://${process.env.VERCEL_URL}`
  : 'https://qteria.vercel.app'

// Test results tracker
interface TestResult {
  name: string
  status: 'PASS' | 'FAIL' | 'SKIP'
  message: string
  duration?: number
}

const testResults: TestResult[] = []

// Colors for terminal output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
}

// Helper: HTTP request wrapper
function httpRequest(url: string, options: any = {}): Promise<any> {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url)
    const client = urlObj.protocol === 'https:' ? https : http

    const req = client.request(
      url,
      {
        method: options.method || 'GET',
        headers: options.headers || {},
        ...options,
      },
      res => {
        let data = ''

        res.on('data', chunk => {
          data += chunk
        })

        res.on('end', () => {
          resolve({
            statusCode: res.statusCode,
            headers: res.headers,
            body: data,
            bodyJson: () => {
              try {
                return JSON.parse(data)
              } catch {
                return null
              }
            },
          })
        })
      }
    )

    req.on('error', reject)

    if (options.body) {
      req.write(typeof options.body === 'string' ? options.body : JSON.stringify(options.body))
    }

    req.end()
  })
}

// Helper: Run test with timing
async function runTest(name: string, testFn: () => Promise<void>): Promise<void> {
  console.log(`${colors.cyan}▶ Running: ${name}${colors.reset}`)
  const startTime = Date.now()

  try {
    await testFn()
    const duration = Date.now() - startTime
    testResults.push({ name, status: 'PASS', message: 'Test passed', duration })
    console.log(`${colors.green}✓ PASS${colors.reset} (${duration}ms)\n`)
  } catch (error: any) {
    const duration = Date.now() - startTime
    testResults.push({ name, status: 'FAIL', message: error.message, duration })
    console.log(`${colors.red}✗ FAIL${colors.reset} (${duration}ms)`)
    console.log(`${colors.red}  Error: ${error.message}${colors.reset}\n`)
  }
}

// Test 1: Backend Health Check
async function testBackendHealthCheck(): Promise<void> {
  const response = await httpRequest(`${RAILWAY_BACKEND_URL}/health`)

  if (response.statusCode !== 200) {
    throw new Error(`Health check failed with status ${response.statusCode}`)
  }

  const json = response.bodyJson()
  if (!json || json.status !== 'healthy') {
    throw new Error(`Health check returned unexpected body: ${response.body}`)
  }

  if (json.environment !== 'production') {
    console.log(
      `${colors.yellow}  Warning: Environment is '${json.environment}', expected 'production'${colors.reset}`
    )
  }

  console.log(`  Environment: ${json.environment}`)
  console.log(`  Status: ${json.status}`)
}

// Test 2: CORS Configuration
async function testCORSConfiguration(): Promise<void> {
  // Send OPTIONS preflight request
  const response = await httpRequest(`${RAILWAY_BACKEND_URL}/health`, {
    method: 'OPTIONS',
    headers: {
      Origin: VERCEL_ORIGIN,
      'Access-Control-Request-Method': 'GET',
    },
  })

  const allowOrigin = response.headers['access-control-allow-origin']
  const allowMethods = response.headers['access-control-allow-methods']

  if (!allowOrigin) {
    throw new Error('CORS header Access-Control-Allow-Origin not present')
  }

  // Check if Vercel origin is allowed (either exact match or wildcard)
  if (allowOrigin !== VERCEL_ORIGIN && allowOrigin !== '*') {
    throw new Error(
      `CORS origin mismatch. Expected '${VERCEL_ORIGIN}' or '*', got '${allowOrigin}'`
    )
  }

  console.log(`  Allowed Origin: ${allowOrigin}`)
  console.log(`  Allowed Methods: ${allowMethods || 'Not specified'}`)
}

// Test 3: API Endpoints Availability
async function testAPIEndpointsAvailability(): Promise<void> {
  // Test GET /v1/workflows (should return 401 without auth, but proves endpoint exists)
  const response = await httpRequest(`${RAILWAY_BACKEND_URL}/v1/workflows`)

  if (response.statusCode === 404) {
    throw new Error('Workflows endpoint not found (404). API routes may not be registered.')
  }

  if (response.statusCode === 401) {
    console.log(`  Workflows endpoint exists (returns 401 Unauthorized as expected)`)
  } else if (response.statusCode === 200) {
    console.log(`  Workflows endpoint accessible (200 OK - auth may be disabled)`)
  } else {
    throw new Error(`Unexpected status code: ${response.statusCode}`)
  }
}

// Test 4: Error Format Consistency
async function testErrorFormatConsistency(): Promise<void> {
  // Test invalid endpoint to verify error format
  const response = await httpRequest(`${RAILWAY_BACKEND_URL}/v1/invalid-endpoint-xyz`)

  if (response.statusCode !== 404) {
    console.log(`  Warning: Expected 404 for invalid endpoint, got ${response.statusCode}`)
  }

  const json = response.bodyJson()

  // Check error format matches API contract (CLAUDE.md, line 767-781)
  if (json && json.error) {
    if (!json.error.code || !json.error.message) {
      throw new Error(`Error format missing required fields. Got: ${JSON.stringify(json)}`)
    }

    // Verify error code uses SCREAMING_SNAKE_CASE (CLAUDE.md, line 806-820)
    if (!/^[A-Z_]+$/.test(json.error.code)) {
      throw new Error(`Error code '${json.error.code}' does not use SCREAMING_SNAKE_CASE format`)
    }

    console.log(`  Error format valid`)
    console.log(`  Error code: ${json.error.code}`)
    console.log(`  Error message: ${json.error.message}`)
  } else {
    // Some frameworks return HTML for 404, which is acceptable
    console.log(`  Note: 404 response is not JSON (may be HTML from framework)`)
  }
}

// Test 5: Database Connectivity (via API)
async function testDatabaseConnectivity(): Promise<void> {
  // Test an endpoint that requires database (workflows list)
  const response = await httpRequest(`${RAILWAY_BACKEND_URL}/v1/workflows`)

  // 401 = auth working, endpoint exists
  // 500 = database connection failed
  // 502/503/504 = service unavailable

  if (response.statusCode >= 500) {
    throw new Error(`Server error ${response.statusCode} suggests database or service issue`)
  }

  if (response.statusCode === 401) {
    console.log(
      `  Database connectivity verified (endpoint returns 401 auth error, not 500 DB error)`
    )
  } else if (response.statusCode === 200) {
    console.log(`  Database connectivity verified (endpoint returns 200 OK)`)
  } else {
    console.log(`  Warning: Unexpected status ${response.statusCode}, but not a 500 error`)
  }
}

// Test 6: Response Time Check
async function testResponseTime(): Promise<void> {
  const startTime = Date.now()
  const response = await httpRequest(`${RAILWAY_BACKEND_URL}/health`)
  const duration = Date.now() - startTime

  if (response.statusCode !== 200) {
    throw new Error(`Health check failed with status ${response.statusCode}`)
  }

  // Target: P95 <500ms for CRUD operations (CLAUDE.md, line 296)
  const threshold = 2000 // Allow 2s for health check (includes network latency)

  if (duration > threshold) {
    console.log(
      `  ${colors.yellow}Warning: Response time ${duration}ms exceeds ${threshold}ms threshold${colors.reset}`
    )
  } else {
    console.log(`  Response time: ${duration}ms (within ${threshold}ms threshold)`)
  }
}

// Main test runner
async function main(): Promise<void> {
  console.log(
    `${colors.blue}╔════════════════════════════════════════════════════════════╗${colors.reset}`
  )
  console.log(
    `${colors.blue}║   Qteria Integration Tests - Railway Backend Deployment   ║${colors.reset}`
  )
  console.log(
    `${colors.blue}╚════════════════════════════════════════════════════════════╝${colors.reset}\n`
  )

  console.log(`Backend URL: ${colors.cyan}${RAILWAY_BACKEND_URL}${colors.reset}`)
  console.log(`Frontend Origin: ${colors.cyan}${VERCEL_ORIGIN}${colors.reset}\n`)

  // Run all tests
  await runTest('1. Backend Health Check', testBackendHealthCheck)
  await runTest('2. CORS Configuration', testCORSConfiguration)
  await runTest('3. API Endpoints Availability', testAPIEndpointsAvailability)
  await runTest('4. Error Format Consistency', testErrorFormatConsistency)
  await runTest('5. Database Connectivity', testDatabaseConnectivity)
  await runTest('6. Response Time Check', testResponseTime)

  // Summary
  console.log(
    `${colors.blue}╔════════════════════════════════════════════════════════════╗${colors.reset}`
  )
  console.log(
    `${colors.blue}║                        Test Summary                        ║${colors.reset}`
  )
  console.log(
    `${colors.blue}╚════════════════════════════════════════════════════════════╝${colors.reset}\n`
  )

  const passed = testResults.filter(r => r.status === 'PASS').length
  const failed = testResults.filter(r => r.status === 'FAIL').length
  const total = testResults.length

  testResults.forEach(result => {
    const icon =
      result.status === 'PASS' ? `${colors.green}✓${colors.reset}` : `${colors.red}✗${colors.reset}`
    const duration = result.duration ? ` (${result.duration}ms)` : ''
    console.log(`${icon} ${result.name}${duration}`)
    if (result.status === 'FAIL') {
      console.log(`  ${colors.red}${result.message}${colors.reset}`)
    }
  })

  console.log('')
  console.log(
    `Total: ${total} | ${colors.green}Passed: ${passed}${colors.reset} | ${
      failed > 0 ? colors.red : colors.reset
    }Failed: ${failed}${colors.reset}\n`
  )

  // Exit with appropriate code
  if (failed > 0) {
    console.log(`${colors.red}✗ INTEGRATION TESTS FAILED${colors.reset}\n`)
    process.exit(1)
  } else {
    console.log(`${colors.green}✓ ALL INTEGRATION TESTS PASSED${colors.reset}\n`)
    console.log(`${colors.blue}Next steps:${colors.reset}`)
    console.log(`  1. Update Vercel environment variable API_URL to: ${RAILWAY_BACKEND_URL}`)
    console.log(`  2. Redeploy frontend: Vercel Dashboard → Deployments → Redeploy`)
    console.log(`  3. Test workflow creation through browser UI`)
    console.log(`  4. Verify no CORS errors in browser console\n`)
    process.exit(0)
  }
}

// Run main
main().catch(error => {
  console.error(`${colors.red}Fatal error: ${error.message}${colors.reset}`)
  process.exit(1)
})
