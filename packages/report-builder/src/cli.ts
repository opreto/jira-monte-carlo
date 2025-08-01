#!/usr/bin/env node

// Polyfill for browser globals in Node.js environment
if (typeof self === 'undefined') {
  global.self = global as any
}

import { Command } from 'commander'
import fs from 'fs'
import path from 'path'
import { ReportRenderer } from './renderer'
import { ReportData } from './types'

const program = new Command()

program
  .name('sprint-radar-report-builder')
  .description('Build static HTML reports for Sprint Radar')
  .version('1.0.0')

program
  .command('build')
  .description('Build a report from JSON data')
  .option('-i, --input <path>', 'Input JSON file path', '-')
  .option('-o, --output <path>', 'Output HTML file path', 'report.html')
  .action(async (options) => {
    try {
      // Read input data
      let jsonData: string
      if (options.input === '-') {
        // Read from stdin
        jsonData = await readStdin()
      } else {
        // Read from file
        jsonData = fs.readFileSync(options.input, 'utf8')
      }

      // Parse JSON
      const data: ReportData = JSON.parse(jsonData)

      // Create renderer
      const renderer = new ReportRenderer()

      // Generate HTML
      console.error('Generating HTML report...')
      const html = await renderer.generateHTML(data)

      // Write output
      const outputPath = path.resolve(options.output)
      fs.writeFileSync(outputPath, html, 'utf8')
      console.error(`Report generated: ${outputPath}`)
      
      // Exit successfully
      process.exit(0)
    } catch (error) {
      console.error('Error generating report:', error)
      process.exit(1)
    }
  })

program.parse()

// Helper function to read from stdin
function readStdin(): Promise<string> {
  return new Promise((resolve, reject) => {
    let data = ''
    process.stdin.setEncoding('utf8')
    
    process.stdin.on('data', (chunk) => {
      data += chunk
    })
    
    process.stdin.on('end', () => {
      resolve(data)
    })
    
    process.stdin.on('error', (err) => {
      reject(err)
    })
  })
}