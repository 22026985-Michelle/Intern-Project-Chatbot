import random
import re

def generate_checksum(prefix, year_digits, random_digits):
    """Generate the checksum for NRIC/FIN"""
    weights = [2, 7, 6, 5, 4, 3, 2]
    prefix_value = 0 if prefix in ['S', 'T'] else 4
    all_digits = [prefix_value] + [int(d) for d in (year_digits + random_digits)]
    total = sum(d * w for d, w in zip(all_digits, weights))
    offset = 0 if prefix in ['S', 'F'] else 4
    remainder = (offset + total) % 11
    
    if prefix in ['S', 'T']:
        checksum_chars = ['J', 'Z', 'I', 'H', 'G', 'F', 'E', 'D', 'C', 'B', 'A']
    else:  # F or G
        checksum_chars = ['X', 'W', 'U', 'T', 'R', 'Q', 'P', 'N', 'M', 'L', 'K']
    
    return checksum_chars[remainder]

def generate_nric(prefix, year):
    """Generate a single valid NRIC/FIN number"""
    year_digits = str(year)[-2:]  
    random_digits = ''.join(random.choices('0123456789', k=5))
    checksum = generate_checksum(prefix, year_digits, random_digits)
    return f"{prefix}{year_digits}{random_digits}{checksum}"

def parse_nric_request(message):
    """Parse the NRIC generation request message"""
    pattern = r"Please generate (\d+) NRICs issued in (\d{4}), of prefix ([STFG])"
    match = re.match(pattern, message)
    if match:
        count = int(match.group(1))
        year = int(match.group(2))
        prefix = match.group(3)
        return count, year, prefix
    return None

def handle_nric_request(message):
    """Handle NRIC generation request and return appropriate response"""
    parsed = parse_nric_request(message)
    if not parsed:
        return "Please use the format: 'Please generate 𝘯𝘶𝘮𝘣𝘦𝘳 NRICs issued in 𝘺𝘦𝘢𝘳, of prefix 𝘚 | 𝘛 | 𝘍 | 𝘎'"
    
    count, year, prefix = parsed
    
    if count <= 0 or count > 10:
        return "Please request between 1 and 10 NRICs at a time."
    if year < 1900 or year > 2024:
        return "Please use a valid year between 1900 and 2024."
    
    # Generate the NRICs
    nrics = [generate_nric(prefix, year) for _ in range(count)]
    
    # Format response with each NRIC on a new line
    response = f"Generated {count} NRICs with prefix {prefix} for year {year}:\n\n"
    response += "\n".join(nrics)
        
    return response