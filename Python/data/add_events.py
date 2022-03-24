import pandas as pd

COL = ["eta","phi","et","position","electron","tau"]
file_path = "./Python/data/old-cms-vbfh.csv"

df = pd.read_csv(file_path, names=["eta","phi","et","position","electron","tau"])
event_num = len(df)//252
event_col = []
for i in range(event_num):
    event_col.extend([i for x in range(252)])

df['event'] = event_col
df.to_csv(file_path, index=False)
