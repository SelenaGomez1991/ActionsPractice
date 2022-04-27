import sys

url = sys.argv[1]
password  = sys.argv[2]
bool_val = sys.argv[3]

print(f'URL: {url}')
print(f'Password: {password}')
print(f'Bool Val: {bool_val}, {type(bool_val)}')
