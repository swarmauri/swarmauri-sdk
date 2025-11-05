// generate-index.js

const fs = require('fs');
const path = require('path');

// Path to the components directory
const componentsDir = path.join(__dirname, 'src', 'components');
const indexFilePath = path.join(__dirname, 'src', 'index.ts');

// Helper function to recursively find all .svelte files in componentsDir
function findSvelteFiles(dir) {
  let svelteFiles = [];
  const files = fs.readdirSync(dir);

  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);

    if (stat.isDirectory()) {
      svelteFiles = svelteFiles.concat(findSvelteFiles(filePath));
    } else if (file.endsWith('.svelte')) {
      svelteFiles.push(filePath);
    }
  });

  return svelteFiles;
}

// Generate export statements for each .svelte file
const svelteFiles = findSvelteFiles(componentsDir);
const exportStatements = svelteFiles.map(filePath => {
  const relativePath = path.relative(path.join(__dirname, 'src'), filePath);
  const componentName = path.basename(filePath, '.svelte');
  return `export { default as ${componentName} } from './${relativePath.replace(/\\/g, '/')}';`;
});

// Write to index.ts
fs.writeFileSync(indexFilePath, exportStatements.join('\n'), 'utf-8');
console.log(`Generated ${indexFilePath} with exports for ${svelteFiles.length} components.`);
