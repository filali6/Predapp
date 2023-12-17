from flask import Flask, render_template,request,redirect,url_for,flash , jsonify,session
from pymongo import MongoClient
from flask_cors import CORS
import pickle
import numpy as np
import pandas as pd 
import json


backend=Flask(__name__)#creation d'une instance de l'application web flask 
#tawa bech nconeectiw maa el mongodb 
CORS(backend)
backend.secret_key = 'your-secret-key'
client=MongoClient("localhost",27017)
db=client['BD_app']
col=db['users']
pred=db['predictions']
model=pickle.load(open('model.pkl','rb'))

@backend.route('/')
def index():
    if 'username' in session:
        return render_template("frontcon.html")
    return render_template("front.html")
@backend.route('/about')
def about():
    if 'username' in session:
        return render_template("aboutcon.html")
    return render_template("aboutfront.html")

@backend.route('/register',methods=['POST','GET'])
def inscri():
    if 'username' in session:
            return redirect(url_for('index'))
    if request.method=='POST':
        
    
        nom=request.form['nom']
        prenom=request.form['prenom']
        username=request.form['username']
        password=request.form['password']
        confirm_password=request.form['confirm_password']
        user_data=col.find_one({'username':username})
        if user_data:
            error_message="utilisateur existant"
            return render_template('registerfront.html',error=error_message)
        if password==confirm_password:
            
            user_data={
                'nom':nom,
                'prenom':prenom,
                'username':username,
                'password':password
            }
            col.insert_one(user_data)
            return redirect(url_for("connexion"))
        else:
            error_message="les mots de passe ne correspondent pas."
            return render_template('registerfront.html',error=error_message)
    return render_template('registerfront.html',error="")
 
    
@backend.route('/connexion',methods=['POST','GET'])
def connexion(): 
    if 'username' in session:
            return redirect(url_for('index'))
    msg=''
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        
        user_data=col.find_one({'username':username,'password':password})
        
        if user_data:
            session['username'] = username
            return redirect(url_for("index"))
        else:
            msg = 'utilisateur introuvable'
            
    return render_template('connexionfront.html', msg = msg)
@backend.route('/prediction',methods=['POST','GET'])
def prediction():
    if not 'username' in session:
            return redirect(url_for('connexion'))
    if request.method=='POST':
        entreprise=request.json['entreprise']
        capprop=float(request.json['capprop'])
        tot_bl=float(request.json['totbl'])
        liq=float(request.json['liq'])
        pass_courant=float(request.json['pc'])
        fr=float(request.json['fr'])
        bfr=float(request.json['bfr'])
        ca=float(request.json['ca'])
        rn=float(request.json['rn'])
        act_courant=float(request.json['ac'])
        ds=float(request.json['ds'])
        cfn=float(request.json['cfn'])
        fpn=float(request.json['fpn'])
        
        #--- calculer ratios
        try:
            sol=capprop/tot_bl
        except ZeroDivisionError:
            sol = np.nan
            
        try:
            liq_im=liq/pass_courant
        except ZeroDivisionError:
            liq_im = np.nan
            
        try:
            eq=fr/bfr
        except ZeroDivisionError:
            eq = np.nan
            
        try:
            rot_cap_prop=ca/capprop
        except ZeroDivisionError:
            rot_cap_prop = np.nan
            
        try:
            roe=rn/capprop
        except ZeroDivisionError:
            roe = np.nan
            
        try:
            rot_act=ca/tot_bl
        except ZeroDivisionError:
            rot_act = np.nan
            
        try:
            marge_net=rn/ca
        except ZeroDivisionError:
            marge_net = np.nan
            
        try:
            liq_cour=act_courant/pass_courant
        except ZeroDivisionError:
            liq_cour = np.nan
            
        try:
            aut_fin=capprop/(capprop+ds)
        except ZeroDivisionError:
            aut_fin = np.nan
            
        try:
            couv=ds/cfn
        except ZeroDivisionError:
            couv = np.nan
            
        try:
            lev=pass_courant/capprop
        except ZeroDivisionError:
            lev = np.nan
            
        try:
            end=ds/fpn
        except ZeroDivisionError:
            end = np.nan
            
        q=pd.DataFrame({'solvabilite':[sol], 'liq_immediate':[liq_im], 'equilibire':[eq], 'rot_cap_prop':[rot_cap_prop], 'roe':[roe],
        'rot_actif':[rot_act], 'marge_net':[marge_net], 'liq_cour':[liq_cour], 'aut_fin':[aut_fin], 'couv_det':[couv],
        'leverage_financier':[lev], 'endettement':[10]})
        res=int(model.predict(q)[0])
        #res=1
        pred.insert_one({"entreprise":entreprise,"defaut":res})
        return jsonify({"res":res})
    return render_template("predfront.html")

#hedy bech trajaa les valeurs lel front
@backend.route('/historique')
def hist():
    if not 'username' in session:
            return redirect(url_for('connexion'))
    return render_template("historiquefront.html") 

@backend.route('/historique/data')
def history_data_encient():
    if not 'username' in session:
            return redirect(url_for('connexion'))
    predictions = list(db.predictions.find({}, {'entreprise':1,'defaut':1 ,'_id':0}).sort('_id',1))
    prediction_data_json = json.loads(json.dumps(predictions))
    return prediction_data_json

@backend.route('/logout')
def logout():
    if not 'username' in session:
            return redirect(url_for('connexion'))
    session.pop('username', None)
    return redirect(url_for('index'))
if __name__=='__main__':
    backend.run(debug=True)

 
            
        

    