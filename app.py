import os
import pickle
import numpy as np
import pandas as pd
from flask import Flask, redirect, request, render_template

app = Flask(__name__)

model = pickle.load(open("model.pkl", "rb"))

def predicts(file):
  model = pickle.load(open("model.pkl", "rb"))
  df = pd.read_csv(file)
  df.drop(['id', 'attack_cat'], axis=1, inplace=True)
  df['proto'] = df.proto.where(df.proto.isin(['tcp', 'udp', 'unas']), 'lain')
  df['service'] = df.service.where(df.service.isin(['-', 'dns', 'http']), 'lain')
  df['state'] = df.state.where(df.state.isin(['FIN', 'INT', 'CON']), 'lain')
  df['proto'] = df.proto.map(lambda x: ['lain', 'tcp', 'udp', 'unas'].index(x))
  df['service'] = df.service.map(lambda x: ['-', 'dns', 'http', 'lain'].index(x))
  df['state'] = df.state.map(lambda x: ['CON', 'FIN', 'INT', 'lain'].index(x))

  X = df.values
  predictions = model.predict(X)
  return predictions

@app.route("/")
def home():
  return render_template("index.html")

@app.route("/predict", methods=["GET", "POST"])
def predict():
  if request.method == 'POST':
    file = request.files.get('file')
    file.save(os.path.join('files', file.filename))
    prediction = predicts(os.path.join('files', file.filename))
    return render_template("index.html", predictions=prediction)
  else:
    return redirect('/')

@app.before_request
def before_request():
  if '127.0.0.1' in request.host_url or '0.0.0.0' in request.host_url:
    app.jinja_env.cache = {}

if __name__ == "__main__":
  app.jinja_env.auto_reload = True
  app.config['TEMPLATES_AUTO_RELOAD'] = True
  app.run(debug=True)
