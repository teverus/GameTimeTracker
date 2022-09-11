@echo off
mode con: cols=107 lines=38
title=Finnish Learner

: ==================================
: Installing virtual environment
: ==================================
echo Activating virtual environment. Please stand by...
set venv_name=venv
py -m venv %venv_name%
call %venv_name%\Scripts\activate
pip install -q -r requirements.txt

: ==================================
: Starting the application
: ==================================
py main.py

: ==================================
: So that we can read logs if needed
: ==================================
timeout -1