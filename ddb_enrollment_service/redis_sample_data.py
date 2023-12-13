import redis
from datetime import datetime

r = redis.Redis()

r.zadd('3' , {'3': datetime.utcnow().timestamp()})
r.zadd('3' , {'5': datetime.utcnow().timestamp()})
r.zadd('1' , {'2': datetime.utcnow().timestamp()})

