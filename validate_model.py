"""Forecast check: can any model predict Oct-Dec incidents from Jan-Sep data?
Run:  python validate_model.py   (needs scikit-learn and scipy: pip install scikit-learn scipy)
Result on the synthetic data: no model beats predicting the average (see HANDOFF_FOR_AI.txt)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd, numpy as np, warnings; warnings.filterwarnings("ignore")
from core.loader import load_data
from core import config
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.linear_model import PoissonRegressor, LogisticRegression
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.metrics import roc_auc_score, mean_poisson_deviance
from scipy.stats import spearmanr
d=load_data(); L,I,C=d.locations,d.incidents.copy(),d.complaints.copy()
cut=pd.Timestamp("2025-10-01")
tr,te=I[I.timestamp<cut],I[I.timestamp>=cut]
idx=L.location_id
def feats():
    g=tr.groupby("location_id")
    X=pd.DataFrame(index=idx)
    X["n"]=g.size().reindex(idx,fill_value=0)
    X["inj"]=g.injuries.sum().reindex(idx,fill_value=0)
    X["inj_ge1"]=tr[tr.injuries>0].groupby("location_id").size().reindex(idx,fill_value=0)
    X["sev"]=tr.assign(s=tr.severity.map(config.SEVERITY_POINTS)).groupby("location_id").s.sum().reindex(idx,fill_value=0)
    X["crit"]=tr[tr.severity=="Critical"].groupby("location_id").size().reindex(idx,fill_value=0)
    X["unres"]=tr[tr.resolved==0].groupby("location_id").size().reindex(idx,fill_value=0)
    X["n_last60"]=tr[tr.timestamp>=cut-pd.Timedelta(days=60)].groupby("location_id").size().reindex(idx,fill_value=0)
    cc=C[C.created_at<cut]
    X["comp"]=cc.groupby("location_id").size().reindex(idx,fill_value=0)
    X["comp_open"]=cc[cc.status.isin(config.OPEN_STATUSES)].groupby("location_id").size().reindex(idx,fill_value=0)
    Ls=L.set_index("location_id")
    X["rt"]=Ls.road_type.map(config.ROAD_TYPE_SCORE); X["rc"]=Ls.road_condition.map(config.ROAD_CONDITION_SCORE)
    X["ped"]=Ls.pedestrian_activity.map(config.PEDESTRIAN_SCORE); X["dens"]=Ls.population_density_per_km2
    X["sch"]=Ls.near_school; X["hos"]=Ls.near_hospital
    return X
X=feats()
y_n=te.groupby("location_id").size().reindex(idx,fill_value=0)
y_inj=te.groupby("location_id").injuries.sum().reindex(idx,fill_value=0)
y_bad=((te.injuries>0)|(te.severity.isin(["High","Critical"]))).groupby(te.location_id).sum().reindex(idx,fill_value=0)
print("test-period incidents/loc mean",y_n.mean().round(2),"var",y_n.var().round(2),"(Poisson-like if var≈mean)")
print("\nSpearman of each feature vs Q4 incident count / Q4 injuries / Q4 serious:")
for c in X.columns:
    print(f"{c:9} {spearmanr(X[c],y_n)[0]:+.3f} {spearmanr(X[c],y_inj)[0]:+.3f} {spearmanr(X[c],y_bad)[0]:+.3f}")
kf=KFold(5,shuffle=True,random_state=0)
for name,y in [("Q4 incidents",y_n),("Q4 injuries",y_inj),("Q4 serious",y_bad)]:
    base=np.full(len(y),y.mean())
    p_pois=cross_val_predict(PoissonRegressor(alpha=1.0,max_iter=500),(X-X.mean())/X.std(),y,cv=kf)
    p_gb=cross_val_predict(GradientBoostingRegressor(n_estimators=100,max_depth=2,learning_rate=0.05,subsample=0.8,random_state=0),X,y,cv=kf)
    p_gb=np.clip(p_gb,0.01,None);p_pois=np.clip(p_pois,0.01,None)
    print(f"\n{name}: Poisson deviance  baseline(mean)={mean_poisson_deviance(y.clip(lower=0),base):.4f}  poisson-GLM={mean_poisson_deviance(y,p_pois):.4f}  GBM={mean_poisson_deviance(y,p_gb):.4f}")
    print("   Spearman(pred,actual)  GLM %.3f  GBM %.3f  | current n-only %.3f"%(spearmanr(p_pois,y)[0],spearmanr(p_gb,y)[0],spearmanr(X.n,y)[0]))
# current rule-based score as predictor of Q4 injuries
from core.scoring import score_locations
r=score_locations(L,tr,C[C.created_at<cut]).set_index("location_id").reindex(idx)
print("\nExisting priority_score vs Q4 incidents/injuries/serious Spearman: %.3f %.3f %.3f"%(spearmanr(r.priority_score,y_n)[0],spearmanr(r.priority_score,y_inj)[0],spearmanr(r.priority_score,y_bad)[0]))
# AUC for 'any injury in Q4'
yb=(y_inj>0).astype(int); print("P(any Q4 injury)=%.2f"%yb.mean())
pp=cross_val_predict(GradientBoostingClassifier(n_estimators=100,max_depth=2,learning_rate=0.05,subsample=0.8,random_state=0),X,yb,cv=kf,method="predict_proba")[:,1]
print("AUC any-injury GBM: %.3f ; rule score AUC: %.3f"%(roc_auc_score(yb,pp),roc_auc_score(yb,r.priority_score)))
# incident-level: does anything predict injuries?
m=I.merge(L,on="location_id")
for col in ["incident_type","road_type","road_condition","pedestrian_activity","reported_by","near_school"]:
    print(col,m.groupby(col).injuries.mean().round(3).to_dict())
