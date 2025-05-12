#!/usr/bin/env node

const { execSync } = require('child_process');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log('CT-5 Platform - Vercel Deployment Helper');
console.log('----------------------------------------');
console.log('This script will help you deploy your CT-5 frontend to Vercel.');
console.log('');

rl.question('Enter your backend API URL (e.g., https://your-backend-api.com): ', (backendUrl) => {
  if (!backendUrl) {
    console.error('Error: Backend API URL is required.');
    rl.close();
    return;
  }

  if (!backendUrl.startsWith('http')) {
    console.error('Error: Backend API URL must start with http:// or https://');
    rl.close();
    return;
  }

  console.log(`\nUpdating vercel.json with backend URL: ${backendUrl}`);
  
  try {
    // Read the vercel.json file
    const fs = require('fs');
    const vercelConfigPath = './vercel.json';
    const vercelConfig = JSON.parse(fs.readFileSync(vercelConfigPath, 'utf8'));
    
    // Update the rewrites destination and environment variable
    vercelConfig.rewrites[0].destination = `${backendUrl}/api/:path*`;
    vercelConfig.env.NEXT_PUBLIC_API_URL = backendUrl;
    
    // Write the updated config back to the file
    fs.writeFileSync(vercelConfigPath, JSON.stringify(vercelConfig, null, 2));
    
    console.log('vercel.json updated successfully.');
    
    rl.question('\nDo you want to deploy to Vercel now? (y/n): ', (answer) => {
      if (answer.toLowerCase() === 'y') {
        console.log('\nDeploying to Vercel...');
        try {
          execSync('vercel', { stdio: 'inherit' });
          console.log('\nDeployment initiated. Follow the instructions in the terminal.');
        } catch (error) {
          console.error('\nError deploying to Vercel:', error.message);
          console.log('\nYou can deploy manually by running: vercel');
        }
      } else {
        console.log('\nYou can deploy manually by running: vercel');
      }
      rl.close();
    });
  } catch (error) {
    console.error('Error updating vercel.json:', error.message);
    rl.close();
  }
});
