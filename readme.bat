@echo off
REM Step One
REM expand the one sentence describing the story into a paragraph
python scenes2description.py .\story\01_sentence .\story\02_paragraph\ sentence_??.txt sentence_ paragraph_

REM Step Two
REM Write the character story
python scenes2description.py .\story\02_paragraph .\story\03_personality\ paragraph_??.txt paragraph_ personality_

REM Step Three
REM For each sentence create a paragraph with personality
python scenes2description.py .\story\02_paragraph .\story\04_expand\ paragraph_??.txt paragraph_ expand_

REM Step Four
REM Create a summary for each character
python scenes2description.py .\story\02_paragraph .\story\05_summary\ paragraph_??.txt paragraph_ summary_

REM Step Five
REM Expand the paragraph from from the text below into a full-page rundown
REM Split paragraphs
REM python text2paragraphs.py .\story\04_expand .\story\04_expand\ expand_??.txt expand_ expand_
REM create rundowns
python scenes2description.py .\story\04_expand\ .\story\06_rundown\ expand_??.txt expand_ rundown_

REM Step Six
REM Create a scene list from the rundowns
python scenes2description.py .\story\06_rundown\ .\story\08_scenes\ rundown_??.txt rundown_ scenes_

REM Step Seven
REM Create the first draft
python text2paragraphs.py .\story\09_description .\story\09_description\ description_??_??.txt description_ description_
python scenes2description.py .\story\09_description\ .\story\10_draft\ description_??_??_??.txt description_ draft_
python merge1level.py .\story\10_draft\ .\story\10_draft\ draft_??_??_??.txt draft_ draft_

