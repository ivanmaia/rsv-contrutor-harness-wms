import json,collections,glob,os,sys
for d in sorted(glob.glob('runs/T*-*')):
    p=os.path.join(d,'stream.jsonl')
    if not os.path.exists(p): continue
    L=[json.loads(l) for l in open(p,encoding='utf-8') if l.strip().startswith('{')]
    tools=collections.Counter(c['name'] for e in L if e.get('type')=='assistant' for c in e['message'].get('content',[]) if c.get('type')=='tool_use')
    rs=[e for e in L if e.get('type')=='result']
    if not rs: print(d,'SEM RESULTADO'); continue
    r=rs[-1]; u=r.get('usage',{})
    tot=u.get('input_tokens',0)+u.get('cache_creation_input_tokens',0)+u.get('cache_read_input_tokens',0)+u.get('output_tokens',0)
    print(f"{os.path.basename(d):12} turns={r.get('num_turns')} tokens={tot} out={u.get('output_tokens')} cost={r.get('total_cost_usd'):.3f} err={r.get('is_error')} tools={dict(tools)}")
    print('   ->', (r.get('result') or '').replace('\n',' | ')[:300])
