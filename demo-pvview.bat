
title EPICS PvView
call %HOME%\Apps\Anaconda\Scripts\activate.bat 
call conda activate bluesky

cd %HOME%\Documents\eclipse\pvview
call python pvview.py sky:datetime sky:UPTIME sky:alldone sky:m1.DESC sky:m1.RBV sky:m1.VAL sky:m1.DMOV
