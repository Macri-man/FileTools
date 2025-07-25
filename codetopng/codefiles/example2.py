def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)

# Example usage
number = 5
result = factorial(number)
print(f"The factorial of {number} is {result}")
