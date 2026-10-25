import json,sys,zipfile
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import pandas as pd

def read_member(z,name):
    try:
        return pd.read_csv(z.open(name),parse_dates=['<DATE>']).rename(columns={'<CLOSE>':'close'}).set_index('<DATE>').sort_index()
    except Exception:
        return None

def main(zip_path,out_path):
    with zipfile.ZipFile(zip_path) as z:
        names=z.namelist(); idx='data/daily/jp/tse indices/^tpx.txt'
        if idx not in names: raise ValueError('Stooq TSE ZIPではありません')
        dates=read_member(z,idx).loc['2015-01-01':].index
        codes=[]; series=[]
        for n in [n for n in names if '/tse stocks/' in n and n.endswith('.txt')]:
            d=read_member(z,n)
            if d is None or d.index.duplicated().any(): continue
            c=d.close.reindex(dates).to_numpy(float); c[c<=0]=np.nan
            codes.append(n.rsplit('/',1)[-1].removesuffix('.txt').upper()); series.append(c)
    close=np.stack(series,axis=1); common=np.flatnonzero(np.isfinite(close).sum(1)>=len(codes)*.5); i=int(common[-1]); date=dates[i].date().isoformat(); rows=[]
    for k,code in enumerate(codes):
        c=close[:i+1,k]
        if i<201 or not np.isfinite(c[-202:]).all() or (c[-202:]<=0).any(): continue
        m5,m25,m75,m200=[c[-w:].mean() for w in (5,25,75,200)]
        if m200<=c[-201:-1].mean(): continue
        choices=[]
        if m5>m25>m75 and m25>m200 and m75<=m200: choices.append(('75対200',(m200-m75)/m200*100))
        if m5>m75>m200 and m25>m200 and m25<=m75: choices.append(('25対75',(m75-m25)/m75*100))
        if m25>m75>m200 and m5>m75 and m5<=m25: choices.append(('5対25',(m25-m5)/m25*100))
        pc=[c[-w-1:-1].mean() for w in (5,25,75,200)]; pp=c[-202:-2].mean(); before=[]
        if pc[3]>pp:
            a,b,d,e=pc
            if a>b>d and b>e and d<=e: before.append('75対200')
            if a>d>e and b>e and b<=d: before.append('25対75')
            if b>d>e and a>d and a<=b: before.append('5対25')
        for typ,gap in choices:
            if 0<=gap<=1.5: rows.append({'code':code,'type':typ,'new':int(typ not in before),'close':round(float(c[-1]),4),'gap':round(float(gap),4)})
    rows.sort(key=lambda x:(-x['new'],x['gap'])); payload={'date':date,'updated_at':datetime.now(timezone.utc).isoformat(),'candidates':len(rows),'new':sum(x['new'] for x in rows),'rows':rows}
    Path(out_path).write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps({k:payload[k] for k in ('date','candidates','new')},ensure_ascii=False))

if __name__=='__main__': main(sys.argv[1],sys.argv[2])
