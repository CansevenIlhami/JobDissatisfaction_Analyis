#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np


# In[2]:


dete_survey = pd.read_csv("dete_survey.csv",na_values = "Not Stated")
tafe_survey = pd.read_csv("tafe_survey.csv")


# In[3]:


dete_survey_updated = dete_survey.drop(dete_survey.columns[28:49],axis=1)
tafe_survey_updated = tafe_survey.drop(tafe_survey.columns[17:66],axis=1)


# In[4]:


dete_survey_updated.columns = dete_survey_updated.columns.str.lower().str.strip().str.replace("_","")


# In[5]:


dete_survey_updated.head()


# In[6]:


tafe_survey_updated.rename(columns={"Record ID":"id",
                                    "CESSATION YEAR":"cease_date",
                                    "Reason for ceasing employment":"separationtype",
                                    "Gender. What is your Gender?":"gender",
                                    "CurrentAge. Current Age":"age",
                                    "Employment Type. Employment Type":"employment_status",
                                    "Classification. Classification":"position",
                                    "LengthofServiceOverall. Overall Length of Service at Institute (in years)":"institute_service",
                                    "LengthofServiceCurrent. Length of Service at current workplace (in years)":"role_service"},inplace=True)


# In[7]:


tafe_survey_updated


# In[8]:


dete_survey_updated["separationtype"].value_counts()
dete_survey_updated.columns = dete_survey_updated.columns.str.lower().str.strip().str.replace(' ', '_')


# In[9]:


tafe_survey_updated["separationtype"].value_counts()


# In[10]:


# Update all separation types containing the word "resignation" to 'Resignation'
dete_survey_updated['separationtype'] = dete_survey_updated['separationtype'].str.split('-').str[0]

# Check the values in the separationtype column were updated correctly
dete_survey_updated['separationtype'].value_counts()


# In[11]:


# Select only the resignation separation types from each dataframe
dete_resignations = dete_survey_updated[dete_survey_updated['separationtype'] == 'Resignation'].copy()
tafe_resignations = tafe_survey_updated[tafe_survey_updated['separationtype'] == 'Resignation'].copy()


# In[12]:


# Extract the years and convert them to a float type
dete_resignations['cease_date'] = dete_resignations['cease_date'].str.split('/').str[-1]
dete_resignations['cease_date'] = dete_resignations['cease_date'].astype("float")

# Check the values again and look for outliers
dete_resignations['cease_date'].value_counts()


# In[13]:


dete_resignations["institute_service"] = dete_resignations["cease_date"] - dete_resignations["dete_start_date"]


# In[14]:


dete_resignations["institute_service"]


# We see there are NaN values.

# In[15]:


tafe_resignations["Contributing Factors. Dissatisfaction"].value_counts()


# In[16]:


tafe_resignations["Contributing Factors. Job Dissatisfaction"].value_counts()


# In[17]:


def update_vals(element):
    if pd.isnull(element):
        element = np.nan
        return element
    if element == "-":
        return False
    else:
        return True


# In[18]:


tafe_resignations['dissatisfied'] = tafe_resignations[['Contributing Factors. Dissatisfaction', 'Contributing Factors. Job Dissatisfaction']].applymap(update_vals).any(1, skipna=False)
tafe_resignations_up = tafe_resignations.copy()


# In[19]:


tafe_resignations_up["dissatisfied"].value_counts(dropna=False)


# In[20]:


dete_resignations['dissatisfied'] = dete_resignations[['job_dissatisfaction',
       'dissatisfaction_with_the_department', 'physical_work_environment',
       'lack_of_recognition', 'lack_of_job_security', 'work_location',
       'employment_conditions', 'work_life_balance',
       'workload']].any(1, skipna=False)
dete_resignations_up = dete_resignations.copy()
dete_resignations_up['dissatisfied'].value_counts(dropna=False)


# In[21]:


dete_resignations_up["institute"] = "DETE"
tafe_resignations_up["institute"] = "TAFE"


# In[22]:


combined = pd.concat([dete_resignations_up, tafe_resignations_up], ignore_index=True)


# In[23]:


combined_updated = combined.dropna(thresh = 500, axis =1).copy()


# In[24]:


combined_updated['institute_service_up'] = combined_updated['institute_service'].astype('str').str.extract(r'(\d+)')
combined_updated['institute_service_up'] = combined_updated['institute_service_up'].astype('float')

# Check the years extracted are correct
combined_updated['institute_service_up'].value_counts()


# In[25]:


def transform_service(val):
    if val >= 11:
        return "Veteran"
    elif 7 <= val < 11:
        return "Established"
    elif 3 <= val < 7:
        return "Experienced"
    elif pd.isnull(val):
        return np.nan
    else:
        return "New"
combined_updated['service_cat'] = combined_updated['institute_service_up'].apply(transform_service)

# Quick check of the update
combined_updated['service_cat'].value_counts()


# In[26]:


combined_updated['dissatisfied'] = combined_updated['dissatisfied'].fillna(False)

# Calculate the percentage of employees who resigned due to dissatisfaction in each category
dis_pct = combined_updated.pivot_table(index='service_cat', values='dissatisfied')

# Plot the results
get_ipython().run_line_magic('matplotlib', 'inline')
dis_pct.plot(kind='bar', rot=30)


# In[ ]:




