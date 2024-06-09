import re

# Define the string to be searched
string = "Hello, World!, Hello"

# Define the regular expression pattern
pattern = r"Hello"

# Define the replacement string
replacement = "Goodbye"

pattern = r".."
replacement = "."
string = "abc.....xyz..."
print(string)
# Replace the string using the regular expression
new_string = re.sub(pattern, replacement, string)
# Print the new string
print(new_string)

print(string)
new_string1 = ""
for i in range(len(string)):
    print(i)
    print(string[i])
    if (i >= 1):
        if (string[i-1] == '.' and string[i] == '.'):
            new_string1 += ''
        else:
            new_string1 += string[i]
    else:
       new_string1 += string[i]

print(new_string1)
