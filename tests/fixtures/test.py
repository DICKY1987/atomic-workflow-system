"""
Test Python script for py2atom converter.

This script demonstrates a simple file processing task
that reads input files and produces output.
"""
# pragma: role=processor
# pragma: inputs=data.json,config.yaml
# pragma: outputs=result.json

import json
from pathlib import Path


def process_data(input_file: str) -> dict:
    """Process input data and return results."""
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Process data
    result = {'processed': True, 'count': len(data)}
    
    return result


def main():
    """Main entry point."""
    result = process_data('data.json')
    
    with open('result.json', 'w') as f:
        json.dump(result, f)


if __name__ == '__main__':
    main()
