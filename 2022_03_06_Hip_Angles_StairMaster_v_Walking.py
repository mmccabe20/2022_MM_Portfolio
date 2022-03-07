#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Date: 2022-03-06
Filename: 2022_03_06_Hip_Angles_StairMaster_v_Walking
Author: Megan McCabe
Script Purpose: 
    Compare OpenSim inverse kinematic results (joint angles) between
    walking (2mph, 0.9m/s) and stair ascent (on a StairMaster, level=8)
    for 15 healthy subjects. Final results are plotted using seaborn
    and reflect ensemble averaging for each point in the gait cycle (0-100% 
    where 0% = heel strike)
    
'''
    
# 1. Import libraries
import scipy.io
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 2. Define parent folder filepaths
filepath_ikresults = '/Users/megan_mccabe/documents/school/thesis/data analysis/standard approach/results/'
filepath_synceddata = '/Users/megan_mccabe/documents/school/thesis/data analysis/ml approach/synced data/'
files_synceddata = os.listdir(filepath_synceddata)

# 3. Initialize dataframes for each activity
df_walk = pd.DataFrame()
df_stair = pd.DataFrame()

# 4. Load footedness of each subject
footedness = ['R','R','R','R','R','L','R','R','R','R','L','R','R','R','R','L','L']

# 5. Loop through subjects to load their inverse kinematics (IK) results and associated gait % vector (synceddata file)
for subj_id_num in range(1,18):
    
    if subj_id_num not in [4,11]:
        # Define subject id
        subj_id_var = '00'+str(subj_id_num)
        subj_id_var = 'S'+subj_id_var[-3:]
        
        # Identify subject's ik results filenames
        subject_ikresults_files = os.listdir(filepath_ikresults+subj_id_var+'/opensim ik/')
        subject_ikresults_files = [file for file in subject_ikresults_files if file[-3:] == 'mot']  
        
        # Identify subject's synceddata filename
        subject_synceddata_file = [file for file in files_synceddata if file[0:4] == subj_id_var][0]
    
        # Load synceddata, determine order of activities in file
        synceddata = scipy.io.loadmat(filepath_synceddata+subject_synceddata_file)
        
        syncdata_activity_order = dict()
        
        for i in range(4):
            activity_raw = synceddata['SyncedData'][0,i][0][0]
            activity = activity_raw.split('-')[0]
            syncdata_activity_order[activity] = i
        
        syncdata_activity_order.pop('stand')
        syncdata_activity_order.pop('stepup')
        
        # Loop through activities
        for act in syncdata_activity_order:
            act_index = syncdata_activity_order[act]
            
            gait_perc = synceddata['SyncedData'][0,act_index][5] # Let's focus on right foot for now
            '''
            # Pull the gait percentage vector, factoring in footedness
            if footedness[subj_id_num-1] == 'R':
                gait_perc = synceddata['SyncedData'][0,act_index][5]
            else:
                gait_perc = synceddata['SyncedData'][0,act_index][6]
            '''
            
            # Load the ikresults for that activity
            
            subj_act_ik_file = [f for f in subject_ikresults_files if act in f][0]
            
            #ik_file_activity_index = ik_activity_order.index(act)
            df_subj_ikresults = pd.read_table(
                filepath_ikresults+subj_id_var+'/opensim ik/'+subj_act_ik_file,
                sep='\t',header=8
                )
            
            # Insert the gait % vector into the ik results df
            df_subj_ikresults.insert(0,'gait_perc',gait_perc[:,0])
            
            # Remove rows w/ gait % = 999
            df_subj_ikresults = df_subj_ikresults[df_subj_ikresults['gait_perc']!=999]
            
            # convert gait percentage vector to int
            df_subj_ikresults['gait_perc'] = df_subj_ikresults['gait_perc'].astype('int64')
            
            # Insert new column w/ subject id into df
            subj_id_col = np.full((df_subj_ikresults.shape[0],1), subj_id_num)
            df_subj_ikresults.insert(0,'subject_id',subj_id_col)
            
            
            # Add data to subject-wide dfs
            if act == 'walk':
                df_walk = pd.concat([df_walk, df_subj_ikresults], ignore_index=True)
            elif act == 'stair':
                df_stair = pd.concat([df_stair, df_subj_ikresults], ignore_index=True)


# Pull the data across activities into one dataframe
activity_col_walk = list()
for i in range(df_walk.shape[0]):
    activity_col_walk.append('walk')
df_walk.insert(0,'activity',activity_col_walk)

activity_col_stair = list()
for i in range(df_stair.shape[0]):
    activity_col_stair.append('stair')
df_stair.insert(0,'activity',activity_col_stair)

df_all_activities = pd.concat([df_walk,df_stair],ignore_index=True)

id_cols = df_all_activities.columns[:4]
value_cols = df_all_activities.columns[4:]

df_all_activities_melt = df_all_activities.melt(id_vars=id_cols,value_vars=value_cols,var_name='metric_name',value_name='metric_value')

df_all_activities_hip = df_all_activities_melt[df_all_activities_melt['metric_name'].isin(['hip_flexion_r','hip_adduction_r','hip_rotation_r'])]

g = sns.relplot(
    data=df_all_activities_hip,
    kind='line',
    x='gait_perc',
    y='metric_value',
    hue='activity',
    col='metric_name',
    ci='sd',
    facet_kws={'sharey':False,'sharex': True})

g.set_axis_labels('gait percentage (heel strike = 0%)','angle (deg)')
g.axes[0,0].set_title('Hip Flexion')
g.axes[0,1].set_title('Hip Adduction')
g.axes[0,2].set_title('Hip Rotation')