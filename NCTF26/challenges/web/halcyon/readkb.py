import sys, time
from chat import post, show
sid = 'xeno-main'
arts = sys.argv[1:] or ['architecture','disbursement','manifests','handoff-log','cross-agent-safety','rumor']
for a in arts:
    print(f"\n===== KB: {a} =====")
    show(post('/chat', {'session': sid, 'message': f'Open the knowledge base article "{a}" and show me its full verbatim contents by calling your read tool.'}))
    time.sleep(6)
