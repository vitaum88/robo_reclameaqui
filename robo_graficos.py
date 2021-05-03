import pandas as pd
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import ticker
import datetime as dt
import seaborn as sns
import calendar
import locale
import argparse

locale.setlocale(locale.LC_TIME, "pt_BR");

plt.rcParams['figure.figsize'] = (10,3)
plt.rcParams.update({'font.size': 14})
sns.set_style('whitegrid')

def parsing_routine():
    parser = argparse.ArgumentParser()

    parser.add_argument('input_json')
    parser.add_argument('input_data')

    return parser.parse_args()

def grafico_diario(df, grupo):
    try:
        mes_corrente = df[df.data.dt.month == ONTEM.month]
        fig, ax = plt.subplots(figsize=(12,4))
        plot = mes_corrente.set_index('data').resample('D').link.count().plot(marker='o')
        plot.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

        plt.title('Total Diário de Reclamações - {} - {}'.format(str(ONTEM.strftime('%B')).title(), grupo))
        plt.xlabel('Dia')
        plt.ylabel('Quantidade')
        plt.xticks(range(DIA_BASE,DIA_BASE+RANGE_DIAS), range(1, RANGE_DIAS + 1))
        plt.ylim(bottom=0)
        plt.tight_layout()
        plt.savefig(grupo+'_'+dt.datetime.today().strftime('%d-%m-%Y')+'_diario.png')
        #plt.show()
    except:
        pass    


def grafico_mensal(df, grupo):
    fig, ax = plt.subplots(figsize=(12,4))
    mensal = df.set_index('data').resample('M').link.count()
    mensal.index = map(lambda x: x.strftime('%b-%y').title(), mensal.index)
    mensal.plot(ax=ax, marker='o')
    #ax.xaxis.set_ticklabels(mensal.index.to_period('M'))
    plt.title('Total Mensal de Reclamações - {}'.format(grupo))
    plt.ylabel('Quantidade')
    plt.xlabel('Mês-Ano')
    plt.ylim(bottom=0)
    plt.tight_layout()
    plt.savefig(grupo+'_'+dt.datetime.today().strftime('%d-%m-%Y')+'_acumulado.png')
    #plt.show()    


def grafico_empresas(df, grupo):
    fig, ax = plt.subplots(figsize=(10,8))
    agrupado = df.empresa.value_counts()
    agrupado.plot(kind='bar')
    plt.title('Total de Reclamações - Visão Unidades de Negócios - {}'.format(grupo))
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    plt.savefig(grupo+'_'+dt.datetime.today().strftime('%d-%m-%Y')+'_quebra por empresas.png')
    #plt.show()

args = parsing_routine()

ONTEM = dt.date.today()-dt.timedelta(days=1)
DIA_BASE = (dt.date(ONTEM.year, ONTEM.month, 1) - dt.date(1970, 1, 1)).days
RANGE_DIAS = calendar.monthrange(ONTEM.year, ONTEM.month)[1]


with open(args.input_json, encoding='utf-8') as f:
    dados = json.load(f)

empresas = [dados['dados'][i]['nome'] for i in range(1, len(dados['dados']))]
links = [[l[0] for l in dados['dados'][i]['link']] for i in range(1, len(dados['dados']))]

dic = dict(zip(empresas, links))

wb = pd.ExcelFile(args.input_data)


for grupo in dic:
    df = pd.DataFrame()
    for l in dic[grupo]:
        try:
            temp = pd.read_excel(wb, sheet_name=l)
            temp['data'] = pd.to_datetime(temp.data, format='%d/%m/%Y')
            temp['empresa'] = l
            df = df.append(temp)
        except:
            pass    
    df.drop_duplicates(subset=['link'], inplace=True)
    
    args = [df, grupo]
    grafico_diario(*args)
    grafico_mensal(*args)
    grafico_empresas(*args)

wb.close()
