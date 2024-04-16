# from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd
import requests, io

st.set_page_config(page_title="Voting Dashboard", layout="wide")
column_names = ['Num', 'Name', 'Vaas', 'Votes']

def fetch_data():
    try:
        response = requests.get('http://localhost/stats/')
        if response.status_code == 200:
            return response.text
    except:
        st.error("Server Error failed to fetch Data!")
        return None
    
def main():
    csv_data = fetch_data()
    if csv_data:
        data = pd.read_csv(io.StringIO(csv_data), names=column_names, index_col="Num")
        data["Name"] = data["Name"].str.split(' ').str[0]
        vaas_groups = data.groupby('Vaas')

        plots = []
        for name, group in vaas_groups:
            fig = go.Figure(data=[
                go.Bar(
                    x=group['Name'], 
                    y=group['Votes'],
                    marker=dict(color=px.colors.qualitative.Plotly)
                )
            ])
            angle = -45 if len(group['Name']) > 3 else 0
            fig.update_layout(
                title=f"Votes for {name}",
                yaxis_title="Votes",
                xaxis_tickangle=angle,
                yaxis=dict(dtick=1),
                height=300,
                width=300
            )
            plots.append(fig)

        rows = [st.columns(4) for _ in range(3)]
        for row, fig in zip(sum(rows, []), plots):
            with row:
                st.plotly_chart(fig, use_container_width=True)
    
if __name__ == '__main__':
    col1, col2 = st.columns([5, 1])
    col1.title("Lunawa Voting Dashboard")
    if col2.button('Reload'): st.experimental_rerun()
    main()
    # st_autorefresh(interval=30000, key='data_refresh')