import pandas as pd
import pandas_datareader.data as web
from pandas._config.config import reset_option
import numpy as np

import datetime as dt

import requests as r
from bs4 import BeautifulSoup

import altair as alt

from IPython.core.display import HTML

import streamlit as st

####App
def main():
    """ ETF Sparplan """
    ##General Settings
    st.set_page_config(page_title='CLUE - ETF Sparplan Rechner', page_icon='logo.jpg')
    
    ## Hide Hamburger Menu
    hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

    st.success('ETF Sparplan Rechner')

###Eingabe
    input  = pd.read_excel('ETF.xlsx')
    input = input.set_index('ETF')
    df_etf = pd.DataFrame(input)           
    list = st.selectbox('Wähle deinen ETF:', df_etf.index)
    entry = df_etf['RIC']
    entry_list = entry[list]
    inf = df_etf['Branche/Region']

###Col Defintion    
    col0_1, col0_2 = st.beta_columns(2)
    col1, col2 = st.beta_columns(2)
    col2_1, col2_2 = st.beta_columns([3,1])
    
    with col0_1:
        st.info(inf[list])
    
    with col0_2:
        url = 'https://de.finance.yahoo.com/quote/' + entry_list + '?p=' + entry_list
        req = r.get(url)
        soup = BeautifulSoup(req.content, 'html.parser')
        try:
            cont_Kostenquote = soup.body.div.find('span', {'data-reactid': '115'}).text.replace(',', '.') #netto
            cont_Nettoverm = soup.body.div.find('span', {'data-reactid': '85'}).text.replace(',', '.')
            
            try:
                size = pd.DataFrame([], columns=['Volumen'], index=[0])
                size['Volumen'] = cont_Nettoverm
                size = size['Volumen'].str.replace('M', '')
                test = size.astype(float) * 1
                vol = test[0].astype(str) + ' Mio. EUR'
            except:
                try:
                    size = pd.DataFrame([], columns=['Volumen'], index=[0])
                    size['Volumen'] = cont_Nettoverm
                    size = size['Volumen'].str.replace('B', '')
                    test = size.astype(float) * 1
                    vol = test[0].astype(str) + ' Mrd. EUR'
                except:
                    vol = 'N/A'
            
            st.success('Nettovermögen d. Fonds: ' + vol)
            st.error('Netto Kostenquote (TER) p.a.: ' + cont_Kostenquote)
        except:
            try:
                cont_Kostenquote = soup.body.div.find('span', {'data-reactid': '113'}).text.replace(',', '.') #netto
                cont_Nettoverm = soup.body.div.find('span', {'data-reactid': '83'}).text.replace(',', '.')
                            
                try:
                    size = pd.DataFrame([], columns=['Volumen'], index=[0])
                    size['Volumen'] = cont_Nettoverm
                    size = size['Volumen'].str.replace('M', '')
                    test = size.astype(float) * 1
                    vol = test[0].astype(str) + ' Mio. EUR'
                except:
                    try:
                        size = pd.DataFrame([], columns=['Volumen'], index=[0])
                        size['Volumen'] = cont_Nettoverm
                        size = size['Volumen'].str.replace('B', '')
                        test = size.astype(float) * 1
                        vol = test[0].astype(str) + ' Mrd. EUR'
                    except:
                        vol = 'N/A'

                st.success('Nettovermögen d. Fonds: ' + vol)
                st.error('Netto Kostenquote (TER) p.a.: ' + cont_Kostenquote)
            except:
                cont_Kostenquote = soup.body.div.find('span', {'data-reactid': '111'}).text.replace(',', '.') #netto
                cont_Nettoverm = soup.body.div.find('span', {'data-reactid': '81'}).text.replace(',', '.')
                
                try:
                    size = pd.DataFrame([], columns=['Volumen'], index=[0])
                    size['Volumen'] = cont_Nettoverm
                    size = size['Volumen'].str.replace('M', '')
                    test = size.astype(float) * 1
                    vol = test[0].astype(str) + ' Mio. EUR'
                except:
                    try:
                        size = pd.DataFrame([], columns=['Volumen'], index=[0])
                        size['Volumen'] = cont_Nettoverm
                        size = size['Volumen'].str.replace('B', '')
                        test = size.astype(float) * 1
                        vol = test[0].astype(str) + ' Mrd. EUR'
                    except:
                        vol = 'N/A'

                st.success('Nettovermögen d. Fonds: ' + vol)
                st.error('Netto Kostenquote (TER) p.a.: ' + cont_Kostenquote)

    with col1:
        entry_money = st.number_input('Wie viel willst du pro Monat einzahlen?', min_value=(25), max_value=(1500), value=(500))
        
        start = st.date_input('Anfangsdatum', dt.datetime(2010, 1, 1), min_value=dt.datetime(2010, 1, 1), max_value=dt.datetime(2019, 1, 1))
        end = dt.datetime.now()
 
    @st.cache
    def key_data(key_data):
        data = web.DataReader(entry_list, 'yahoo', start, end)
        ###Basis zu relevanten Zeitwerten
        df = pd.DataFrame(data).reset_index()
        df = df[['Date', 'Close', 'Volume']]
        ##Extract year, month and day of Date
        df['year'] = df['Date'].dt.year
        df['month'] = df['Date'].dt.month
        df['day'] = df['Date'].dt.day
        ##Get max of each month
        df_time = pd.DataFrame(df.groupby(['year', 'month'])['day'].max()).reset_index()
        #Merge year, month and day of max
        df_time['Date'] = df_time['year'].astype(str) + '-' + df_time['month'].astype(str) + '-' + df_time['day'].astype(str)
        #convert to datetime
        df_time['Date'] = pd.to_datetime(df_time['Date'])
        #drop not needed columns
        df_time = df_time.drop(columns=['year', 'month', 'day'])
        ##merge oroginal df and needed timeseries df
        out = pd.merge(df, df_time, left_on='Date', right_on='Date').drop(columns=['year', 'month', 'day'])
        out['Close'] = round(out['Close'] ,2)

        ###Grundlage für Grafik
        df_out = pd.DataFrame(out).reset_index()
        df_out['index'] += 1
        df_out['Stueckzahl kum.'] = round(entry_money / df_out['Close'], 2).cumsum()
        df_out['Wertentwicklung Sparplan in EUR'] = round(df_out['Stueckzahl kum.'] * df_out['Close'], 2)
        df_out['Investiert in EUR'] = entry_money * df_out['index']
        df_out['Performance in %'] = round((df_out['Wertentwicklung Sparplan in EUR'] / df_out['Investiert in EUR'] -1) * 100, 2)
        df_out['max Kurs'] = df_out['Close'].cummax()
        df_out['Differenz zu max Kurs'] = round(((df_out['Close'] - df_out['max Kurs']) / df_out['max Kurs']) * 100, 2)
        df_out = df_out.rename(columns={'Date': 'Datum', 'Close': 'Tageschlusskurs', 'Volume': 'Handelsvolumen'})
        return df_out
    
    df_out = key_data(key_data)

###Zusatzinfo zu Produkt und Grafik
    with col2:
        count = df_out.index.max()
        perf_pyear = round(df_out['Performance in %'][count] / df_out['index'].max() * 12, 2).astype(str)
        max_drawdown = df_out['Differenz zu max Kurs'].min().astype(str)
        st.success('Durchschnittlich Performance pro Jahr seit Anfangsdatum: ' + perf_pyear + '%')
        st.error('max. Drawdown seit Anfangsdatum: ' + max_drawdown + '%')

###Grafik Historisch
    with col2_1:
        option = st.selectbox('Wertentwicklung anzeigen als: Zukünftig oder historisch und grafisch oder als Tabelle?', ('Zukünftig mit Grafik', 'Zukünftig mit Tabelle', 'Historisch mit Grafik', 'Historisch mit Tabelle'))
        breit = 500
        hoch = 450

        if option == 'Historisch mit Grafik':
            chart_plan = alt.Chart(df_out).mark_trail(point=True, clip=True, opacity=0.8).encode(
                alt.X('Datum',
                    #scale=alt.Scale(domain=(df_hist['Datum'].astype(int).min() -1, df_hist['Datum'].astype(int).max() + 1)),
                    title='Datum'),
                alt.Y('Wertentwicklung Sparplan in EUR',
                    scale=alt.Scale(domain=(df_out['Wertentwicklung Sparplan in EUR'].min() -1, df_out['Wertentwicklung Sparplan in EUR'].max() + 1)),
                    title='Wertentwicklung Sparplan in EUR'),
                tooltip=['Datum', 'Wertentwicklung Sparplan in EUR', 'Performance in %', 'Investiert in EUR'],
                size=alt.Size('Wertentwicklung Sparplan in EUR', scale=alt.Scale(range=[1, 4, 10]), legend=None),
            ).interactive().properties(
                width=breit,
                height=hoch
            )

            chart_invest = alt.Chart(df_out).mark_trail(point=True, clip=True, color='yellow', opacity=0.8).encode(
                alt.X('Datum',
                    title='Datum'),
                alt.Y('Investiert in EUR',
                    title='Investiert in EUR'),
                tooltip=['Datum', 'Wertentwicklung Sparplan in EUR', 'Performance in %', 'Investiert in EUR'],
                size=alt.Size('Investiert in EUR', scale=alt.Scale(range=[1, 4, 10]), legend=None),
            ).interactive()

            chart = chart_plan + chart_invest
            st.altair_chart(chart)
        elif option == 'Zukünftig mit Grafik':
            Laufzeit = st.number_input('Wie viele Jahre planst du zu investieren?', min_value=5, max_value=50, value=10)

            df_fut = pd.DataFrame([], columns=['Sparbetrag', 'Wertentwicklung', 'Zinsertrag (brutto)'], index=range(Laufzeit*12)).reset_index().rename(columns={'index': 'Monat'})
            df_fut['Monat'] = df_fut.index + 1 
            df_fut['Sparbetrag'] = (entry_money * df_fut['Monat'])
            perf_year = round(df_out['Performance in %'][count] / df_out['index'].max() * 12, 2)
            df_fut['Wertentwicklung'] = -1 * np.fv(perf_year/100/12, df_fut['Monat'], entry_money, 0, when=1)
            df_fut['Zinsertrag (brutto)'] = df_fut['Wertentwicklung'] - df_fut['Sparbetrag']
            df_fut['Wertentwicklung'] = round(df_fut['Wertentwicklung'] *1, 2)
            df_fut['Zinsertrag (brutto)'] = round(df_fut['Zinsertrag (brutto)'] *1, 2)
        
###Grafik Zukunft
            chart_fut = alt.Chart(df_fut).mark_trail(point=True, clip=True, opacity=0.8).encode(
                alt.X('Monat',
                    #scale=alt.Scale(domain=(df_hist['Datum'].astype(int).min() -1, df_hist['Datum'].astype(int).max() + 1)),
                    title='Monat'),
                alt.Y('Wertentwicklung',
                    scale=alt.Scale(domain=(df_fut['Wertentwicklung'].min() -1, df_fut['Wertentwicklung'].max() + 1)),
                    title='Wertentwicklung Sparplan in EUR'),
                tooltip=['Monat', 'Wertentwicklung', 'Sparbetrag', 'Zinsertrag (brutto)'],
                size=alt.Size('Wertentwicklung', scale=alt.Scale(range=[1, 4, 10]), legend=None),
            ).interactive().properties(
                width=breit,
                height=hoch
            )

            chart_spar = alt.Chart(df_fut).mark_trail(point=True, clip=True, color='yellow', opacity=0.8).encode(
                alt.X('Monat',
                    title='Monat'),
                alt.Y('Sparbetrag'),
                tooltip=['Monat', 'Wertentwicklung', 'Sparbetrag', 'Zinsertrag (brutto)'],
                size=alt.Size('Sparbetrag', scale=alt.Scale(range=[1, 4, 10]), legend=None),
            ).interactive().properties(
                width=breit,
                height=hoch
            )

            chart = chart_fut + chart_spar
            chart

###Tabelle historisch        
        elif option == 'Historisch mit Tabelle':
            df_out = df_out[['Datum', 'Investiert in EUR', 'Wertentwicklung Sparplan in EUR', 'Performance in %']].rename(columns={'Investiert in EUR': 'Sparbetrag in EUR', 'Wertentwicklung Sparplan in EUR': 'Wertentwicklung in EUR'})
            df_outhtml = df_out.to_html(escape=False, index=False)
            st.markdown(df_outhtml, unsafe_allow_html=True)
            

###Tabelle zukünftig       
        else:
            Laufzeit = st.number_input('Wie viele Jahre planst du zu investieren?', min_value=5, max_value=50, value=10)

            df_fut = pd.DataFrame([], columns=['Sparbetrag in EUR', 'Wertentwicklung in EUR', 'Zinsertrag in EUR'], index=range(Laufzeit*12)).reset_index().rename(columns={'index': 'Monat'})
            df_fut['Monat'] = df_fut.index + 1 
            df_fut['Sparbetrag in EUR'] = (entry_money * df_fut['Monat'])
            perf_year = round(df_out['Performance in %'][count] / df_out['index'].max() * 12, 2)
            df_fut['Wertentwicklung in EUR'] = -1 * np.fv(perf_year/100/12, df_fut['Monat'], entry_money, 0, when=1)
            df_fut['Zinsertrag in EUR'] = df_fut['Wertentwicklung in EUR'] - df_fut['Sparbetrag in EUR']
            df_fut['Wertentwicklung in EUR'] = round(df_fut['Wertentwicklung in EUR'] *1, 2)
            df_fut['Zinsertrag in EUR'] = round(df_fut['Zinsertrag in EUR'] *1, 2)
            df_futhtml = df_fut.to_html(escape=False, index=False)
            st.markdown(df_futhtml, unsafe_allow_html=True)

###Werbung
    with col2_2:
        st.text_area('', 'Diesen Broker nutze ich - nur zu empfehlen:')
        url_neu = 'https://financeads.net/tc.php?t=40489C274463070B'    
        link = pd.DataFrame(['<a href="' +url_neu+ '" target="_blank"><img src="https://www.clever-und-erfolgreich.de/wp-content/uploads/etf/trade_republic.png" width="145" ></a>'], columns=[''])
        html = link.to_html(escape=False, index=False)   
        st.markdown(html, unsafe_allow_html=True)

###Sector Info
    ##Create Expander
    my_expander = st.beta_expander("Weitere Infos: Sektorgewichtung", expanded=False)
    with my_expander:
        @st.cache
        def key_sector(key_sector):
            url_sec = 'https://de.finance.yahoo.com/quote/' + entry_list + '/holdings?p=' + entry_list
            req_sec = r.get(url_sec)
            dat_sec = BeautifulSoup(req_sec.content, 'html.parser')
            cont_sec = dat_sec.body('div', {'class': 'Mb(25px)'})
            df_sec = pd.DataFrame(cont_sec[1])
            sec = df_sec[0].astype(str).str.split('</span>').to_list()
            df_sec2 = pd.DataFrame(sec).dropna().transpose()
            sec2 = df_sec2[1].astype(str).str.split('">').to_list()
            df_sec3 = pd.DataFrame(sec2)
            sec_industry = df_sec3[4][1:].dropna().reset_index().drop(columns=['index'])
            sec_percent = df_sec3[1].str.replace(',', '.').str.replace('%', '').apply(pd.to_numeric, errors='coerce').dropna().reset_index().drop(columns=['index'])
            df_merge = pd.merge(sec_industry, sec_percent, left_index=True, right_index=True).rename(columns={4: 'Sektor', 1: 'Gewichtung in %'}).sort_values(by=['Gewichtung in %'], ascending=False).reset_index().drop(columns=['index'])
            return df_merge
        df_merge = key_sector(key_sector)

        table = pd.DataFrame(df_merge).style.set_precision(2)
        st.table(table)
    
if __name__ == '__main__':
    main()