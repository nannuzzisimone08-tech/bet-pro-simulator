import os, json, random
from flask import Flask, render_template, jsonify, request
from datetime import datetime
import os


base_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, template_folder=os.path.join(base_dir, 'templates'))

FILE_DATI = os.path.join(base_dir, "dati_gioco.json")

SQUADRE = {
    "SERIE A": ["Inter","Milan","Juventus","Napoli","Roma","Lazio","Atalanta","Fiorentina","Bologna","Torino","Monza","Udinese"],
    "PREMIER LEAGUE": ["Man City","Arsenal","Liverpool","Chelsea","Man Utd","Tottenham","Newcastle","Aston Villa","Everton","Fulham","West Ham","Brighton"],
    "LALIGA": ["Real Madrid","Barcellona","Atletico Madrid","Siviglia","Villarreal","Real Sociedad","Betis","Valencia","Getafe","Osasuna","Girona","Alaves"],
    "CHAMPIONS LEAGUE": ["Bayern","PSG","Real Madrid","Man City","Inter","Dortmund","Barcellona","Arsenal","Porto","Benfica","Napoli","Lipsia"]
}

def carica_dati():
    if os.path.exists(FILE_DATI):
        try:
            with open(FILE_DATI) as f:
                return json.load(f)
        except:
            pass
    return {
        "saldo": 1000,
        "giocate": [],
        "movimenti": []
    }

def salva_dati(d):
    with open(FILE_DATI,"w") as f:
        json.dump(d,f,indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_dati')
def get_dati():
    return jsonify(carica_dati())

@app.route('/get_palinsesto')
def get_palinsesto():
    out={}
    for c,s in SQUADRE.items():
        random.shuffle(s)
        partite=[]
        for i in range(0,12,2):
            casa=s[i]
            fuori=s[i+1]

            partite.append({
                "casa":casa,
                "fuori":fuori,
                "esiti":{
                    "1":round(random.uniform(1.5,3),2),
                    "X":round(random.uniform(2.5,4),2),
                    "2":round(random.uniform(1.8,4),2),

                    "GG":round(random.uniform(1.4,2.2),2),
                    "NG":round(random.uniform(1.4,2.2),2),

                    # UNDER / OVER fino a 4.5
                    "U1.5":round(random.uniform(1.6,2.2),2),
                    "O1.5":round(random.uniform(1.4,1.9),2),

                    "U2.5":round(random.uniform(1.6,2.2),2),
                    "O2.5":round(random.uniform(1.4,2.0),2),

                    "U3.5":round(random.uniform(1.4,2.0),2),
                    "O3.5":round(random.uniform(1.6,2.6),2),

                    "U4.5":round(random.uniform(1.2,1.8),2),
                    "O4.5":round(random.uniform(1.8,3.5),2),

                    # RISULTATI ESATTI (max somma gol = 6)
                    "CS":{
                        "1":{
                            "1-0":7,"2-0":9,"2-1":8,"3-0":10,"3-1":11,"4-0":14,"4-1":13,"5-0":18
                        },
                        "X":{
                            "0-0":10,"1-1":6,"2-2":12,"3-3":18
                        },
                        "2":{
                            "0-1":8,"0-2":11,"1-2":9,"0-3":12,"1-3":14,"0-4":18,"1-4":20
                        }
                    }
                }
            })
        out[c]=partite
    return jsonify(out)

@app.route('/scommetti',methods=['POST'])
def scommetti():
    d=carica_dati()
    r=request.get_json()

    imp=float(r["importo"])
    q=float(r["quota"])

    if imp>d["saldo"]:
        return jsonify({"error":"saldo"}),400

    win=random.random()<(1/q)

    d["saldo"]-=imp
    profitto = 0

    if win:
        profitto = imp*q
        d["saldo"]+=profitto

    d["saldo"]=round(d["saldo"],2)

    # storico
    d["giocate"].insert(0,{
        "evento":r["evento"],
        "scelta":r["scelta"],
        "importo":imp,
        "quota":q,
        "risultato":"VINTO" if win else "PERSO"
    })

    # MOVIMENTI PER GRAFICO
    d["movimenti"].append({
        "time":datetime.now().strftime("%H:%M:%S"),
        "delta": profitto-imp
    })

    salva_dati(d)
    return jsonify({"risultato":"VINTO" if win else "PERSO"})

port = int(os.environ.get("PORT", 5000))
app.run(host='0.0.0.0', port=port)

if __name__=="__main__":
    app.run(debug=True)