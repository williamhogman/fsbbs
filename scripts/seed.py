"""Seeds the redis datastore with the minimal forum structure from INSTALL.

Idempotent: does nothing when the forum root (thing:1) already exists.
"""
import sys
import time

import redis

port = int(sys.argv[1]) if len(sys.argv) > 1 else 6379
r = redis.Redis(host="127.0.0.1", port=port, decode_responses=True)

if r.get("thing:1:type"):
    print("redis already seeded")
    sys.exit(0)

now = time.time()

# forum root
r.set("thing:1:type", "forum")
r.set("thing:1:name", "fsbbs")
r.set("thing:1:tagline", "fseek bulletin board system")

# a category
r.set("thing:2:type", "category")
r.set("thing:2:title", "General")
r.set("thing:2:description", "Discuss *anything* here")
r.zadd("thing:1:contents", {"2": 0})

# a topic with an original post inside the category
r.set("thing:3:type", "topic")
r.set("thing:3:title", "Welcome to fsbbs")
r.set("thing:3:original_post", "4")
r.zadd("thing:2:contents", {"3": 0})

r.set("thing:4:type", "post")
r.set("thing:4:poster_uid", "1")
r.set("thing:4:text", "Hello and **welcome** to fsbbs.\n\nThis board runs on the fsbbs proof of concept.")
r.set("thing:4:pubdate", str(now))

r.set("thing:next_tid", "4")

# the seed user
r.set("user:next_uid", "1")
r.set("user:1:username", "admin")
r.set("username:admin:uid", "1")

# salt for the basic password auth module
r.set("authmod:BasicPasswords:salt", "fsbbs-dev-salt")

print("seeded redis on port %d" % port)
