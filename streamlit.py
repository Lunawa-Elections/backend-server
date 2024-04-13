from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd
import requests, io

column_names = ['Num', 'Name', 'Vaas', 'Votes']
st.set_page_config(page_title="Voting Data Dashboard", layout="wide")

def fetch_data(url):
    try:
        response = requests.get(url+'stats/')
        if response.status_code == 200:
            return response.text
    except:
        st.error("Server Error failed to fetch Data!")
        return None
    
def main():
    col1, col2, col3 = st.columns(3)
    api_url = col1.text_input('Enter the API URL', 'http://localhost:8000/')
    reload_time = col2.text_input('Auto Reload Dashboard (in Seconds)', '5')
    # auto_reload = col3.checkbox("Auto-reload data", value=False)

    with col3:
        col3_row1 = st.columns(1)
        with col3_row1[0]:
            auto_reload = st.checkbox("Auto-reload data", value=False)

        col3_row2 = st.columns(1)
        with col3_row2[0]:
            reload = st.button('Reload Now')


    if auto_reload: st_autorefresh(interval=int(reload_time)*1000, key='data_refresh')

    csv_data = fetch_data(api_url)
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
            fig.update_layout(
                title=f"Votes for {name}",
                xaxis_title="Member Name",
                yaxis_title="Votes",
                xaxis_tickangle=-10,
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
    main()
