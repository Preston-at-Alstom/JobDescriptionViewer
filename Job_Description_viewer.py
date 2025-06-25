# importing all the required modules
from dataclasses import dataclass
from PyPDF2 import PdfReader
import pandas as pd
import streamlit as st
import backend
import datetime as dt


# create Job template
@dataclass
class Job():
    job_number          : str
    on_duty             : str
    on_duty_location    : str
    operating_time      : str
    work_time           : str
    split_time          : str
    trips               : list
    interact_with_crew  : list
    operating_days      : str
    off_duty            : str

# create Trip template
@dataclass
class Trip():
    job_number      : str = ''
    service_type    : str = ''
    train_number    : str = ''
    start_location  : str = ''  
    finish_location : str = ''
    departure       : str = ''
    arrival         : str = ''
    operating_days  : str = ''


st.set_page_config(
    page_title="Job Description Viewer ver 1.0",
    layout="wide",)

packages = ['TO-ON-25-084 - Job description_27Apr2025_baseline_Mon-Fri_2025-04-07_Full.pdf',
            'TO-ON-25-084 - Job description_27Apr2025_baseline_Sat-Sun_2025-04-07_Full.pdf'
            ]


today = dt.datetime.today()
day = today.weekday()


# if 0 <= day <= 5:
#         print('Weekday') 
# else:
#       print('Weekend')

weekday = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'mon-fri', 'mon-thu']
weekend = ['saturday', 'sunday', 'sat-sun']



loaded_package = packages[0]


form = st.form(key='my_form')
selected_job_package = form.selectbox('Select Job Package',packages, key=1)
submit_button = form.form_submit_button(label='Load Package')

if selected_job_package != loaded_package:
    loaded_package = selected_job_package


# creating a pdf reader object
reader = PdfReader(selected_job_package)



# Find the number of pages
number_of_pages = len(reader.pages)

# Create list to hold all the jobs
Job_Descriptions = [""] * number_of_pages

# Create list to hold trip info for each job
Job_Trips = []


# Filter list 
filter = ["Non-Revenue", "Revenue", "DH", "VAN", "SHUTTLE", "Split from", 'takeover', 'handover','DEF' ,'FUEL', 'STBY']

# Loop through pages
for  page in range(number_of_pages):
    
    # Read page content
    page_content = reader.pages[page].extract_text()


    trips_list = []
    trips_list_obj = []
    interact_list = []    

    # Read line by line and extract data
    for line in page_content.splitlines():
        
        line_as_list = line.split()
        
        if len(line_as_list) > 0:
            first_item = line_as_list[0]


            if first_item == 'Operating':
                operating_time = line_as_list[-1]

            if first_item == 'Platform':
                on_duty_location = line_as_list[5][0:2]
                off_duty = line_as_list[8]
                split_time = line_as_list[11][0:5]

            if first_item == 'Work':                
                work_time = line_as_list[-1]

            if first_item in ['Valid', 'Eff' , 'Mon-Fri', 'Friday', 'Saturda', 'Sunday', 'Sat-Sun']:
                job_number = line_as_list[-1]
                operating_days = line_as_list[0]
                on_duty = line_as_list[-4]
                
            if first_item in ['Valid', 'Eff' , 'Mon-Fri', 'Friday', 'Saturda', 'Sunday', 'Sat-Sun']:
                job_number = line_as_list[-1]
                operating_days = line_as_list[0]
                on_duty = line_as_list[-4]


            if first_item in filter:  
                formatted_line  = ''  
                service_type    = ''
                train_number    = ''
                start_location  = ''
                finish_location = ''
                departure       = ''
                arrival         = ''


                if  first_item in ['VAN', 'Shuttle']:
                    service_type    = first_item
                    start_location  = line_as_list[1][0:2]
                    finish_location = line_as_list [2]
                    departure       = line_as_list[3]
                    arrival         = line_as_list[4]

                    formatted_line = f'{service_type} | {start_location} {departure} > {finish_location} {arrival}'
                    
                if  first_item in ["Non-Revenue", "Revenue"]:
                    service_type    = first_item
                    train_number    = line_as_list[2]
                    start_location  = line_as_list[3][0:2]
                    finish_location = line_as_list[4]
                    departure       = line_as_list[5]
                    arrival         = line_as_list[6]
                    
                    formatted_line = f'{train_number} | {service_type} | {start_location} {departure} > {finish_location} {arrival}'
                    
                if first_item in ['handover', 'takeover']:
                    interact_list.append(line_as_list[-1])
                    formatted_line = f'{first_item} > {line_as_list[-1]}'
                    
                if first_item in ['DH', 'SHUTTLE']:
                    service_type    = first_item
                    start_location  = line_as_list[1][0:2]
                    finish_location = line_as_list[2]
                    departure       = line_as_list[3]
                    arrival         = line_as_list[4]

                    formatted_line = f'{service_type} | {start_location} {departure} > {finish_location} {arrival}'
                        
                if first_item in ['FUEL', 'DEF']:
                    service_type    = first_item
                    train_number    = line_as_list[1]
                    start_location  = line_as_list[2][0:2]
                    finish_location = line_as_list[3]
                    departure       = line_as_list[4]
                    arrival         = line_as_list[5]

                    formatted_line = f'{service_type} | {start_location} {departure} > {arrival}'

                if first_item == 'STBY':
                    service_type    = first_item
                    start_location  = line_as_list[2][0:2]
                    departure       = line_as_list[4]
                    arrival         = line_as_list[5]

                    formatted_line = f'{service_type} | {start_location} {departure} > {arrival}'                


                trips_list.append(formatted_line)
                #Job_Trips.append(Trip(job_number, service_type, train_number, start_location, finish_location, departure, arrival, operating_days))

    
    Job_Descriptions[page] = Job(job_number , on_duty , on_duty_location , operating_time , work_time , split_time , trips_list , interact_list, operating_days , off_duty)




# Check for and remove duplicates (some job descriptioons span 2 pages)
backend.clear_duplicates(Job_Descriptions)



# Create dataframe from list of Jobs
df = pd.DataFrame([job.__dict__ for job in Job_Descriptions])


job_number_filter = st.text_input("Find Job Number :")

default_list_of_locations = ['AE','BR','HA','LI','LR','ML','RL','SH','WB','WR']
filtered_locations = []

# Create checkboxes for filtering terminals, alligned in a row. Default is unchecked
teminal_select_columns = st.columns(10)
with teminal_select_columns[0]: 
    ae = st.checkbox('Allendale (AE)', value = False)
with teminal_select_columns[1]: 
    br = st.checkbox('Bradford (BR)', value = False)
with teminal_select_columns[2]: 
    ha = st.checkbox('Hamilton (HA)', value = False)
with teminal_select_columns[3]: 
    li = st.checkbox('Lincolnville (LI)', value = False)
with teminal_select_columns[4]: 
    lr = st.checkbox('Lewis Road (LR)', value = False)
with teminal_select_columns[5]: 
    ml = st.checkbox('Milton (ML)', value = False)
with teminal_select_columns[6]: 
    rl = st.checkbox('Richmond Hill (RL)', value = False)
with teminal_select_columns[7]: 
    sh = st.checkbox('Shirley (SH)', value = False)
with teminal_select_columns[8]: 
    wb = st.checkbox('Willowbrook (WB)', value = False)
with teminal_select_columns[9]:
    wr = st.checkbox('WRMF (WR)', value = False)

# List to hold terminal checkbox results
selected_locations = [ae,br,ha,li,lr,ml,rl,sh,wb,wr]

# Add selected terminals to the filtered list
if any(selected_locations):
    filtered_locations = []
    if ae : filtered_locations.append('AE')
    if br : filtered_locations.append('BR')
    if ha : filtered_locations.append('HA')
    if li : filtered_locations.append('LI')
    if lr : filtered_locations.append('LR')
    if ml : filtered_locations.append('ML')
    if rl : filtered_locations.append('RL')
    if sh : filtered_locations.append('SH')
    if wb : filtered_locations.append('WB')
    if wr : filtered_locations.append('WR')

else:
    filtered_locations = default_list_of_locations.copy()


if job_number_filter != '':
    filtered_df = df[df['job_number'].str.contains(job_number_filter, case=False)]
else:
    filtered_df = df


filtered_df = filtered_df.loc[filtered_df['on_duty_location'].isin(filtered_locations)]

st.dataframe(filtered_df, height=600, hide_index=True)
