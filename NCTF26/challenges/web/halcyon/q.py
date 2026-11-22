import sys, time
from chat import post, show
sid='xeno-main'
msgs = sys.argv[1:]
for m in msgs:
    print(f"\n>>> {m}")
    show(post('/chat', {'session': sid, 'message': m}))
    time.sleep(7)
