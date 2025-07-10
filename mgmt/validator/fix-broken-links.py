#!/usr/bin/env python3
"""Fix broken ID links based on discovered mappings."""

import os
import re
import sys

# Mappings from broken IDs to correct IDs
ID_MAPPINGS = {
    # Critical Scattering Form
    '4d3a9bc0-c8b2-43ff-bcaa-393f584e194d': 'e361a82a-9085-4566-9e2d-803e22bd473b',
    
    # Mermin-Wagner Theorem
    '15028591-0c87-4a11-b5de-f0360439042a': '9302663d-a632-4e0a-98d3-f9506fb0ab92',
    
    # Two-Dimensional Physics
    'e0883a37-4d29-4fe1-b4f3-1f182755b53d': '8db469c1-ca8a-4d69-bc33-16e51908a8a3',
    
    # Functional Determinants
    '02d3c7e4-c09b-4809-a1c4-989d154ea5bc': '67c747dc-64e5-4d38-93c7-c3041d7e51d1',
    
    # Ginzburg Region
    '39cbb004-8f52-4220-9b8d-46cae5d84138': '50c6effe-fc5a-4304-a7bd-8376b7de5df6',
    
    # Coherence Lengths ξ₀
    'fde40a31-429d-4163-bfce-f255f164b51c': '946d05e3-fc1f-4924-a6ba-ba74c10ffde7',
    
    # Correlation Decay Regimes
    'ad9411f3-56cd-489b-ae7e-d011257e4329': 'c26b66f5-ded0-4426-bf02-2dcf8b35114b',
}

def fix_broken_links(file_path):
    """Fix broken ID links in a file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    changes_made = []
    
    for old_id, new_id in ID_MAPPINGS.items():
        # Pattern to match [[id:old_id][Description]]
        pattern = rf'\[\[id:{re.escape(old_id)}\]\[([^\]]+)\]\]'
        
        # Check if this pattern exists
        if re.search(pattern, content):
            # Replace with new ID
            new_link = rf'[[id:{new_id}][\1]]'
            content = re.sub(pattern, new_link, content)
            changes_made.append(f"  - {old_id} → {new_id}")
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return changes_made
    
    return []

def main():
    """Main function to fix broken links."""
    slips_dir = '/home/b/documents/slipbox/slips'
    
    if not os.path.exists(slips_dir):
        print(f"Error: Directory {slips_dir} not found")
        sys.exit(1)
    
    print("Fixing broken ID links...")
    print(f"\nFound {len(ID_MAPPINGS)} ID mappings to fix")
    
    total_files_fixed = 0
    total_links_fixed = 0
    
    # Process all .org files
    for filename in os.listdir(slips_dir):
        if filename.endswith('.org'):
            file_path = os.path.join(slips_dir, filename)
            changes = fix_broken_links(file_path)
            
            if changes:
                print(f"\nFixed {filename}:")
                for change in changes:
                    print(change)
                total_files_fixed += 1
                total_links_fixed += len(changes)
    
    print(f"\nSummary:")
    print(f"- Files fixed: {total_files_fixed}")
    print(f"- Links fixed: {total_links_fixed}")
    
    # Show the mapping details
    print("\nID Mappings used:")
    print("1. Critical Scattering Form")
    print("2. Mermin-Wagner Theorem")
    print("3. Two-Dimensional Physics")
    print("4. Functional Determinants")
    print("5. Ginzburg Region")
    print("6. Coherence Lengths ξ₀")
    print("7. Correlation Decay Regimes")

if __name__ == '__main__':
    main()