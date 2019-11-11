import json
import pathlib
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

root = str(pathlib.Path(__file__).resolve().parents[2])
path_approach_1 = '/experiments/reports/approach_simple.txt'
path_approach_2 = '/experiments/reports/approach_coalition.txt'

def get_approach_metrics(path):
    # print('path: ',path)
    with open(root + path, 'r') as config:
        content = json.loads(config.read())
    metrics = content['environment']
    entriesToRemove = ('delivered_items','max_steps','current_step','floods_amount')
    for k in entriesToRemove:
        metrics.pop(k, None)
    return metrics

approach1 = pd.DataFrame(get_approach_metrics(path_approach_1), index=[0])
approach1 = approach1.T
approach1['approach']='No Coalitions'
approach1['metrics']=approach1.index
approach2 = pd.DataFrame(get_approach_metrics(path_approach_2), index=[0])
approach2 = approach2.T
approach2['approach']='With Coalitions'
approach2['metrics']=approach2.index
approaches = pd.concat([approach1,approach2])
approaches.columns = ['Amount','Approach','Metrics']

fig, ax = plt.subplots(1,1)
g = sns.catplot(ax=ax, x='Metrics', y='Amount', hue="Approach", data=approaches,kind="bar", palette="muted")
ax.set_xlabel('Metrics of the Simulator')
ax.set_xticklabels(ax.get_xticklabels(),rotation=80)
fig.savefig(root+'/experiments/reports/Comparison-Metrics-Approaches.png',bbox_inches="tight")