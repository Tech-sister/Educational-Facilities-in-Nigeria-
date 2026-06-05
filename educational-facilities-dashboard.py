#import libraries
import streamlit as st
import pandas as pd
import plotly.express as px


#set config page
st.set_page_config(
    page_title="Educational Facilities in Nigeria Dashboard",
    page_icon="📗",
    layout="wide"
 )

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/educational_Cleaned_Data.csv")
        return df
    except FileNotFoundError as e:
        st.warning(f"An error occured: {e}")




def create_sidebar_filters(df):
    st.sidebar.header("Educational Filters")

    Facility_Type_Display = st.sidebar.multiselect(
        "Select Facility_Type_Display",
        options=df['Facility_Type_Display'].unique(),
        default=df['Facility_Type_Display'].unique()
    )

    management = st.sidebar.multiselect(
        "Select management(s)",
        options=df['management'].unique(),
        default=df['management'].unique()
    )

    unique_lga = st.sidebar.multiselect(
        "Select unique_lga(s)",
        options=df['unique_lga'].unique(),
        default=df['unique_lga'].unique()
    )


    return Facility_Type_Display, management, unique_lga

def filter_data(df, Facility_Type_Display, management, phcn_Electricity):
    filtered_df = df[df['Facility_Type_Display'].isin(Facility_Type_Display) & df['management'].isin(management)]
    return filtered_df

def display_metrics(filtered_df):
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("🏨 Total school", f"{len(filtered_df):,.2f}")

    with col2:
        st.metric("👨‍👩‍👧‍👦 num student total", f"{len (filtered_df):,.2f}")

    with col3:
        avg_students = filtered_df['Total_Number_students'].mean() if len(filtered_df) > 0 else 0
        st.metric("🤷‍♂️ avg students", f"{avg_students:,.2f}")

    with col4:
        electricity_pct = (filtered_df['PHCN_Electricity'] == True).sum() / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
        st.metric("💡 PHCN Electricity", f"{electricity_pct:,.1f}%")

    with col5:
        Water_pct = (filtered_df['Improved_Water_Supply'] == True).sum() / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
        st.metric("💧Improved Water Supply", f"{Water_pct:.1f}%")

def display_charts(filtered_df):
    if len(filtered_df) == 0:
        st.warning("No filter data to display. Please adjust the data from the sidebar")
        return
    col1, col2 = st.columns(2)

    
    st.subheader("Distribution of school types")
    Facility_counts = filtered_df['Facility_Type_Display'].value_counts()
    fig1 = px.bar(
        x=Facility_counts.values,
        y=Facility_counts.index,
    )
    fig1.update_layout(xaxis_title="Count", yaxis_title="School Type")
    st.plotly_chart(fig1, width='stretch')
    

    fig2 = px.histogram(
    filtered_df, x='Total_Number_students', nbins=50,
          title="Student population distribution"
    )
    fig2.update_traces(marker_line_color='white',marker_line_width=1)
    st.plotly_chart(fig2, width='stretch')

    with col1:
        comparison = (filtered_df.groupby('management')[['num_student_total', 'num_teachers_total']].mean().reset_index())   
        fig3= px.bar(
            comparison,
            x='management',
            y=['num_student_total', 'num_teachers_total'],
            barmode='group',
            title='Public vs Private Schools: Average Students and Teachers',
            labels={
                'management': 'School Management',
                'value': 'Average Count',
                'variable': 'Metric'
            }
        )
        st.plotly_chart(fig3, width='stretch')


    with col2:
        Water_pct = (
        filtered_df['Improved_Water_Supply'].mean() * 100
        )
        Sanitation_pct = (filtered_df['Improved_Sanitation'].mean() * 100)

        access = pd.DataFrame({
            'Category':['Water','Sanitation'],
            'Percentage':[Water_pct,Sanitation_pct]
    
        })
        fig4 = px.pie(
            access,
            values='Percentage',
            names='Category',
            title=' Water and Sanitation access'
        )
        st.plotly_chart(fig4, width='stretch')

    col3, col4 = st.columns(2)
    with col3:
        electricity_counts = filtered_df['PHCN_Electricity'].value_counts().reset_index()
        electricity_counts.columns = ['Electricity', 'Count']

        fig5 = px.pie(
        electricity_counts,
        names='Electricity',
        values='Count',
        title='Electricity Availability in Schools'
        )
        st.plotly_chart(fig5, width='stretch')

    with col4:
        fig6 = px.scatter_mapbox(filtered_df,
            lat='latitude',
            lon='longitude',
            hover_name='Facility_name',
            zoom=4,
            height=600
        )
        fig6.update_layout(
            mapbox_style='open-street-map'
        )
        st.plotly_chart(fig6, width='stretch')

def display_table_data(filtered_df):
    if len (filtered_df) > 0:
        st.dataframe(filtered_df, width='stretch', height=300)
    else:
        st.warning("No Educational data to display")

        csv = filtered_df.to_csv(index=False)

        st.download_button(
            label="Download Filtered Data",
            data=csv,
            file_name='filtered_data.csv',
            mime='text/csv'
            )




def main():
    #load dataset
    df = load_data()

    #sidebar
    Facility_Type_Display, management, unique_lga =  create_sidebar_filters(df)

    #filtered_data
    filtered_df = filter_data(df, Facility_Type_Display, management, unique_lga)

    st.title("Educational Facilities in Nigeria Dashboard")
    st.markdown("---")
    #display metrics
    display_metrics(filtered_df)

    # display chart
    display_charts(filtered_df)
    # display table_data
    display_table_data(filtered_df)
# st.subheader("Insights & Recommendations")

# st.markdown("""
# **Major Findings**
# - Many schools lack reliable electricity access.
# - Water and sanitation facilities are not evenly distributed across Nigeria.
# - Public schools generally serve larger student populations than private schools.
# - Some states have significantly higher school densities than others.

# **Recommendations**
# - Prioritize investment in electricity and sanitation infrastructure.
# - Allocate more teachers to schools with high student-to-teacher ratios.
# - Use geographic data to target underserved LGAs and states.
# - Support data-driven planning through continuous monitoring of educational facilities.
# """)

    


main()