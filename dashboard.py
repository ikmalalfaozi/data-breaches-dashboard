import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px
import pandas as pd
import altair as alt

st.set_page_config(page_title="Data Breaches", page_icon="🔐", layout="wide")

# Fetch Data
csv_url = "data_breaches.csv"
df = pd.read_csv(csv_url)

# Sidebar -> Image Icon
st.markdown(
    """
    <style>
        [data-testid=stSidebar] [data-testid=stImage]{
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True
)
# https://www.svgrepo.com/svg/308517/data-breach?edit=true
st.sidebar.image("./images/data-breach.svg", width=128)

# Sidebar -> Menu
with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",
        options=["Dashboard", "Data"],
        icons=["house", "table"],
        menu_icon="cast",
        default_index=0
    )

# Sidebar -> Filter
st.sidebar.header("Filter")
years = st.sidebar.slider("Year", min_value=2004, max_value=2023, value=(2003, 2024))
org_types = st.sidebar.multiselect(
    "Select Organization Type",
    options=df["Organization type"].unique(),
    default=df["Organization type"].unique(),
)
methods = st.sidebar.multiselect(
    "Select Method",
    options=df["Method"].unique(),
    default=df["Method"].unique(),
)

# show data
selected_df = df.query(f"Year >= {years[0]} and Year <= {years[1]} and `Organization type` in {org_types} and Method in {methods}")

def Data():
    with st.expander("View Dataset"):
        show_data = st.multiselect("Filter: ", selected_df.columns.tolist(), default=selected_df.columns.tolist())
        st.dataframe(selected_df[show_data],
                     use_container_width=True,
                     column_config={'Year': st.column_config.NumberColumn(format="%d")})

    # Compute for analytics
    # total data and records
    total_data = len(selected_df)
    total_records = selected_df['Records'].sum()

    st.markdown(f'<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
    total1, total2 = st.columns(2, gap='small')
    with total1:
        st.info(f'Total Data: \n\n{total_data}', icon="📌")

    with total2:
        st.info(f'Total Records: \n\n{total_records:,.0f}', icon="📌")
    st.markdown(f'</div>', unsafe_allow_html=True)

    # Total Organization Type
    st.markdown(f'<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
    st.info('Organization Type:', icon="📌")
    organization_types = df['Organization type'].unique()
    organization_counts = selected_df['Organization type'].value_counts()
    for i in range(4):
        cols = st.columns(4, gap="small")
        for j, col in enumerate(cols):
            with col:
                t = organization_types[i*4 + j]
                st.info(f"{t.capitalize()}: \n\n{organization_counts.get(t, 0)}")
    st.markdown(f'</div>', unsafe_allow_html=True)

    # Total Method
    st.markdown(f'<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
    st.info('Method', icon="📌")
    method_types = df['Method'].unique()
    method_counts = selected_df['Method'].value_counts()
    for i in range(2):
        cols = st.columns(3, gap="small")
        for j, col in enumerate(cols):
            with col:
                t = method_types[i * 3 + j]
                st.info(f"{t.capitalize()}: \n\n{method_counts.get(t, 0)}")
    st.markdown(f'</div>', unsafe_allow_html=True)


def Dashboard():
    # line chart
    df_years = selected_df.groupby('Year')['Records'].sum().reset_index()
    df_years['Year'] = df_years['Year'].astype('str')
    df_years = df_years.rename(columns={"Records": 'Number of Records'})
    st.markdown("<h3 style='text-align: center;'>Data Breach Instances per Year</h3>", unsafe_allow_html=True)
    st.line_chart(df_years, x='Year', y='Number of Records')

    # bar chart: organization type
    st.markdown("<h3 style='text-align: center;'>Sector Breakdown</h3>", unsafe_allow_html=True)
    chart = (
        alt.Chart(selected_df)
        .mark_bar()
        .encode(
            x=alt.X("Records", type="quantitative", title="Number of Records"),
            y=alt.Y("Organization type", type="nominal", title="Sector", sort="-x"),
            color=alt.Color("Method", type="nominal", title="Method"),
            order=alt.Order('Method', sort="ascending"),
        )
        .properties(
            height=400,
        )
        .interactive()
    )

    st.altair_chart(chart, use_container_width=True)

    # bar chart: method type
    st.markdown("<h3 style='text-align: center;'>Method Breakdown</h3>", unsafe_allow_html=True)
    chart = (
        alt.Chart(selected_df)
        .mark_bar()
        .encode(
            x=alt.X("Records", type="quantitative", title="Number of Records"),
            y=alt.Y("Method", type="nominal", title="Method", sort="-x"),
            color=alt.Color("Organization type", type="nominal", title="Sector"),
            order=alt.Order('Organization type', sort="descending"),
        )
        .interactive()
    )

    st.altair_chart(chart, use_container_width=True)

    # Tree map
    st.markdown("<h3 style='text-align: center; margin-bottom: -50px;'>Method and Sector Proportions</h3>", unsafe_allow_html=True)
    order = st.radio("", options=("Method", "Organization Type"), horizontal=True)
    if order == "Method":
        path = ['Method', 'Organization type']
    else:
        path = ['Organization type', 'Method']

    fig = px.treemap(selected_df, path=path, values='Records')
    fig.update_layout(margin=dict(t=0, l=5, r=5, b=5))
    st.plotly_chart(fig, use_container_width=True)

def sidebar():
    if selected == "Dashboard":
        st.header("Data Breaches Dashboard", divider=True)
        st.markdown("###")
        Dashboard()
    if selected == "Data":
        st.header("Data Breaches Detail", divider=True)
        st.markdown("###")
        Data()


sidebar()
