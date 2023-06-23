import streamlit as st
import numpy as np
import pandas as pd
import os
# For DB Connection
import psycopg2
import urllib
from streamlit_pills import pills

st.set_page_config(page_title=None, page_icon=None, layout='centered', initial_sidebar_state='collapsed')

"""
# arXiv Paper Search

"""

conn = psycopg2.connect('postgresql://gpadmin:changeme@35.225.47.84:5432/warehouse')


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
def search_result(i: int, url: str, title: str, highlights: str,
                  author: str, length: str, **kwargs) -> str:
    """ HTML scripts to display search results. """
    return f"""
        <div style="font-size:120%;">
            {i + 1}.
            <a href="{url}">
                {title}
            </a>
        </div>
        <div style="font-size:95%;">
            <div style="color:grey;font-size:95%;">
                {url[:90] + '...' if len(url) > 100 else url}
            </div>
            <div style="float:left;font-style:italic;">
                {author} ·&nbsp;
            </div>
            <div style="color:grey;float:left;">
                {length} ...
            </div>
            {highlights}
        </div>
    """
def tag_boxes(search: str, tags: list, active_tag: str) -> str:
    """ HTML scripts to render tag boxes. """
    html = ''
    search = urllib.parse.quote(search)
    for tag in tags:
        if tag != active_tag:
            html += f"""
            <a id="tags" href="?search={search}&tags={tag}">
                {tag.replace('-', ' ')}
            </a>
            """
        else:
            html += f"""
            <a id="active-tag" href="?search={search}">
                {tag.replace('-', ' ')}
            </a>
            """

    html += '<br><br>'
    return html

def show_papers(df, show_abstract):
    for index, row in df.iterrows():

        st.markdown(f'{index+1}.  **{row.title}**. *{row.authors}*. :blue[{row.year}].')
        if show_abstract:
            with st.expander(""):
                #st.markdown(row.abstract)
                st.info(row.abstract)
        pills("", row.categories.split(','), key = str(index)+str(row.categories))



def search_keywords(
        button_clicked, data_load_state,
        key_words, year_begin, year_end, max_show,
        show_abstract):
    if button_clicked:
        data_load_state.markdown('Searching paper...')



        # query_string = f""" with cte_input_arxiv as (select t.* from match_arxiv_articles((generate_arxiv_search_embeddings('{key_words}')), 0, 10) t) select * from cte_input_arxiv order by similarity desc;"""

        query_string = f"""
        set optimizer to off; 
        set enable_nestloop to off;
        with cte_query_embedding as (select generate_arxiv_search_embeddings('{key_words}') as query_embedding) ,
        cte_filter_table as (select * from arxiv_articles where year >= {year_begin} and year <= {year_end}),
        cte_input_arxiv as (
                SELECT
                       documents.abstract,
                    documents.title, documents.year, documents.authors, documents.categories,
                       1 - (documents.vector <=> cte_query_embedding.query_embedding) AS similarity
                     FROM cte_filter_table documents, cte_query_embedding
                     ORDER BY  1 - (documents.vector <=> cte_query_embedding.query_embedding) DESC
                     LIMIT {max_show}

        )
        , cte_result as (select distinct on (title) * from cte_input_arxiv)
        select * from cte_result order by similarity DESC;
        
        """
        print(query_string)
        dt = pd.read_sql(query_string, con = conn)
        #dt  =dt.drop_duplicates(subset=['title'], keep='last')
        #dt = dt[(dt.year >= year_begin) & (dt.year <= year_end)]
        data_load_state.markdown(f'**{dt.shape[0]} Papers Found**')
        show_papers(dt.head(int(max_show)), show_abstract)

def sidebar_info():
    #st.sidebar.image("Code/gp_icon.png")

    st.sidebar.header("About")
    st.sidebar.markdown("""
    <div style="font-size: small; font-style: italic">
    This is a simple app to search for <b>arXiv scientific papers</b> leveraging  <font color="green"> VMware Greenplum data warehouse </font> and <font color="blue"> pgvector extension </font> to store articles as vector embeddings.<br>
    It allows <b>semantic smart search</b> for scientific papers.<br>
    </div>
    """, unsafe_allow_html=True)


    st.sidebar.subheader("Experimental Config")
    show_abstract = st.sidebar.checkbox("show abstract", value=False)

    return show_abstract


def hide_right_menu():
    # ref: https://discuss.streamlit.io/t/how-do-i-hide-remove-the-menu-in-production/362/3
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def main():
    show_abstract = sidebar_info()
    # st.text(os.getcwd())
    hide_right_menu()

    #local_css("Code/style.css")

    form = st.form(key='search')


    key_words = form.text_input('Perform semantic search')
    button_label = 'Search'


    a1, a2 = form.columns([1.08, 1]) # 1.53 without " & configs!"
    button_clicked = a1.form_submit_button(label=button_label)


    # alternatively add show abstract here
    # show_abstract = a3.checkbox("show abstract", value=False)

    js = ['aer', 'jpe', 'qje', 'ecta', 'restud',
          'aejmac', 'aejmic', 'aejapp', 'aejpol', 'aeri',
          'restat', 'jeea', 'eer', 'ej',
          'jep', 'jel', 'are',
          'qe', 'jeg',
          'jet', 'te', 'joe',
          'jme', 'red', 'rand', 'jole', 'jhr',
          'jie', 'ier', 'jpube', 'jde',
          'jeh', 'ehr',
          "jhe",
          'jpemic', 'jpemac'
          ]
    js_ = ["jae","geb","jinde","jlawe","jebo","ee","ectt","imfer","ecot","jmcb","jue","edcc","sje","ecoa",
            "jaere","jeem","wber","ieio","jleo","le","jpope","qme","ei","jedc","cej","obes","jems","jes","jmate",
            "rsue","eedur","jhc","efp","aler","jbes","jru","jpam","jfe",
            'eeh',
            ]

    js += js_
    js_cats = {"all": js,
               "top5": ['aer', 'jpe', 'qje', 'ecta', 'restud'],
               "general": ['aer', 'jpe', 'qje', 'ecta', 'restud', 'aeri', 'restat', 'jeea', 'eer', 'ej', 'qe'],
               "survey": ['jep', 'jel', 'are', ]
               }
    js_cats_keys = list(js_cats.keys())


    year_min = 1900
    year_max = 2023

    c1, c2, c3 = form.columns(3)
    year_begin = c1.number_input('Year from', value=1980, min_value=year_min, max_value=year_max)
    year_end = c2.number_input('Year to', value=year_max, min_value=year_min, max_value=year_max)
    max_show = c3.number_input('Top-N. Search', value=100, min_value=0, max_value=500)

    data_load_state = st.empty()


    search_keywords(button_clicked,
                     data_load_state,
                    key_words, year_begin, year_end, max_show,
                    show_abstract)
