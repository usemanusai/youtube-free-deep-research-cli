#!/usr/bin/env node

/**
 * NPM Publishing Script for JAEGIS YouTube Chat MCP Server
 * 
 * This script handles the complete npm publishing process including:
 * - Package validation
 * - Building the package
 * - Publishing to npm
 * - Testing the published package
 */

const { spawn, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Colors for output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function error(message) {
  log(`❌ ${message}`, 'red');
}

function success(message) {
  log(`✅ ${message}`, 'green');
}

function info(message) {
  log(`ℹ️  ${message}`, 'blue');
}

function warning(message) {
  log(`⚠️  ${message}`, 'yellow');
}

async function runCommand(command, args = [], options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { 
      stdio: 'inherit', 
      shell: true,
      ...options 
    });
    
    child.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`Command failed with exit code ${code}`));
      }
    });
    
    child.on('error', reject);
  });
}

function getPackageInfo() {
  const packagePath = path.join(__dirname, '..', 'package.json');
  return JSON.parse(fs.readFileSync(packagePath, 'utf8'));
}

async function validatePackage() {
  info('Validating package configuration...');
  
  const pkg = getPackageInfo();
  
  // Check required fields
  const requiredFields = ['name', 'version', 'description', 'main', 'bin'];
  for (const field of requiredFields) {
    if (!pkg[field]) {
      throw new Error(`Missing required field: ${field}`);
    }
  }
  
  // Check if dist directory exists
  const distPath = path.join(__dirname, '..', 'dist');
  if (!fs.existsSync(distPath)) {
    throw new Error('dist/ directory not found. Run npm run build first.');
  }
  
  // Check if main file exists
  const mainFile = path.join(__dirname, '..', pkg.main);
  if (!fs.existsSync(mainFile)) {
    throw new Error(`Main file not found: ${pkg.main}`);
  }
  
  // Check if bin file exists
  const binFile = path.join(__dirname, '..', pkg.bin['jaegis-youtube-chat-mcp']);
  if (!fs.existsSync(binFile)) {
    throw new Error(`Bin file not found: ${pkg.bin['jaegis-youtube-chat-mcp']}`);
  }
  
  success('Package validation passed');
  return pkg;
}

async function buildPackage() {
  info('Building package...');
  
  try {
    await runCommand('npm', ['run', 'build']);
    success('Package built successfully');
  } catch (error) {
    throw new Error(`Build failed: ${error.message}`);
  }
}

async function testPackage() {
  info('Testing package...');
  
  try {
    // Test that the main file can be required
    const mainFile = path.join(__dirname, '..', 'dist', 'index.js');
    require(mainFile);
    success('Package loads successfully');
  } catch (error) {
    throw new Error(`Package test failed: ${error.message}`);
  }
}

async function publishPackage(testMode = false) {
  const pkg = getPackageInfo();
  
  if (testMode) {
    info('Publishing to npm (dry run)...');
    try {
      await runCommand('npm', ['publish', '--dry-run']);
      success('Dry run completed successfully');
    } catch (error) {
      throw new Error(`Dry run failed: ${error.message}`);
    }
  } else {
    info(`Publishing ${pkg.name}@${pkg.version} to npm...`);
    
    // Check if already published
    try {
      const output = execSync(`npm view ${pkg.name}@${pkg.version}`, { encoding: 'utf8' });
      if (output) {
        throw new Error(`Version ${pkg.version} already exists on npm`);
      }
    } catch (error) {
      // Version doesn't exist, which is good
    }
    
    try {
      await runCommand('npm', ['publish', '--access', 'public']);
      success(`Successfully published ${pkg.name}@${pkg.version}`);
    } catch (error) {
      throw new Error(`Publish failed: ${error.message}`);
    }
  }
}

async function verifyPublication() {
  const pkg = getPackageInfo();
  
  info('Verifying publication...');
  
  try {
    // Wait a moment for npm to propagate
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    const output = execSync(`npm view ${pkg.name}@${pkg.version}`, { encoding: 'utf8' });
    if (output) {
      success('Package successfully published and available on npm');
      
      // Show installation instructions
      log('\n📦 Installation Instructions:', 'cyan');
      log(`npm install -g ${pkg.name}`, 'green');
      log(`npx ${pkg.name}`, 'green');
      
      return true;
    }
  } catch (error) {
    warning('Could not verify publication immediately. It may take a few minutes to propagate.');
  }
  
  return false;
}

async function main() {
  const args = process.argv.slice(2);
  const isDryRun = args.includes('--dry-run') || args.includes('--test');
  
  log('🎙️ JAEGIS YouTube Chat MCP Server - NPM Publisher', 'magenta');
  log('=' * 60, 'magenta');
  
  try {
    // Step 1: Validate package
    const pkg = await validatePackage();
    log(`\n📦 Package: ${pkg.name}@${pkg.version}`, 'cyan');
    
    // Step 2: Build package
    await buildPackage();
    
    // Step 3: Test package
    await testPackage();
    
    // Step 4: Publish package
    await publishPackage(isDryRun);
    
    // Step 5: Verify publication (only for real publish)
    if (!isDryRun) {
      await verifyPublication();
      
      log('\n🎉 Publication completed successfully!', 'green');
      log('\nNext steps:', 'cyan');
      log('1. Test installation: npm install -g jaegis-youtube-chat-mcp', 'blue');
      log('2. Test execution: npx jaegis-youtube-chat-mcp', 'blue');
      log('3. Update documentation with npm installation instructions', 'blue');
    } else {
      log('\n✅ Dry run completed successfully!', 'green');
      log('Run without --dry-run to publish for real.', 'blue');
    }
    
  } catch (error) {
    error(`Publication failed: ${error.message}`);
    process.exit(1);
  }
}

// Handle command line arguments
if (process.argv.includes('--help') || process.argv.includes('-h')) {
  log('JAEGIS YouTube Chat MCP Server - NPM Publisher', 'cyan');
  log('');
  log('Usage:', 'yellow');
  log('  node scripts/publish-npm.js [options]', 'blue');
  log('');
  log('Options:', 'yellow');
  log('  --dry-run, --test    Perform a dry run without actually publishing', 'blue');
  log('  --help, -h          Show this help message', 'blue');
  log('');
  log('Examples:', 'yellow');
  log('  node scripts/publish-npm.js --dry-run    # Test the publishing process', 'blue');
  log('  node scripts/publish-npm.js              # Publish to npm', 'blue');
  process.exit(0);
}

if (require.main === module) {
  main();
}
