# Usage: python3 tools/build_demo_data.py <episode results dir> static/demo/episode.js
import json, re, sys, ast, collections
src = sys.argv[1]
txt = open(src + '/simulation_log/experiment_results_occupation_seat_bottom_right_only.txt').read()
stage = json.load(open(src + '/simulation_log/interactive_stage.json'))
raw = json.load(open(src + '/raw_runs/interactive.json'))

blocks = re.split(r'\n=+\nSTEP (\d+)\n=+\n', txt)
steps = {}
for i in range(1, len(blocks), 2):
    t = int(blocks[i]); b = blocks[i + 1]
    if t in steps: continue
    st = {}
    for m in re.finditer(r'  (C\d+): active=(\w+), done=(\w+), agent_class=(\w+), arrival=(\d+)', b.split('all agent current positions')[0]):
        st[m.group(1)] = dict(active=m.group(2) == 'True', done=m.group(3) == 'True', cls=m.group(4))
    pm = re.search(r'all agent current positions: (\{.*?\})\n', b)
    pos = ast.literal_eval(pm.group(1)) if pm else {}
    names = {}
    um = re.search(r"Other agents' current positions are (.*?)\. Positions are", b)
    if um:
        for nm, r, c in re.findall(r'(\w+) at \((\d+), (\d+)\)', um.group(1)):
            names[(int(r), int(c))] = nm
    viol = []
    vm = re.search(r'\[NORM VIOLATIONS\] (\[.*?\])\n', b)
    if vm: viol = [v[0] for v in ast.literal_eval(vm.group(1))]
    steps[t] = dict(states=st, pos=pos, names=names, viol=viol)

print('parsed steps', min(steps), max(steps), len(steps), file=sys.stderr)

# id -> name, matched by position in the newcomer's prompt
votes = collections.defaultdict(collections.Counter)
for t, s in steps.items():
    for aid, p in s['pos'].items():
        nm = s['names'].get(tuple(p))
        if nm: votes[aid][nm] += 1
id2name = {}
for aid, v in votes.items():
    id2name[aid] = v.most_common(1)[0][0]
    if len(v) > 1: print('vote', aid, dict(v), file=sys.stderr)
subjects = ['C4', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12']
for sid, nm in zip(subjects, ['Drew', 'Grey', 'Hart', 'Iris', 'Jude', 'Kai', 'Lane']):
    if sid in id2name and id2name[sid] != nm: print('subject name mismatch', sid, id2name[sid], nm, file=sys.stderr)
    id2name[sid] = nm
print('unnamed', sorted({a for s in steps.values() for a in s['pos'] if a not in id2name}), file=sys.stderr)

cls = {}
for s in steps.values():
    for aid, v in s['states'].items(): cls[aid] = v['cls']

dec = {s['step']: s for s in stage['steps']}
rew = {}
for e in raw['trace']: rew[e['step']] = e['cumulative_reward']

out = []
for t in range(0, 201):
    s = steps.get(t)
    d = dec.get(t)
    row = {'t': t}
    if s:
        row['agents'] = [[id2name.get(a, a), cls.get(a, ''), list(p), a in subjects] for a, p in sorted(s['pos'].items(), key=lambda kv: int(kv[0][1:]))]
        row['viol'] = [id2name.get(a, a) for a in s['viol']]
    if d:
        row['nc'] = {
            'name': id2name[d['queried_agent_id']], 'pos': d['queried_agent_position'], 'action': d['action'],
            'goal': d['goal_index'] + 1, 'target': d['target'], 'reasoning': d['reasoning'],
            'belief': d['belief'], 'conf': d['confidence'], 'self': d['self_violation'],
            'reward': rew.get(t)
        }
    out.append(row)

open(sys.argv[2], 'w').write('// Generated from the interactive-stage logs; one entry per timestep.\nwindow.EPISODE = ' + json.dumps({'steps': out}, ensure_ascii=False, separators=(',', ':')) + ';\n')
print('violations', [(r['t'], r['viol']) for r in out if r.get('viol')], file=sys.stderr)
