import numpy as np
import plotly.graph_objects as go

xs = np.linspace(0, 10, 100)
sins = np.sin(xs)
randoms = np.random.rand(100)
fig = go.Figure(data=[
    go.Scatter(x=xs, y=sins, name="sin"),
    go.Scatter(x=xs, y=randoms, name="random"),
])
fig.update_xaxes(title="x") # X軸タイトルを指定
fig.update_yaxes(title="y") # Y軸タイトルを指定

fig.update_xaxes(range=(1,3)) # X軸の最大最小値を指定
fig.update_xaxes(rangeslider={"visible":True}) # X軸に range slider を表示（下図参照）

fig.update_yaxes(scaleanchor="x", scaleratio=1) # Y軸のスケールをX軸と同じに（plt.axis("equal")）

fig.update_layout(title="Title") # グラフタイトルを設定
fig.update_layout(font={"family":"Meiryo", "size":20}) # フォントファミリとフォントサイズを指定
fig.update_layout(showlegend=True) # 凡例を強制的に表示（デフォルトでは複数系列あると表示）
fig.update_layout(xaxis_type="linear", yaxis_type="log") # X軸はリニアスケール、Y軸はログスケールに
fig.update_layout(width=800, height=600) # 図の高さを幅を指定
fig.update_layout(template="plotly_white") # 白背景のテーマに変更
fig.show()