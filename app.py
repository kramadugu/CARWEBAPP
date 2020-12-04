# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 10:34:30 2020

@author: karthik.ramadugu
"""
#=========Importing Libraries========#
import os
import pickle
from shutil import make_archive
import time
import matplotlib.pyplot as  plt
from flask import Flask,request,render_template,redirect,url_for,render_template_string,flash,send_file
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup
import pandas as pd
#from sklearn.datasets import load_iris
from PDF_IMAGE_EXTRACTOR import *
from auxmethods import *
from summarizer import *
from tagger import *

#====================================#
phase_1 = pd.read_csv('static/df_all_features_v01.csv')

ttags = None
with open('tabble_tags.pkl','rb') as f:
    ttags = pickle.load(f)

ttags = {k+'_'+i:j for k,v in ttags.items() for i,j in v.items()}

topics = None
with open('topicmodels.pkl','rb') as f:
    topics = pickle.load(f)

boring_logs = {"T0600101493":("T0600101493.PDF",pd.read_csv("files/output csv along with pdf/Template 1/df3.csv").drop_duplicates()),"T0609500432_27":("WELL REPLACEMENT REPORT - T0609500432_27.pdf",pd.read_csv("files/output csv along with pdf/Template 2/df3.csv").drop_duplicates()),"T0609500432_30":("WELL REPLACEMENT REPORT - T0609500432_30.pdf",pd.read_csv("files/output csv along with pdf/Template 2/df4.csv").drop_duplicates())}
imtags = dict([(k.split('.')[0],pd.read_csv(os.path.join('files/IMTAGS',k))) for k in os.listdir('files/IMTAGS')])


UPLOAD_FOLDER = 'Uploads'
ALLOWED_EXTENSIONS = {'txt', 'xml'}
ALLOWED_EXTENSIONS_TAB = {'pdf'}
#==========Creating Flask App Object=======#
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#==========================================#

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_file_tabulas(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_TAB

#======Defining Access Methods==============#
@app.route('/',methods=['GET','POST'])
def get_submit():
    if request.method == 'GET':
        #[os.remove(os.path.join(UPLOAD_FOLDER,k)) for k in os.listdir(UPLOAD_FOLDER)]
        return render_template('index.html')
    elif request.method =='POST':
        #print(request.form)
        print(list(request.form.keys()))
        if 'p1esa' in list(request.form.keys()):
            return redirect(url_for('get_phase_1'))
        if 'home' in list(request.form.keys()):
            return redirect(url_for('get_submit'))
        elif 'docparser' in list(request.form.keys()):
            return redirect(url_for('get_doc_parser'))
        
@app.route('/docparser',methods=['GET','POST'])
def get_doc_parser():
    if request.method == 'GET':
        return render_template('Dparser.html')
    if request.method == 'POST':
        if 'summary' in list(request.form.keys()):
            return redirect(url_for('summar'))
        if 'topic' in list(request.form.keys()):
            return redirect(url_for('tmodel'))
        if 'home' in list(request.form.keys()):
            return redirect(url_for('get_submit'))
        if 'toc' in list(request.form.keys()):
            return redirect(url_for('TOC'))
        if 'imext' in list(request.form.keys()):
            return redirect(url_for('download_Images'))
        if 'imtag' in list(request.form.keys()):
            return redirect(url_for('imtagger'))
        if 'blog' in list(request.form.keys()):
            return redirect(url_for('get_boring_logs'))
        
        if 'tabletag' in list(request.form.keys()):
            return redirect(url_for('tblindex'))

@app.route('/imtag',methods=['GET','POST'])
def imtagger():
    if request.method == 'GET':
        page = create_imgtag_page(imtags)
        with open('templates/imtag.html',mode='w') as f:
            f.write(page)
        if os.path.exists('templates/imtag.html'):
            return render_template('imtag.html')
    if request.method == 'POST':
        if 'home' in list(request.form.keys()):
            return redirect(url_for('get_submit'))
        site = list(request.form.values())[0]
        df = imtags[site]
        page = None
        with open('templates/imtag.html','r') as f:
            page = f.read()
        page = page.replace('<!-- This is a comment -->',df.to_html())
        
        return render_template_string(page)
    

@app.route('/blogs',methods=['GET','POST'])
def get_boring_logs():
    if request.method == 'GET':
        page = create_blogs_page(boring_logs)
        with open('templates/blogs.html',mode='w') as f:
            f.write(page)
        if os.path.exists('templates/blogs.html'):
            return render_template('blogs.html')
    if request.method == 'POST':
        if 'home' in list(request.form.keys()):
            return redirect(url_for('get_submit'))
        site = list(request.form.values())[0]
        fpath,df = boring_logs[site]
        st = "{{ url_for('static', filename="+"'{}'".format(fpath)+")}}"
        print(st)
        padd = '''<table>
        <tr><td>
        <embed src= {} width= "500" height= "500">
        </td></tr>
        </table>'''.format(st)
        padd = df.to_html()+'\n'+padd
        page = None
        with open('templates/blogs.html','r') as f:
            page = f.read()
        page = page.replace('<!-- This is a comment -->',padd)
        return render_template_string(page)
        
@app.route('/imext',methods=['GET','POST'])
def download_Images():
    if request.method == 'GET':
        return render_template_string(tagger_html)
    if request.method == 'POST':
        # check if the post request has the file part
        if 'home' in list(request.form.keys()):
            return redirect(url_for('get_submit'))
        
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file_tabulas(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            IMGS = extract_images(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            rpath = os.path.join(app.config['UPLOAD_FOLDER'], filename.split('.')[0])
            os.mkdir(rpath)
            [plt.imsave(os.path.join(rpath,'IMG_{}.jpg'.format(i+1)),IM) for i,IM in enumerate(IMGS)]
            make_archive(os.path.join(UPLOAD_FOLDER,filename.split('.')[0]),'zip',rpath)
            while(True):
                if os.path.exists(os.path.join(UPLOAD_FOLDER,filename.split('.')[0]+'.zip')):
                    break
                else:
                    time.sleep(0.5)
                    
            return send_file(os.path.join(UPLOAD_FOLDER,filename.split('.')[0]+'.zip'),as_attachment=True)
            
            
            #tblindex = readtables(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #rpage = tagger_html.replace('<!-- This is a comment -->',tblindex.to_html(index=False))
            #return render_template_string(rpage)
    
    

@app.route('/tableindex',methods=['GET','POST'])
def tblindex():
    if request.method == 'GET':
        page = create_tagger_page(ttags)
        with open('templates/ttag.html',mode='w') as f:
            f.write(page)
        if os.path.exists('templates/ttag.html'):
            return render_template('ttag.html')
    if request.method == 'POST':
        if 'home' in list(request.form.keys()):
            return redirect(url_for('get_submit'))
        site = list(request.form.values())[0]
        df = ttags[site]
        page = None
        with open('templates/ttag.html','r') as f:
            page = f.read()
        page = page.replace('<!-- This is a comment -->',df.to_html())
        
        return render_template_string(page)



@app.route('/toc',methods=['GET','POST'])
def TOC():
    if request.method == 'GET':
        return render_template_string(tagger_html)
    if request.method == 'POST':
        # check if the post request has the file part
        if 'home' in list(request.form.keys()):
            return redirect(url_for('get_submit'))
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file_tabulas(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            tocs = get_TOC(os.path.join(app.config['UPLOAD_FOLDER'], filename))[0]
            rpage = tagger_html.replace('<!-- This is a comment -->',tocs.to_html(index=False))
            return render_template_string(rpage)
    
    
        

@app.route('/topicmodel',methods=['GET','POST'])
def tmodel():
    if request.method == 'GET':
        page = create_topics_page(topics)
        with open('templates/topics.html',mode='w') as f:
            f.write(page)
        if os.path.exists('templates/topics.html'):
            return render_template('topics.html')
    
    if request.method == 'POST':
        if 'home' in list(request.form.keys()):
            return redirect(url_for('get_submit'))
        site = list(request.form.values())[0]
        df = topics[site]
        page = None
        with open('templates/topics.html','r') as f:
            page = f.read()
        page = page.replace('<!-- This is a comment -->',df.to_html())
        
        return render_template_string(page)
            
            
    
    

@app.route('/summarizer',methods=['GET','POST'])
def summar():
    if request.method == 'GET':
        return render_template('Summarizer.html')
        
    if request.method == 'POST':
        # check if the post request has the file part
        if 'home' in list(request.form.keys()):
            return redirect(url_for('get_submit'))
        nsents = int(request.form['quantity'])
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            summary = None
            st = None
            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename),'r',encoding='latin-1') as f:
                st = f.read()
            if filename.endswith('txt'):
                summary = generate_summary(st,nsents)
            if filename.endswith('xml'):
                summary = generate_summary(BeautifulSoup(st,'xml').get_text(),nsents)
            print(summary)
            return render_template('Summarizer.html',summary=summary)
        
    
    
    

@app.route('/p1parser',methods=['GET','POST'])
def get_phase_1():
    if request.method == 'GET':
        page = create_phase_1_page(phase_1)
        with open('templates/Phase1.html',mode='w') as f:
            f.write(page)
        if os.path.exists('templates/Phase1.html'):
            return render_template('Phase1.html')
        else:
            return redirect(url_for('get_submit'))
    if request.method == 'POST':
        if 'home' in list(request.form.keys()):
            return redirect(url_for('get_submit'))
        site = list(request.form.values())[0]
        sid = int(site.split('_')[0])
        rdf = phase_1[phase_1['Site Id']==sid].T.to_html()
        base_html = None
        with open('templates/Phase1.html','r') as f:
            base_html = f.read()
        base_html = base_html.replace('<!-- This is a comment -->',rdf)
        
        return render_template_string(base_html)
        
    
if __name__=='__main__':
    app.run()
    
    
