import configparser

# ConfigParser 객체 생성
config = configparser.ConfigParser()

# 설정 파일 읽기
config.read('Qscript/parser.ini')

# 기본값 딕셔너리 정의
default_values = {
    'ServerAliveInterval': '45',
    'Compression': 'yes',
    'CompressionLevel': '9',
    'ForwardX11': 'yes'
}

# bitbucket.org 섹션에서 값을 읽을 때 vars 매개변수 사용
server_alive_interval = config.get('bitbucket.org', 'ServerAliveInterval', vars=default_values)
compression = config.get('bitbucket.org', 'Compression', vars=default_values)
compression_level = config.get('bitbucket.org', 'CompressionLevel', vars=default_values)
forward_x11 = config.get('bitbucket.org', 'ForwardX11', vars=default_values)
user = config.get('bitbucket.org', 'User')

print(f"bitbucket.org - ServerAliveInterval: {server_alive_interval}")
print(f"bitbucket.org - Compression: {compression}")
print(f"bitbucket.org - CompressionLevel: {compression_level}")
print(f"bitbucket.org - ForwardX11: {forward_x11}")
print(f"bitbucket.org - User: {user}")

# topsecret.server.com 섹션에서 값을 읽을 때 vars 매개변수 사용
port = config.get('topsecret.server.com', 'Port')
forward_x11_topsecret =              
server_alive_interval_topsecret = config.get('topsecret.server.com', 'ServerAliveInterval', vars=default_values)
compression_topsecret = config.get('topsecret.server.com', 'Compression', vars=default_values)
compression_level_topsecret = config.get('topsecret.server.com', 'CompressionLevel', vars=default_values)

print(f"\ntopsecret.server.com - Port: {port}")
print(f"topsecret.server.com - ForwardX11: {forward_x11_topsecret}")
print(f"topsecret.server.com - ServerAliveInterval: {server_alive_interval_topsecret}")
print(f"topsecret.server.com - Compression: {compression_topsecret}")
print(f"topsecret.server.com - CompressionLevel: {compression_level_topsecret}")
