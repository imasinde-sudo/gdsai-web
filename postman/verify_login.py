with open(r'postman/collections/GDSAI Auth API/Auth/Login.request.yaml', 'rb') as f:
    raw = f.read()
print('BOM present:', raw[:3] == b'\xef\xbb\xbf')
print('CRLF present:', b'\r\n' in raw)
print('email field present:', b'"email": "{{test_email}}"' in raw)
print('First 100 bytes:', raw[:100])
