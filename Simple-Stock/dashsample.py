# 必要なライブラリをインポート。
import dash
# 描画に必要なグラフやボタン、ドロップダウンなどのUIを提供するパッケージ。
from dash import dcc 
# import dash_core_components as dcc
# `dash_html_components`は、DivタグやH1タグなどのHTMLタグを提供するパッケージ。
# import dash_html_components as html
from dash import html

# カスタムCSSのパスをリスト形式で指定。詳細は以下のDocs参照
# https://dash.plotly.com/external-resources
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# ファイル名をアプリ名として起動。その際に外部CSSを指定できる。
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# この`layout`にアプリの外観部分を指定していく。
# `dash_html_components`がHTMLタグを提供し、React.jsライブラリを使って実際の要素が生成される。
# HTMLの開発と同じ感覚で外観を決めることが可能
app.layout = html.Div(children=[
    # `dash_html_components`が提供するクラスは`childlen`属性を有している。
    # `childlen`属性を慣例的に最初の属性にしている。
    html.H1(children='Hello Dash'),

    html.Div(children='Dash: A web application framework for Python.'),

    # `dash_core_components`が`plotly`に従う機能を提供する。
    # HTMLではSVG要素として表現される。
    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    )
])


if __name__ == '__main__':
    # `debug=True`でhot-reloadingモードを有効にし、コード上の変更を画面に反映する。
    app.run_server(debug=True)