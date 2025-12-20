#!/usr/bin/env python3
"""
PinkSync Schema Validator

Validates accessibility events and visual states against PinkSync schemas.
"""

import json
import sys
from pathlib import Path


def load_schema(schema_path):
    """Load a JSON schema from file."""
    with open(schema_path, 'r') as f:
        return json.load(f)


def load_example(example_path):
    """Load an example JSON file."""
    with open(example_path, 'r') as f:
        return json.load(f)


def validate_basic(data, schema):
    """Basic validation without jsonschema library."""
    errors = []
    
    # Check required fields
    if 'required' in schema:
        for field in schema['required']:
            if field not in data:
                errors.append(f"Missing required field: {field}")
    
    # Check field types
    if 'properties' in schema:
        for field, field_schema in schema['properties'].items():
            if field in data:
                expected_type = field_schema.get('type')
                if expected_type == 'string' and not isinstance(data[field], str):
                    errors.append(f"Field '{field}' should be string")
                elif expected_type == 'integer' and not isinstance(data[field], int):
                    errors.append(f"Field '{field}' should be integer")
                elif expected_type == 'boolean' and not isinstance(data[field], bool):
                    errors.append(f"Field '{field}' should be boolean")
                elif expected_type == 'object' and not isinstance(data[field], dict):
                    errors.append(f"Field '{field}' should be object")
                elif expected_type == 'array' and not isinstance(data[field], list):
                    errors.append(f"Field '{field}' should be array")
    
    return errors


def main():
    specs_dir = Path(__file__).parent
    examples_dir = specs_dir / 'examples'
    
    print("PinkSync Schema Validator")
    print("=" * 60)
    
    # Validate accessibility events
    print("\nValidating Accessibility Events...")
    print("-" * 60)
    
    event_schema = load_schema(specs_dir / 'accessibility-intent.schema.json')
    event_examples = [
        'event-emergency-alert.json',
        'event-captions-mandatory.json',
        'event-sign-language.json'
    ]
    
    for example_file in event_examples:
        try:
            example = load_example(examples_dir / example_file)
            errors = validate_basic(example, event_schema)
            
            if not errors:
                print(f"✓ {example_file}: VALID")
            else:
                print(f"✗ {example_file}: INVALID")
                for error in errors:
                    print(f"  - {error}")
        except Exception as e:
            print(f"✗ {example_file}: ERROR - {e}")
    
    # Validate visual states
    print("\nValidating Visual States...")
    print("-" * 60)
    
    visual_schema = load_schema(specs_dir / 'sign-visual-state.schema.json')
    visual_examples = [
        'visual-state-asl-hd.json',
        'visual-state-recorded-tutorial.json'
    ]
    
    for example_file in visual_examples:
        try:
            example = load_example(examples_dir / example_file)
            errors = validate_basic(example, visual_schema)
            
            if not errors:
                print(f"✓ {example_file}: VALID")
            else:
                print(f"✗ {example_file}: INVALID")
                for error in errors:
                    print(f"  - {error}")
        except Exception as e:
            print(f"✗ {example_file}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print("Validation complete!")
    print("\nNote: For full JSON Schema validation, install jsonschema:")
    print("  pip install jsonschema")
    print("  jsonschema -i examples/event.json accessibility-intent.schema.json")


if __name__ == '__main__':
    main()
