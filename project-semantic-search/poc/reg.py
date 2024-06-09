import re

'''
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

s = 'one two one two one'
print(s)

print(s.replace('one', 'XXX'))
# XXX two XXX two XXX

print(s.replace('one', 'XXX', 2))
# XXX two XXX two one
'''

special_char_dict = {
  'àtma-jñànì': 'atma-jnani',
  'daréan': 'darsan',
}
text = 'When Käçåa says a friend to all beings, he doesn’t just mean all types of people. The heart of the àtma-jñànì extends with the feeling of friendship to every aspect of creation. Amma’s biography is filled with stories illustrating the reciprocal heartfelt bond between Amma and various animals, and I have personally seen Amma give daréan not just to common pets like cats and dogs, but also to parrots, eagles, horses, wolves, cows, goats, camels, beetles, owls, rabbits, chipmunks, bats, turtles, pythons, boa constrictors, monkeys, cheetahs, and elephants. Amma’s heart truly has a space for every aspect of creation. It never ceases to amaze me how she never forgets to consider the needs and feelings of even those creatures we typically think of as insignificant.'
print("*** original text ***")
print(text)
for s in special_char_dict:
    print(s, special_char_dict[s])
    text = text.replace(s, special_char_dict[s])
print("*** modified text ***")
print(text)
