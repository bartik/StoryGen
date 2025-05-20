@echo off
REM Step One
REM expand the one sentence describing the story into a paragraph
python scenes2description.py -c story_01.ini -n SENTENCE2PARAGRAPH

REM Step Two
REM Write the character story
python scenes2description.py -c story_01.ini -n STORY4CHARACTER
REM Each character into its own file
python t2t.py -c story_01.ini -n CHARACTER2SPLIT

REM Step two and a half
REM create character charts
python scenes2description.py -c story_01.ini -n PERSONALITY2CHART

REM Step Three
REM For each sentence create a paragraph
python scenes2description.py -c story_01.ini -n PARAGRAPH2EXPAND

REM Step Four
REM Create a summary for each character
python scenes2description.py -c story_01.ini -n PARAGRAPH2SUMMARY

REM Step Four and a half
REM Create a beatsheet
python scenes2description.py -c story_01.ini -n EXPAND2BEATSHEET

REM Step Five
REM Expand the paragraph from from the text below into a full-page rundown
REM Split paragraphs
python t2t.py -c story_01.ini -n SPLIT4RUNDOWN
REM create rundowns
python scenes2description.py -c story_01.ini -n PARAGRAPH2RUNDOWN

REM Step Six
REM Create a scene list from the rundowns
python scenes2description.py -c story_01.ini -n RUNDOWN2SCENES

REM Step Seven
REM Create descriptions for each scene
REM Split paragraphs
python t2t.py -c story_01.ini -n SPLIT4DESCRIPTION
REM create rundowns
python scenes2description.py -c story_01.ini -n SCENES2DESCRIPTION

REM Step Eight
REM Create the first draft
python scenes2description.py -c story_01.ini -n DESCRIPTION2DRAFT
python merge1level.py -c story_01.ini -n DRAFT2MERGE
python merge1level.py -c story_01.ini -n DRAFT4MERGE
