"""Discovery v2 draft (9 catalogs; 4 options + "don't know", one pick per question): simulation.

Draft spec: claude-qadamio docs/specs/2026-10-05-discovery-v2-draft.md. Model-based
numbers only; real-user validation is still required. Not wired into the app.

    python scripts/discovery_v2_sim.py
"""
import random, collections
CAT=["dev","data","infra","design","mkt","media","product","sales","finance"]
B=[['finance','media','design','mkt'],['mkt','sales','media','infra'],['finance','infra','design','mkt'],
 ['dev','data','design','finance'],['product','data','media','infra'],['product','sales','data','design'],
 ['product','data','dev','mkt'],['finance','dev','product','sales'],['infra','sales','media','dev']]
def answer(u,sigma,skip,rng):
    out=[]
    for b in B:
        sc={x:u[x]+rng.gauss(0,sigma) for x in b}; best=max(sc,key=sc.get)
        out.append(best if sc[best]>=skip else None)
    return out
def result(picks,min_top,margin):
    s=collections.Counter({x:0 for x in CAT}); s.update(p for p in picks if p)
    top=s.most_common()
    if top[0][1]<min_top: return None
    if top[0][1]-top[1][1]<margin: return ("tie",top[0][0],top[1][0])
    return top[0][0]
rng=random.Random(5)
for rule in ((3,1),):
    print("4 options + skip, one pick; rule top>=%d margin>=%d"%rule)
    for label,sigma in (("yuqori",0.15),("o'rta",0.25),("past",0.35),("juda past",0.5)):
        N=6000; ok=tie=none=pin=0
        for _ in range(N):
            prim,sec=rng.sample(CAT,2)
            u={x:rng.uniform(0,0.4) for x in CAT}; u[prim]=1.0; u[sec]=0.65
            r=result(answer(u,sigma,0.3,rng),*rule)
            if r==prim: ok+=1
            elif isinstance(r,tuple): tie+=1; pin+=prim in r
            elif r is None: none+=1
        print(f"  {label:9}: found {ok/N:.0%} | tie {tie/N:.0%} (inside {pin/N:.0%}) | no clear {none/N:.0%} | wrong {(N-ok-tie-none)/N:.0%}")
    N=6000; clear=0
    for _ in range(N):
        r=result([rng.choice(b+[None]) for b in B],*rule); clear+= r is not None and not isinstance(r,tuple)
    N2=3000; clear2=0
    for _ in range(N2):
        u={x:rng.uniform(0,0.3) for x in CAT}; r=result(answer(u,0.25,0.3,rng),*rule); clear2+= r is not None and not isinstance(r,tuple)
    print(f"  random clicker clear {clear/N:.0%}; no-interest clear {clear2/N2:.0%}")
