"""
Script to update logging across all processor files.
Run this to apply consistent logging to all processor modules.
"""
import os
import re
from pathlib import Path

# Get the directory of this script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Pattern to find processor files
processor_pattern = r'^processor_.+\.py$'

# Logging imports to add
LOGGING_IMPORTS = '''from GameCockAI.src.logging_utils import get_processor_logger

logger = get_processor_logger('{module_name}')'''

# Pattern to find existing logging imports
LOGGING_IMPORT_PATTERN = r'import\s+logging\s*\n(?:from\s+logging\s+import\s+.*\n)*'

# Pattern to find basicConfig calls
BASIC_CONFIG_PATTERN = r'logging\.basicConfig\([^)]*\)\s*\n'

def update_file(file_path):
    """Update logging in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get module name from filename
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # Skip if already updated with absolute import
        if 'from src.logging_utils import' in content:
            print(f"Skipping {file_path} - already updated")
            return False
            
        # Replace relative imports with absolute imports
        content = content.replace('from ..logging_utils import', 'from GameCockAI.src.logging_utils import')
        content = content.replace('from src.logging_utils import', 'from GameCockAI.src.logging_utils import')
            
        # Remove basicConfig calls
        content = re.sub(BASIC_CONFIG_PATTERN, '', content)
        
        # Replace logging imports
        if 'import logging' in content:
            content = re.sub(
                LOGGING_IMPORT_PATTERN, 
                LOGGING_IMPORTS.format(module_name=module_name) + '\n', 
                content
            )
        else:
            # Add after last import
            imports_end = max(
                content.rfind('import '),
                content.rfind('from ')
            )
            if imports_end > 0:
                next_newline = content.find('\n', imports_end) + 1
                content = (
                    content[:next_newline] + 
                    '\n' + LOGGING_IMPORTS.format(module_name=module_name) + 
                    '\n\n' + content[next_newline:]
                )
        
        # Update logger names
        content = content.replace('logging.', 'logger.')
        content = re.sub(r'logger\.getLogger\([^)]*\)', 'logger', content)
        
        # Write changes
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Updated {file_path}")
        return True
        
    except Exception as e:
        print(f"Error updating {file_path}: {str(e)}")
        return False

def main():
    """Update all processor files."""
    updated = 0
    errors = 0
    
    for root, _, files in os.walk(current_dir):
        for file in files:
            if re.match(processor_pattern, file):
                file_path = os.path.join(root, file)
                if update_file(file_path):
                    updated += 1
                else:
                    errors += 1
    
    print(f"\nUpdate complete. Updated: {updated}, Errors: {errors}")

if __name__ == "__main__":
    main()
