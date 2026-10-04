"""Discovery v2 draft (9 catalogs, 5 options + "don't know"): balanced design + simulation.

Draft spec: claude-qadamio docs/specs/2026-10-05-discovery-v2-draft.md. Model-based
numbers only; real-user validation is still required. Not wired into the app.

    python scripts/discovery_v2_sim.py
"""
import random, itertools, collections
CAT=["dev","data","infra","design","mkt","media","product","sales","finance"]
K=5
def cost(B):
    bad=sum(len(b)-len(set(b)) for b in B)*50
    pc=collections.Counter(frozenset(p) for b in B for p in itertools.combinations(set(b),2))
    return bad+sum(max(0,2-pc.get(frozenset(p),0)) for p in itertools.combinations(CAT,2))
def find_design(seed=3):
    rng=random.Random(seed)
    slots=[c for c in CAT for _ in range(K)]; rng.shuffle(slots)
    B=[slots[i*K:(i+1)*K] for i in range(9)]; c=cost(B)
    for _ in range(400000):
        i,j=rng.sample(range(9),2); a,b=rng.randrange(K),rng.randrange(K)
        B[i][a],B[j][b]=B[j][b],B[i][a]; n=cost(B)
        if n<=c: c=n
        else: B[i][a],B[j][b]=B[j][b],B[i][a]
        if c==0: break
    return B,c
B,c=find_design()
pc=collections.Counter(frozenset(p) for b in B for p in itertools.combinations(b,2))
print("design cost",c,"pair min/max",min(pc.values()),max(pc.values()),"pairs covered",len(pc))
for i,b in enumerate(B): print("  Q%d"%(i+1),b)
def answer(u,sigma,skip_level,rng,worst=True):
    out=[]
    for b in B:
        sc={x:u[x]+rng.gauss(0,sigma) for x in b}
        order=sorted(b,key=sc.get)
        if sc[order[-1]]<skip_level: out.append((None,None)); continue   # "Bilmayman / mosi yo'q"
        out.append((order[-1],order[0] if worst else None))
    return out
def score(ans):
    s=collections.Counter({x:0 for x in CAT})
    for best,w in ans:
        if best: s[best]+=1
        if w: s[w]-=1
    return s
def result(s,min_top=3,margin=1):
    top=s.most_common()
    if top[0][1]<min_top: return None
    if top[0][1]-top[1][1]<margin: return ("tie",top[0][0],top[1][0])
    return top[0][0]
rng=random.Random(11)
for worst in (True,False):
  for rule in ((3,1),(4,1)):
    print(f"\n{'best+worst' if worst else 'best only'}; rule top>={rule[0]} margin>={rule[1]}")
    for sigma in (0.15,0.25,0.35,0.5):
        N=4000; ok=tie=none=pin=0
        for _ in range(N):
            prim,sec=rng.sample(CAT,2)
            u={x:rng.uniform(0,0.4) for x in CAT}; u[prim]=1.0; u[sec]=0.65
            r=result(score(answer(u,sigma,0.3,rng,worst)),*rule)
            if r==prim: ok+=1
            elif isinstance(r,tuple): tie+=1; pin+=prim in r
            elif r is None: none+=1
        print(f"   sigma={sigma}: primary {ok/N:.0%} | tie {tie/N:.0%} (primary inside {pin/N:.0%}) | no clear {none/N:.0%} | wrong {(N-ok-tie-none)/N:.0%}")
    N=4000; clear=0
    for _ in range(N):
        ans=[]
        for b in B:
            best=rng.choice(b+[None])
            ans.append((best, rng.choice([x for x in b if x!=best]) if (best and worst) else None))
        r=result(score(ans),*rule); clear+= r is not None and not isinstance(r,tuple)
    N2=2000; clear2=0
    for _ in range(N2):
        u={x:rng.uniform(0,0.3) for x in CAT}; r=result(score(answer(u,0.25,0.3,rng,worst)),*rule); clear2+= r is not None and not isinstance(r,tuple)
    print(f"   random clicker -> clear {clear/N:.0%}; no-interest -> clear {clear2/N2:.0%}")
