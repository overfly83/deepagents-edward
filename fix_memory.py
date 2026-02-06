import json
import os
import re

# Read the current file
with open('src/memory/short_term_memory.py', 'r') as f:
    content = f.read()

# Add json import if not present
if 'import json' not in content:
    content = 'import json\n' + content

# Fix add_message method with regex
content = re.sub(
    r'content = self\.backend\.read\(file_path\)[^\n]+\n[^\n]+json\.loads\(content\)',
    r'content = self.backend.read(file_path)\n            if content and content != "File not found":\n                try:\n                    messages = json.loads(content)\n                except json.JSONDecodeError:\n                    messages = []',
    content
)

# Fix get_memory method with regex
content = re.sub(
    r'content = self\.backend\.read\(file_path\)[^\n]+\n[^\n]+json\.loads\(content\)',
    r'content = self.backend.read(file_path)\n            if content and content != "File not found":\n                try:\n                    messages = json.loads(content)\n                except json.JSONDecodeError:\n                    return []',
    content
)

# Write the changes back
with open('src/memory/short_term_memory.py', 'w') as f:
    f.write(content)

print('Fix applied successfully!')