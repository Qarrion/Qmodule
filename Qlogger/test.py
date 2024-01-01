from configparser import ConfigParser


config = ConfigParser()
config.read('Qlogger/default.ini')
config.sections()
config.get('DEFAULT','fmt', raw=True)
config.get('DEFAULT','fmt')

# config.defaults()



import configparser

# 설정 파서 생성
config = configparser.ConfigParser()

# example.ini 파일 읽기
config.read('example.ini')

# 'bitbucket.org'에서 'Compression' 조회 (DEFAULT 섹션에서 가져옴)
print("bitbucket.org compression:", config.get('bitbucket.org', 'Compression'))

# 'bitbucket.org'에서 'ServerAliveInterval' 조회 (DEFAULT 섹션에서 가져옴)
print("bitbucket.org ServerAliveInterval:", config.get('bitbucket.org', 'ServerAliveInterval'))

# 'topsecret.server.com'의 'CompressionLevel' 조회 (DEFAULT 섹션에서 가져옴)
print("topsecret.server.com CompressionLevel:", config.get('topsecret.server.com', 'CompressionLevel'))

# 'topsecret.server.com'의 'Host Port' 조회 (DEFAULT 섹션에 없으므로 해당 섹션에서 가져옴)
print("topsecret.server.com Host Port:", config.get('topsecret.server.com', 'Host Port'))