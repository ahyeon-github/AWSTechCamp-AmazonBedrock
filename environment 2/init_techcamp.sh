#!/bin/sh

echo "Create TechCamp Default Directory and Files"

mkdir -p techcamp/app/pages
mkdir -p techcamp/lambdas/1_summaryfunc
mkdir -p techcamp/lambdas/2_shortformfunc

cd techcamp/app
echo "boto3==1.34.59
streamlit==1.32.2
requests==2.31.0
python_dateutil==2.8.1" > requirements.txt
touch Home.py

cd pages
touch 1_Review_Summary.py
touch 2_Video_Shortform.py

cd ../../lambdas/1_summaryfunc
touch lambda_handler.py

cd ../2_shortformfunc
touch lambda_handler.py
