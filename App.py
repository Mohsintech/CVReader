import streamlit as st
import pandas as pd
import base64,random
import time,datetime
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io,random
from streamlit_tags import st_tags
from PIL import Image
import pymysql
from Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos
import pafy
import plotly.express as px

import docx2txt
import nltk

def get_table_download_link(df,filename,text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    # href = f'<a href="data:file/csv;base64,{b64}">Download Report</a>'
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    # pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)




def insert_data(name,email,res_score,timestamp,no_of_pages,reco_field,cand_level,skills,recommended_skills,courses):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (name, email, str(res_score), timestamp,str(no_of_pages), reco_field, cand_level, skills,recommended_skills,courses)
    cursor.execute(insert_sql, rec_values)
    connection.commit()
    
    
def extract_names(txt):
    person_names = []
 
    for sent in nltk.sent_tokenize(txt):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            if hasattr(chunk, 'label') and chunk.label() == 'PERSON':
                person_names.append(
                    ' '.join(chunk_leave[0] for chunk_leave in chunk.leaves())
                )
 
    return person_names

st.set_page_config(
   page_title="CV Parsing Solution",
   page_icon='./Logo/SRA_Logo.ico',
)
def run():
    st.title("CV Parsing Solution")
    st.sidebar.markdown("#Select Category")
    activities = ["NCR Employee", "Non NCR Employee"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
    # link = '[©Developed by Spidy20](http://github.com/spidy20)'
    # st.sidebar.markdown(link, unsafe_allow_html=True)
    img = Image.open('./Logo/logo.jpg')
    st.image(img)

    # Create the DB
    #db_sql = """CREATE DATABASE IF NOT EXISTS SRA;"""
    #cursor.execute(db_sql)

    # Create table
    #DB_table_name = 'user_data'
    
    #cursor.execute(table_sql)
    if choice == 'NCR Employee':
        # st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>* Upload your resume, and get smart recommendation based on it."</h4>''',
        #             unsafe_allow_html=True)
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            # with st.spinner('Uploading your Resume....'):
            #     time.sleep(4)
            save_image_path = './Uploaded_Resumes/'+pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                ## Get the whole resume data
                resume_text = pdf_reader(save_image_path)

                person_names = []
 
                for sent in nltk.sent_tokenize(resume_text):
                    for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
                        if hasattr(chunk, 'label') and chunk.label() == 'PERSON':
                            person_names.append(
                                ' '.join(chunk_leave[0] for chunk_leave in chunk.leaves())
                            )

                st.header("**Resume Analysis**")
                st.success("Hello "+ resume_data['name'])
                st.subheader("**Your Basic info**")
                st.subheader(person_names)
                try:
                    st.text('Name: '+resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Resume pages: '+str(resume_data['no_of_pages']))
                except:
                    pass
                cand_level = ''
                dataframe = pd.DataFrame()
                dataframe = resume_data
                st.subheader("Your Skills")
                ## Skill shows
                keywords = st_tags(label='### Skills that you have', text='See our skills recommendation',value=resume_data['skills'],key = '1')

                ##  recommendation
                ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                               'javascript', 'angular js', 'c#', 'flask']
                android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
                ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
                uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']

                recommended_skills = []
                reco_field = ''
                rec_course = ''
                               
                # Insert into table
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date+'_'+cur_time)

                ### Resume writing recommendation
                resume_score = 0
                if 'Objective' in resume_text:
                    resume_score = resume_score+20
                   
                else:
                    st.markdown('''<h4 style='text-align: left; color: #fabc10;'>[-] Objective Not Found.</h4>''',unsafe_allow_html=True)

                if 'Hobbies' or 'Interests'in resume_text:
                    resume_score = resume_score + 20
                    
                else:
                    st.markdown('''<h4 style='text-align: left; color: #fabc10;'>[-] Hobbies Not Found.</h4>''',unsafe_allow_html=True)

                if 'Achievements' in resume_text:
                    resume_score = resume_score + 20
                    
                else:
                    st.markdown('''<h4 style='text-align: left; color: #fabc10;'>[-] Achievements not found.</h4>''',unsafe_allow_html=True)

                if 'Projects' in resume_text:
                    resume_score = resume_score + 20
                    
                else:
                    st.markdown('''<h4 style='text-align: left; color: #fabc10;'>[-] Projects Not Found</h4>''',unsafe_allow_html=True)

                st.subheader("**Resume Score📝**")
                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )
                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(resume_score):
                    score +=1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)
                st.success('** Resume Score: ' + str(score)+'**')
                st.warning("** Note: This score is calculated based on the content that you have added in your Resume. **")
              
                st.subheader(resume_data['skills'])

                #connection.commit()
            else:
                st.error('Something went wrong..')
run()