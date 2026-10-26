def multiply(a, b):
    if type(a) is not int or type(b) is not int:
        raise ValueError("Both inputs must be whole numbers.")

    if not (0 <= a <= 1_000_000 and 0 <= b <= 1_000_000):
        raise ValueError("Inputs must be between 0 and 1,000,000.")

    return a * b

MULTIPLY_TOOL = {
    "type": "function",
    "function": {
        "name": "multiply",
        "description": "Multiply two whole numbers between 0 and 1,000,000.",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "integer", "minimum": 0, "maximum": 1_000_000},
                "b": {"type": "integer", "minimum": 0, "maximum": 1_000_000},
            },
            "required": ["a", "b"],
            "additionalProperties": False,
        },
    },
}

if __name__ == "__main__":
    print(multiply(18, 24))