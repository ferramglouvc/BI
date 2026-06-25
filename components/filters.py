import streamlit as st


def render_filters(df, project_leaders):
    all_salesrooms = sorted(
        df["SalesRoom"].dropna().astype(str).unique().tolist(),
        key=str.lower
    )

    leader_names = sorted(
        [name for name in project_leaders.keys() if name != "ALL"],
        key=str.lower
    )

    leader_options = ["ALL"] + leader_names

    project_leader = st.selectbox(
        "Select Project Leader",
        leader_options
    )

    if project_leader == "ALL":
        leader_salesrooms = all_salesrooms
    else:
        leader_salesrooms = sorted(project_leaders[project_leader], key=str.lower)

    salesroom_options = ["ALL"] + leader_salesrooms

    salesroom = st.selectbox(
        "Select SalesRoom",
        salesroom_options
    )

    if salesroom == "ALL":
        selected_salesrooms = leader_salesrooms
    else:
        selected_salesrooms = [salesroom]

    return project_leader, salesroom, selected_salesrooms
