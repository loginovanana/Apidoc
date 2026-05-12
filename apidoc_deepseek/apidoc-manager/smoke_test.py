import glob
for f in ['apidoc_server/services/validation_service.py'] + glob.glob('apidoc_server/**/*.py', recursive=True):
    try:
        with open(f, 'r', encoding='utf-8') as fh:
            c = fh.read()
        c = c.replace('OpenAPIValidationError', 'OpenAPISpecValidatorError')
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(c)
        print(f'Patched {f}')
    except: pass
print('Done')