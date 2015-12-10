
LOGSTASH_URL = 'http://es.example.com:8080'
LOGSTASH_USER = 'nutuser' 
LOGSTASH_PASSWORD = '' 

try:
    from local_settings import *
except ImportError:
    pass
