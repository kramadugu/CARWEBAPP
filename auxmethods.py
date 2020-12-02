import pandas as pd

dummy_html_template = '''
<html>
<head>
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<title> CAR WEB Application </title>
<h1> Web Application for CAR Analytics Capability Demo</h1>
<div id="logo"> 
	<img src="{{ url_for('static', filename='ghd-logo.jpg') }}"> 
</div>
<table>
<tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr>
<tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr>
<tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr>
<tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr><tr></tr>
<tr><td><h4>Select Site</h4></td></tr>
<tr><td>
<form method="post">
  <input list="Sites" name="site">
  <datalist id="Sites">
  <REPLACE_OPTIONS_HERE>    
  </datalist>
  <input type="submit">
</form>
</td></tr>
<table>
<div id='SIte Details'>
<!-- This is a comment -->
<div>
<div id="HOME"> 
<form method="post">
<input type="submit" value="HOME" name="home"/>
</form>
</div>
</html>
'''
#<option value="Safari">


def create_phase_1_page(df):
    options =  [str(s1)+'_'+s2 for s1,s2 in list(zip(df['Site Id'],df['file_name']))]
    rstring = '\n'.join(['<option value="{}">'.format(op) for op in options])
    rendered_page = dummy_html_template.replace('<REPLACE_OPTIONS_HERE>',rstring)
    return rendered_page
    
def create_tagger_page(di):
    options =  list(di.keys())
    rstring = '\n'.join(['<option value="{}">'.format(op) for op in options])
    rendered_page = dummy_html_template.replace('<REPLACE_OPTIONS_HERE>',rstring)
    return rendered_page
  
def create_imgtag_page(di):
    options =  list(di.keys())
    rstring = '\n'.join(['<option value="{}">'.format(op) for op in options])
    rendered_page = dummy_html_template.replace('<REPLACE_OPTIONS_HERE>',rstring)
    return rendered_page

def create_topics_page(di):
    options =  list(di.keys())
    rstring = '\n'.join(['<option value="{}">'.format(op) for op in options])
    rendered_page = dummy_html_template.replace('<REPLACE_OPTIONS_HERE>',rstring)
    return rendered_page



def create_blogs_page(di):
    options =  list(di.keys())
    rstring = '\n'.join(['<option value="{}">'.format(op) for op in options])
    rendered_page = dummy_html_template.replace('<REPLACE_OPTIONS_HERE>',rstring)
    return rendered_page