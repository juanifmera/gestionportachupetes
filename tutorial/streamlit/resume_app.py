import streamlit as st
import pandas as pd
from datetime import datetime
import time

st.set_page_config('Project Numer 1', page_icon='🦈', layout='wide')
st.title('Primer Proyecto / Resume App')
st.subheader('Juan Ignacio Francisco Mera - Python Developer', divider='rainbow')

st.sidebar.title('Navegation')
section = st.sidebar.radio(' Go to:', ['ABOUT', 'SKILLS', 'EXPERIENCE', 'EDUCATION', 'CONTACT'])

skills = {
    'Python':0.8,
    'Machine Learning':0.9,
    'Streamlit': 0.9,
    'SQL': 0.7,
    'Data Visualization': 0.8
}

if section == 'ABOUT':
    st.markdown(
        '''
        Experienced data scientist with sttrong skills in analytics, machine learning and storytelling with data.
        Passionate about turning data into actionable insights
        '''
    )

elif section == 'SKILLS':
    st.header('Skills Overview')

    for skill, level in skills.items():
        
        st.write(f'Skills: {skill}')
        st.progress(level)

    df_skills = pd.DataFrame({
            'Skill':list(skills.keys()),
            'Proficiency':list(skills.values())
        })

    st.dataframe(df_skills)
    st.bar_chart(df_skills.set_index('Skill'), horizontal=True)
        

elif section == 'EXPERIENCE':

    with st.expander(f'Data Scientist | Carrefour Argentina | June 2025'):
        st.write(f'''
                - Built 5 Streamlit apps in production
                - Built 30+ Dashboards for risk and underwriting
                - Developed 20 DBT Models
                    ''')
    
    with st.expander (f'Co-Founder | UdiBaby | Ago 2025'):
        st.write(f'''
                - Created System to keep Orders, Stocks and Materials
                - Developed a new Sale System
                - Developed Fair Sales
                    ''')
        
    with st.expander (f'Senior Data Analyst | EY | June 2022'):
           
        bullets = [
            "- Developed Dashboards for workflow",
            "- Automated Sysytems",
            "- Created value for BlackRock and Bank of America"
            ]
        
        with st.spinner('Processing Info ...'):
            for message in bullets:
                time.sleep(2)
                st.markdown(message)
            time.sleep(1)
            st.success('All items have been display')


elif section == 'EDUCATION':

    tabs = st.tabs(['Primary Education', 'Bachelors Educations'])

    with tabs[0]:
        with st.expander('See this'):
            st.write('Hello!')

    with tabs[1]:
        st.color_picker('COLOR PICKER!')
            

elif section == 'CONTACT':
    st.header('Get in Touch')

    col1, col2 = st.columns(2)

    with col1:
        st.write('Phone 1126640509')

    with col2:
        st.write('email: juanignaciofmera@gmail.com')