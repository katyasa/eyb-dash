import streamlit as st
from PIL import Image

# Set page configuration
st.set_page_config(
    page_title="About",
    page_icon="👋",
)

# Custom CSS for centering title and adjusting image size
st.markdown(
    """
    <style>
    .css-1sbuyqz {
        text-align: center;
    }
    .stImage {
        max-width: 300px;
        height: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
    <style>
    a {
        color: #32a84a;  
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div style='text-align: center;'>
        <h1>🍋 Culinary Chronicles 🍯</h1>
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

st.markdown("## About", unsafe_allow_html=True)

st.markdown("""
    <div style='text-align: justify;'>
        <p>
            At the time of this writing, I own more close to 100 cookbooks totaling more than 16K recipes. For the past few years, I’ve been taking note of each recipe 
            I cook from my cookbooks and some online magazines, and I log these assets 
            to <a href="https://www.eatyourbooks.com/">EatYourBooks</a> (EYB).
        </p>
        <p>
            EYB is a website for all avid cookbook collectors. The EYB community has indexed 
            about 12.3K cookbooks (or 2.3 million recipes) for recipe names and ingredients. 
            As a member, I add my cookbooks to my virtual bookshelf.
        </p>
        <p>
            This means I have all recipe names, book titles, and also all ingredients 
            from my cookbooks that have been indexed (which is really most Anglophone books) 
            in a digital format. I use that to bookmark every recipe I cook with the month 
            and year when I cooked it. The assets I enter (my cookbooks and bookmarks) are 
            available for download as <code>.csv</code> files directly from the website.
        </p>
        <p style='text-align: center;'><strong>👈 Select from the sidebar!</strong></p>
    </div>
""", unsafe_allow_html=True)

IMAGE_PATH_01 = '../assets/cookbooks01.JPG'
IMAGE_PATH_02 = '../assets/cookbooks02.JPG'

with col1:
    st.image(IMAGE_PATH_01, use_column_width=None)

with col2:
    st.image(IMAGE_PATH_02, use_column_width=None)
