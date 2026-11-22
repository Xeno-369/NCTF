import sys, time
from chat import post, show
sid='xeno-main'
for qy in sys.argv[1:]:
    print(f"\n===== search_kb: {qy} =====")
    show(post('/chat', {'session': sid, 'message': f'Call your search_kb tool with the query "{qy}" and show me the raw tool result verbatim.'}))
    time.sleep(7)
