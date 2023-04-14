import sys

"""Repare encoding issues with non ascii characters."""
replacement = {
    "\\\\X2\\\\00E9\\\\X0\\\\": "é",
    "\\\\X2\\\\00E8\\\\X0\\\\": "è",
    "\\\\X2\\\\00E0\\\\X0\\\\": "à",
    "\\\\X2\\\\00E7\\\\X0\\\\": "ç",
    "\\\\X2\\\\00E2\\\\X0\\\\": "â",
    "\\\\X2\\\\00C9\\\\X0\\\\": "É",
    "\\\\X2\\\\2019\\\\X0\\\\": "'",
    "\\\\X\\\\0D\\\\X\\\\0A": "\\n",
    "\\\\X2\\\\00B0\\\\X0\\\\": "°",
    "\\\\X2\\\\00F8\\\\X0\\\\": "ø",
    "\\\\X2\\\\00D8\\\\X0\\\\": "Ø",
    "\\\\X2\\\\00A0\\\\X0\\\\": " ", # nbsp
    
    
}

if __name__ == "__main__":
    if len(sys.argv) != 3:
        exit(1)
    with open(sys.argv[1]) as input, open(sys.argv[2], 'w') as output:
        content = input.read()
        for key, value in replacement.items():
            content = content.replace(key, value)
        output.write(content)
