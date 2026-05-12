path = 'tests_out/conftest.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('https://api.example.com/v1', 'http://127.0.0.1:8766')
with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('OK base_url исправлен на http://127.0.0.1:8766')