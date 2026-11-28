import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import seaborn as sns
from matplotlib.lines import Line2D

CPT_ORDER = ['ASY','ATA','NAP','TA']
HEATMAP_COLS = ['Age','RestingBP','cholesterol_imputed','MaxHR','Oldpeak','HeartDisease']
def plot_scatter(df,path):
    sick = df[df["HeartDisease"]==1]
    well = df[df["HeartDisease"]==0]
    fig,ax = plt.subplots(figsize=(8,6))
    ax.scatter(sick['MaxHR'],sick['Oldpeak'],c='red',alpha = 0.6,s=25)
    ax.scatter(well['MaxHR'],well['Oldpeak'],c='green',alpha =0.6,s=25)


    ax.axvline(120,color='grey',linestyle='--')
    ax.axhline(2.0,color='grey',linestyle=':')

    handles=[
        Line2D([0],[0],marker='o',color='w',markerfacecolor='red',markersize=9,label='Heart Disease'),
        Line2D([0],[0],marker='o',color='w',markerfacecolor='green',markersize=9,label='Normal'),
        Line2D([0],[0],color='grey',linestyle='--',label='MaxHR = 120'),
        Line2D([0],[0],color='grey',linestyle=':',label='Oldpeak = 2.0'),
          ]
    ax.legend(handles=handles,loc='upper right')
    ax.set_xlabel('MaxHR(bpm)')
    ax.set_ylabel('Oldpeak(ST depression)')
    ax.set_title('MaxHR vs Oldpeak by disease status')
    fig.tight_layout()
    fig.savefig(path,dpi=150)
    plt.close(fig)
def plot_correlation_and_slope(df,path):
    fig,(ax1,ax2) = plt.subplots(1,2,figsize=(13,5))
    sns.heatmap(df[HEATMAP_COLS].corr(),annot=True,fmt='.2f',cmap='coolwarm',
                center=0,ax=ax1)
    ax1.set_title('Correlation of clinical vitals')
    sns.boxplot(data=df,x='ST_Slope',y='Oldpeak',order=['Up','Flat','Down'],ax=ax2)
    sns.despine(ax=ax2)
    ax2.set_title('Oldpeak by ST_Slope')
    fig.tight_layout()
    fig.savefig(path,dpi=150)
    plt.close(fig)
def plot_distribution_regimes(df,path):
    fig,ax = plt.subplots(figsize=(7,5))
    sns.violinplot(data=df,x='risk_percentile_tier',y='Oldpeak',
    order=['Low','Medium','High'],cut=0,ax=ax)
    sns.despine(ax=ax)
    ax.set_title('Oldpeak distribution by risk tier')
    fig.tight_layout()
    fig.savefig(path,dpi=150)
    plt.close(fig)
def _hover(sub):
    return[f'Age {r.Age},{r.Sex}<br>Chest pain: {r.ChestPainType},<br>'
           f'MaxHR {r.MaxHR},Oldpeak {r.Oldpeak}<br>'
           f'Risk percentile {r.risk_percentile:.0f}<br>Disease: {r.HeartDisease}'
           for r in sub.itertuples()
    ]
def write_dashboard(df,path):
    def subset(cpt,cut):
        return df[
            (df['ChestPainType'] == cpt) & (df['risk_percentile']>=cut)
        ]
    fig=go.Figure()
    for cpt in CPT_ORDER:
        s=subset(cpt,0)
        fig.add_trace(go.Scatter(x=s['MaxHR'].tolist(), y=s['Oldpeak'].tolist(),
                                    mode='markers',name=cpt,text=_hover(s),
                                     hoverinfo = 'text',marker=dict(size=12)
            )
        )
    n=len(CPT_ORDER)
    buttons=[dict(label='All',method='restyle',args=[{'visible':[True]*n}]
                )
        ]
    for i, cpt in enumerate(CPT_ORDER):
            buttons.append(dict(label=cpt,method='restyle',
                                    args=[{'visible':[j == i for j in range(n)
                                            ]
                                    }]
                            )
            )
    steps= []
    for cut in(0,25,50,75):
        subs = [subset(c,cut) for c in CPT_ORDER]
        steps.append(dict(label=f'{cut}+',method = 'restyle',args=[{
                        'x':[s['MaxHR'].tolist() for s in subs],
                        'y':[s['Oldpeak'].tolist() for s in subs],
                        'text':[_hover(s)for s in subs]
                    }]
                )
            )
    fig.update_layout(
                    title='Cardiac risk triage dashboard',
                    xaxis_title='MaxHR(bpm)', yaxis_title='Oldpeak(ST depression,mm)',
                    updatemenus=[dict(buttons=buttons,direction='down',x=0.0,y=1.18
                                )
                    ],
                    sliders=[dict(active=0,steps=steps,pad=dict(t=50),
                                  currentvalue=dict(prefix='Minimum risk percentile:'))])
    fig.write_html(path,include_plotlyjs=True)
                





    





