#!/usr/bin/env python3
"""
Test which parser is actually being used
"""

# Simulate the same import logic as main.py
try:
    from file_parsers import parse_attachments
    print("✅ Successfully imported full file parser")
    parser_type = "full"
except ImportError as e:
    print(f"❌ Full parser import failed: {e}")
    from file_parsers_minimal import parse_attachments
    print("✅ Using minimal file parser")
    parser_type = "minimal"

# Test with a simple attachment
test_attachments = [
    {
        "filename": "test.pdf",
        "contentBase64": "JVBERi0xLjQKJcOkw7zDtsO8CjIgMCBvYmoKPDwKL0xlbmd0aCAzIDAgUgovRmlsdGVyIC9GbGF0ZURlY29kZQo+PgpzdHJlYW0KeJxLSU1MzsjPS1VIzkxPzStRyC9VqFZQqZOqVshNTM5ILU5VyE9VyMnPS1XIyU9VSMssMU1NzQG6sKoOiDNSc2u1XDPz6vKri_JzSlLTUhWKjFQSk0tSczOLKnPS8ouLFUq1kvNTQbIW0KUCxsWZaZUJpakF2dl5mSkpmcklqQpWCrWaQAxqCYBCaQpAUZCKYsXigpzUksy8dCCjNLcosbKk1pKbBwDQQC6rCmVuZHN0cmVhbQplbmRvYmoK"
    }
]

print(f"\nTesting attachment parsing with {parser_type} parser...")
result = parse_attachments(test_attachments, ".")
print(f"Result: {result}")

# Check if it mentions "minimal mode"
if "minimal mode" in result:
    print("❌ Using minimal parser (attachments not processed)")
else:
    print("✅ Using full parser (attachments processed)")