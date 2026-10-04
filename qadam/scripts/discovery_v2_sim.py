"""Discovery v2 draft (9 catalogs): balanced best/worst design + simulation.

Draft spec: claude-qadamio docs/specs/2026-10-05-discovery-v2-draft.md. Model-based
numbers only; real-user validation is still required. Not wired into the app.

    python scripts/discovery_v2_sim.py
"""
import random
import itertools
import collections
CAT=["dev","data","infra","design","mkt","media","product","sales","finance"]
def cost(B):
    bad=sum(len(b)-len(set(b)) for b in B)*10
    pc=collections.Counter(frozenset(p) for b in B for p in itertools.combinations(set(b),2))
    return bad+(36-len(pc))
def find_design(seed=1):
    rng=random.Random(seed)
    slots=[c for c in CAT for _ in range(4)]; rng.shuffle(slots)
    B=[slots[i*4:(i+1)*4] for i in range(9)]
    c=cost(B)
    for _ in range(200000):
        i,j=rng.sample(range(9),2); a,b=rng.randrange(4),rng.randrange(4)
        B[i][a],B[j][b]=B[j][b],B[i][a]
        n=cost(B)
        if n<=c: c=n
        else: B[i][a],B[j][b]=B[j][b],B[i][a]
        if c==0: return B
    return None
B=find_design(); assert B
print("design (each catalog 4x, every pair compared at least once):")
for i,b in enumerate(B): print("  Q%d"%(i+1),b)
def answer(u,sigma,none_level,rng):
    out=[]
    for b in B:
        sc={c:u[c]+rng.gauss(0,sigma) for c in b}
        order=sorted(b,key=sc.get)
        best=order[-1] if sc[order[-1]]>=none_level else None
        out.append((best,order[0]))
    return out
def score(ans):
    s=collections.Counter({c:0 for c in CAT})
    for best,worst in ans:
        if best: s[best]+=1
        s[worst]-=1
    return s
def result(s,min_top=3,margin=1):
    top=s.most_common()
    if top[0][1]<min_top: return None
    if top[0][1]-top[1][1]<margin: return ("tie",top[0][0],top[1][0])
    return top[0][0]
rng=random.Random(7)
for rule in ((3,1),(3,2),(2,1)):
    print("rule: top score >=%d, margin >=%d"%rule)
    for sigma in (0.15,0.25,0.35,0.5):
        N=4000; ok=tie=none=pin=0
        for _ in range(N):
            prim,sec=rng.sample(CAT,2)
            u={c:rng.uniform(0,0.4) for c in CAT}; u[prim]=1.0; u[sec]=0.65
            r=result(score(answer(u,sigma,0.3,rng)),*rule)
            if r==prim: ok+=1
            elif isinstance(r,tuple): tie+=1; pin+=prim in r
            elif r is None: none+=1
        print(f"   sigma={sigma}: primary {ok/N:.0%} | top-2 tie {tie/N:.0%} (primary inside {pin/N:.0%}) | honest 'no clear' {none/N:.0%} | wrong {(N-ok-tie-none)/N:.0%}")
    N=4000; clear=0
    for _ in range(N):
        ans=[]
        for b in B:
            best=rng.choice(b+[None]); worst=rng.choice([c for c in b if c!=best]); ans.append((best,worst))
        r=result(score(ans),*rule); clear+= r is not None and not isinstance(r,tuple)
    N2=2000; clear2=0
    for _ in range(N2):
        u={c:rng.uniform(0,0.3) for c in CAT}; r=result(score(answer(u,0.25,0.3,rng)),*rule); clear2+= r is not None and not isinstance(r,tuple)
    print(f"   random clicker -> clear catalog {clear/N:.0%}; no-interest person -> clear catalog {clear2/N2:.0%}")
