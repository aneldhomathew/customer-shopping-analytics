import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# ---------- 1. Load the data ----------
data = pd.read_csv("customer_shopping.csv")
amount = "Purchase Amount (USD)"  # short name for the long column

# ---------- 2. Sidebar filters ----------
st.sidebar.header("Filters")

categories = st.sidebar.multiselect(
    "Category", data["Category"].unique(), default=data["Category"].unique()
)
seasons = st.sidebar.multiselect(
    "Season", data["Season"].unique(), default=data["Season"].unique()
)
age_min, age_max = st.sidebar.slider("Age range", 18, 70, (18, 70))
size = st.sidebar.selectbox("Size", ["All", "S", "M", "L", "XL"])

# ---------- 3. Apply the filters ----------
df = data[data["Category"].isin(categories)]
df = df[df["Season"].isin(seasons)]
df = df[(df["Age"] >= age_min) & (df["Age"] <= age_max)]
if size != "All":
    df = df[df["Size"] == size]

# Stop if nothing matches the filters
if df.empty:
    st.warning("No data for these filters. Change the filters in the sidebar.")
    st.stop()

# ---------- 4. KPIs (side by side using columns) ----------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Records", len(df))
col2.metric("Total Purchase (USD)", int(df[amount].sum()))
col3.metric("Average Purchase (USD)", round(df[amount].mean(), 2))
col4.metric("Average Age", round(df["Age"].mean(), 1))

# ---------- 5. Tabs ----------
tab1, tab2, tab3, tab4 = st.tabs(
    ["Dataset Overview", "Data Analysis", "Visualizations", "Insights"]
)

# ----- Tab 1: Dataset Overview -----
with tab1:
    st.subheader("Dataset")
    st.dataframe(df)
    with st.expander("Summary statistics"):
        st.write(df[["Age", amount]].describe())

# ----- Tab 2: Data Analysis (group-by) -----
with tab2:
    st.subheader("Records by Category")
    st.write(df.groupby("Category")[amount].count())

    st.subheader("Total and Average Purchase by Category")
    st.write(df.groupby("Category")[amount].agg(["sum", "mean"]))

    with st.expander("Records by Season"):
        st.write(df.groupby("Season")[amount].count())

# ----- Tab 3: Visualizations -----
with tab3:
    # Bar chart: total purchase amount per category
    st.subheader("Bar Chart")
    bar_data = df.groupby("Category")[amount].sum()
    fig1, ax1 = plt.subplots()
    ax1.bar(bar_data.index, bar_data.values, color="steelblue")
    ax1.set_title("Total Purchase Amount by Category")
    ax1.set_xlabel("Category")
    ax1.set_ylabel("Total Purchase Amount (USD)")
    st.pyplot(fig1)
    st.write("Interpretation: the tallest bar is the category that earns the most money.")

    # Line chart and scatter plot side by side
    left, right = st.columns(2)

    with left:
        st.subheader("Line Chart")
        # Put ages into groups: 18-25, 26-35, ...
        df = df.copy()
        df["Age Group"] = pd.cut(
            df["Age"],
            bins=[17, 25, 35, 45, 55, 65, 100],
            labels=["18-25", "26-35", "36-45", "46-55", "56-65", "66+"],
        )
        line_data = df.groupby("Age Group", observed=True)[amount].mean()
        fig2, ax2 = plt.subplots()
        ax2.plot(line_data.index.astype(str), line_data.values,
                 marker="o", label="Average purchase")
        ax2.set_title("Average Purchase Amount by Age Group")
        ax2.set_xlabel("Age Group")
        ax2.set_ylabel("Average Purchase Amount (USD)")
        ax2.legend()
        st.pyplot(fig2)
        st.write("Interpretation: shows which age group spends more on average.")

    with right:
        st.subheader("Scatter Plot")
        fig3, ax3 = plt.subplots()
        # One colour per category so the legend is meaningful
        for cat in df["Category"].unique():
            part = df[df["Category"] == cat]
            ax3.scatter(part["Age"], part[amount], label=cat)
        ax3.set_title("Age vs Purchase Amount")
        ax3.set_xlabel("Age")
        ax3.set_ylabel("Purchase Amount (USD)")
        ax3.legend()
        st.pyplot(fig3)
        st.write("Interpretation: each dot is one customer; look for groups or outliers.")

# ----- Tab 4: Insights -----
with tab4:
    st.subheader("Key Insights")
    st.write("Top category (by total purchase):", df.groupby("Category")[amount].sum().idxmax())
    st.write("Top season (by total purchase):", df.groupby("Season")[amount].sum().idxmax())
    st.write("Top item (by total purchase):", df.groupby("Item Purchased")[amount].sum().idxmax())

    st.subheader("Age and Purchase Amount Correlation")
    correlation = df["Age"].corr(df[amount])
    st.write("Correlation:", round(correlation, 2))
    st.write("A value close to 0 means age and spending are not strongly related.")

    with st.expander("View Insight Data"):
        st.dataframe(df)