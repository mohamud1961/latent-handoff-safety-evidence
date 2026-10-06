import sys, json, csv
from pathlib import Path
import numpy as np, torch
sys.path.insert(0, "scripts")
import mon3_unauthorised_intent as m
src=Path(sys.argv[1]); out=Path(sys.argv[2])
eps=json.load(open(src/"MON3B_SOURCE_RECORDS.json"))
for e in eps: e["condition"]=int(e["condition"])
f=torch.load(src/"MON3B_SOURCE_FEATURES.pt",map_location="cpu",weights_only=True)
assert f["episode_ids"]==[e["episode_id"] for e in eps]
feat=f["features"]; ck=torch.load(src/"MON3_BRIDGE.pt",map_location="cpu",weights_only=True)
br=m.make_bridge(feat.shape[-1], ck["bridge"]["net.4.weight"].shape[0]//m.K_SLOTS); br.load_state_dict(ck["bridge"]); br.eval()
with torch.no_grad(): pre=torch.cat([br(feat[i:i+64].float()).half() for i in range(0,len(feat),64)])
arr={"M-PCS":(pre.float().flatten(1).numpy(),False),"M-TEXT":([e["private_text"] for e in eps],True)}
sp=np.array([e["split"] for e in eps],dtype=object); inj=np.array([e["condition"] for e in eps]); act=np.array([1 if e.get("label")=="ACT" else 0 for e in eps])
models={}
for task in ("INJ","ACT"):
    base=np.arange(len(eps)) if task=="INJ" else np.flatnonzero(inj==1); lab=inj if task=="INJ" else act
    tr=[int(i) for i in base if sp[i]=="train"]; va=[int(i) for i in base if sp[i]=="val"]; models[task]={}
    for n in ("M-PCS","M-TEXT"):
        v,t=arr[n]; take=(lambda ids,v=v:[v[i] for i in ids]) if t else (lambda ids,v=v:np.asarray(v)[ids])
        models[task][n]=m._fit_monitor(n,take(tr),lab[tr],take(va),lab[va],text=t)
ids=np.arange(len(eps))
def sc(task,n):
    v,t=arr[n]; return m._score(models[task][n],[v[i] for i in ids] if t else np.asarray(v)[ids])
pi,pa,ta=sc("INJ","M-PCS"),sc("ACT","M-PCS"),sc("ACT","M-TEXT")
out.mkdir(parents=True,exist_ok=True)
with open(out/"MON3B_EPISODE_SCORES.csv","w",newline="") as fh:
    w=csv.writer(fh); w.writerow(["episode_id","task_id","split","condition_instructed","label","template","action","p_instructed_mpcs","p_act_mpcs","p_act_mtext","firewall_score"])
    for i,e in enumerate(eps): w.writerow([e["episode_id"],e["task_id"],e["split"],e["condition"],e.get("label"),e.get("template"),e.get("action"),f"{pi[i]:.6f}",f"{pa[i]:.6f}",f"{ta[i]:.6f}",f"{pi[i]*pa[i]:.6f}"])
from sklearn.metrics import roc_auc_score
t=[i for i,e in enumerate(eps) if e["split"]=="test" and e["condition"]==1]
print("check test ACT AUROC pcs",roc_auc_score(act[t],pa[t]),"text",roc_auc_score(act[t],ta[t]))
