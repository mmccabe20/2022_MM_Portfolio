# 2022_MM_Portfolio
This repository holds a portfolio of my work researching biomechanics, with a particular focus on wearable technologies (inertial measurement units, force-measuring instrumented insoles) and machine learning.

# First upload: 2022_03_06_Hip_Angles_StairMaster_v_Walking
This upload includes a script (.py) and generated plots (.png). The script aggregates OpenSim inverse kinematics results (https://simtk-confluence.stanford.edu:8443/display/OpenSim/Getting+Started+with+Inverse+Kinematics) across 15 health subjects and two activities (walking: 2mph, stair ascent on a StairMaster: level 8). It then plots ensemble-averaged (averaged across subject gait cycles; heel strike = 0%) hip flexion, adduction, and internal rotation using seaborn relplot. The shaded area represents standard deviation rather than confidence intervals.
