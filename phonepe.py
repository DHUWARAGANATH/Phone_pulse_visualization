import streamlit as st
import pandas as pd
import pymysql
import plotly.express as px
import json
import requests

myconnection=pymysql.connect(host="*********",user="root",password="***********",database="phonepe")
cur=myconnection.cursor()

#Aggregated_transaction
cur.execute("select * from aggregated_transaction")
myconnection.commit()
table1 = cur.fetchall()
Aggre_transaction = pd.DataFrame(table1,columns = ("States", "Years", "Quarter", "Transaction_type", "Transaction_count", "Transaction_amount"))

#Aggregated_user
cur.execute("select * from aggregated_user")
myconnection.commit()
table2 = cur.fetchall()
Aggre_user = pd.DataFrame(table2,columns = ("States", "Years", "Quarter", "Brands", "Transaction_count", "Percentage"))

#Aggregated_insurance
cur.execute("select * from aggregated_insurance")
myconnection.commit()
table3 = cur.fetchall()
Aggre_insurance = pd.DataFrame(table3,columns = ("States", "Years", "Quarter", "Transaction_type", "Transaction_count","Transaction_amount"))


#Map_transaction
cur.execute("select * from map_transaction")
myconnection.commit()
table4 = cur.fetchall()
Map_transaction = pd.DataFrame(table4,columns = ("States", "Years", "Quarter", "Districts", "Transaction_count", "Transaction_amount"))
Map_transaction['Districts'] = Map_transaction['Districts'].str.replace(" district", "")
Map_transaction['Districts']=Map_transaction['Districts'].str.title()

#Map_user
cur.execute("select * from map_user")
myconnection.commit()
table5 = cur.fetchall()
Map_user = pd.DataFrame(table5,columns = ("States", "Years", "Quarter", "Districts", "RegisteredUser", "AppOpens"))
Map_user['Districts'] = Map_user['Districts'].str.replace(" district", "")
Map_user['Districts']=Map_user['Districts'].str.title()

#Map_insurance
cur.execute("select * from map_insurance")
myconnection.commit()
table6 = cur.fetchall()
Map_insurance = pd.DataFrame(table6,columns = ("States", "Years", "Quarter", "Districts", "Transaction_count","Transaction_amount"))
Map_insurance['Districts'] = Map_insurance['Districts'].str.replace(" district", "")
Map_insurance['Districts']=Map_insurance['Districts'].str.title()

#Top_transaction
cur.execute("select * from top_transaction")
myconnection.commit()
table7= cur.fetchall()
Top_transaction = pd.DataFrame(table7,columns = ("States", "Years", "Quarter", "Pincodes", "Transaction_count", "Transaction_amount"))
Top_transaction['Pincodes'] = Top_transaction['Pincodes'].astype(str).apply(lambda x: x.split('.')[0])


#Top_user
cur.execute("select * from top_user")
myconnection.commit()
table8 = cur.fetchall()
Top_user = pd.DataFrame(table8, columns = ("States", "Years", "Quarter", "Pincodes", "RegisteredUser"))
Top_user['Pincodes'] = Top_user['Pincodes'].astype(str).apply(lambda x: x.split('.')[0])

#Top_insurance
cur.execute("select * from top_insurance")
myconnection.commit()
table9 = cur.fetchall()
Top_insurance = pd.DataFrame(table9,columns = ("States", "Years", "Quarter", "Pincodes", "Transaction_count", "Transaction_amount"))
Top_insurance['Pincodes'] = Top_insurance['Pincodes'].astype(str).apply(lambda x: x.split('.')[0])


#Transaction information
#Total payment value
def aggre_transaction_totaltransactionamount(df,year,quarter):
    at= df[(df['Years']==year)&(df['Quarter']==quarter)]
    
    AT=at['Transaction_amount'].sum()
    return '₹'+'{:,.0f} Cr'.format(round(AT / 10000000))

#All PhonePe transactions (UPI + Cards + Wallets)
def aggre_transaction_totaltransactioncount(df,year,quarter):
    at= df[(df['Years']==year)&(df['Quarter']==quarter)]
    
    AT=at['Transaction_count'].sum()
    return AT

#Avg. transaction value
def aggre_transaction_avgtransactionamount(df,year,quarter):
    at= df[(df['Years']==year)&(df['Quarter']==quarter)]
    AT=at['Transaction_amount'].sum()/at['Transaction_count'].sum()
    Average_amount_integer = int(AT)
    return "₹"+ str(Average_amount_integer)

#Categories
def aggre_transaction_transactiontypecount(df,year,quarter):
    at= df[(df['Years']==year)&(df['Quarter']==quarter)]
    AT=at.groupby("Transaction_type")['Transaction_count'].sum()
    AT.sort_values(ascending=False, inplace=True)
    transaction_type=st.dataframe(AT)
    return transaction_type

#states
def aggre_transaction_topstatetransactioncount(df,year,quarter):
    at= df[(df['Years']==year)&(df['Quarter']==quarter)]
    agg_tran=at.groupby("States")['Transaction_count'].sum()
    Agg_tran=agg_tran.sort_values(ascending=False).head(10)
    Agg_tran_df=st.dataframe(Agg_tran)
    return Agg_tran_df

#district
def map_transaction_topdistricttransactioncount(df,year,quarter):
    mt= df[(df['Years']==year)&(df['Quarter']==quarter)]
    map_tran=mt.groupby("Districts")['Transaction_count'].sum()
    Map_tran=map_tran.sort_values(ascending=False).head(10)
    Map_tran_df=st.dataframe(Map_tran)
    return Map_tran_df

#pincodes
def Top_transaction_toppincodestransactioncount(df,year,quarter):
    tt= df[(df['Years']==year)&(df['Quarter']==quarter)]
    top_tran=tt.groupby("Pincodes")['Transaction_count'].sum()
    Top_tran=top_tran.sort_values(ascending=False).head(10)
    Top_tran_df=st.dataframe(Top_tran)
    return Top_tran_df

#geo states
def aggre_transaction_geotransactionamount(df,year,quarter):
    at= df[(df['Years']==year)&(df['Quarter']==quarter)]
    at.reset_index(drop=True,inplace=True)

    AI=at.groupby("States")[['Transaction_count',"Transaction_amount"]].sum()
    AI.reset_index(inplace=True)
    url="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response=requests.get(url)
    data=json.loads(response.content)
    state_names=[]

    for feature in data['features']:
        state_names.append(feature['properties']['ST_NM'])    
    state_names.sort()
    
    figure_india=px.choropleth_mapbox(AI,geojson=data,locations="States",featureidkey="properties.ST_NM",color="Transaction_amount",
                            color_continuous_scale=px.colors.diverging.PuOr,color_continuous_midpoint=0,
                           hover_name="States",center={"lat": 24, "lon": 79},mapbox_style="carto-positron",zoom=3.3,height=900,width=800)
    st.plotly_chart(figure_india)

def aggre_transaction_geotransactioncount(df,year,quarter):
    at= df[(df['Years']==year)&(df['Quarter']==quarter)]
    at.reset_index(drop=True,inplace=True)

    AI=at.groupby("States")[['Transaction_count',"Transaction_amount"]].sum()
    AI.reset_index(inplace=True)
    url="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response=requests.get(url)
    data=json.loads(response.content)
    state_names=[]

    for feature in data['features']:
        state_names.append(feature['properties']['ST_NM'])    
    state_names.sort()
    
    figure_india=px.choropleth_mapbox(AI,geojson=data,locations="States",featureidkey="properties.ST_NM",color="Transaction_count",
                            color_continuous_scale=px.colors.diverging.PuOr,color_continuous_midpoint=0,
                           hover_name="States",center={"lat": 24, "lon": 79},mapbox_style="carto-positron",zoom=3.3,height=900,width=800)
    st.plotly_chart(figure_india)

#agg_tran_count
def aggre_transaction_transactioncount(df,year,quarter):
    at= df[(df['Years']==year)&(df['Quarter']==quarter)]
    at.reset_index(drop=True,inplace=True)

    AT=at.groupby("States")[['Transaction_count',"Transaction_amount"]].sum()
    AT.sort_values(by='Transaction_count', ascending=False, inplace=True)
    AT.reset_index(inplace=True)

    figure_count=px.bar(AT,x='States',y="Transaction_count",orientation='v',title=f"Transaction_count Q {quarter}-{year}",color='Transaction_count',height=600,width=800)
    st.plotly_chart(figure_count)

#agg_tran_amount
def aggre_transaction_transactionamount(df,year,quarter):
    at= df[(df['Years']==year)&(df['Quarter']==quarter)]
    at.reset_index(drop=True,inplace=True)

    AT=at.groupby("States")[['Transaction_count',"Transaction_amount"]].sum()
    AT.sort_values(by='Transaction_amount', ascending=False, inplace=True)
    AT.reset_index(inplace=True)

    figure_amount=px.bar(AT,x='States',y="Transaction_amount",orientation='v',title=f'Transaction_amount Q {quarter}-{year}',color='Transaction_amount',height=600,width=800)
    st.plotly_chart(figure_amount)

#geo district
def map_transaction_geotransactionamount(df,Year,Quarter,State):
    mt= df[(df['Years']==Year)&(df['Quarter']==Quarter)&(df['States']==State)]
    mt.reset_index(drop=True,inplace=True)

    MT=mt.groupby("Districts")[['Transaction_count',"Transaction_amount"]].sum()
    MT.reset_index(inplace=True)
    file_path="C:/Users/dhuwa/Downloads/project folder/phonepe/pulse/output.geojson"
    with open(file_path, "r") as file:
        data = json.load(file)
    district_names=[]
    state=State
    def get_state_center(state):
        centers = {
            "Andaman & Nicobar Islands": {"lat": 10.7449, "lon": 92.5000},
            "Andhra Pradesh": {"lat": 15.9129, "lon": 79.74},
            "Arunachal Pradesh": {"lat": 28.2180, "lon": 94.7278},
            "Assam": {"lat": 26.2006, "lon": 92.9376},
            "Bihar": {"lat": 25.0961, "lon": 85.3131},
            "Chhattisgarh": {"lat": 21.2787, "lon": 81.8661},
            "Goa": {"lat": 15.2993, "lon": 74.1240},
            "Gujarat": {"lat": 22.2587, "lon": 71.1924},
            "Haryana": {"lat": 29.0588, "lon": 76.0856},
            "Himachal Pradesh": {"lat": 31.1048, "lon": 77.1734},
            "Jharkhand": {"lat": 23.6102, "lon": 85.2799},
            "Karnataka": {"lat": 15.3173, "lon": 75.7139},
            "Kerala": {"lat": 10.8505, "lon": 76.2711},
            "Madhya Pradesh": {"lat": 22.9734, "lon": 78.6569},
            "Maharashtra": {"lat": 19.7515, "lon": 75.7139},
            "Manipur": {"lat": 24.6637, "lon": 93.9063},
            "Meghalaya": {"lat": 25.4670, "lon": 91.3662},
            "Mizoram": {"lat": 23.1645, "lon": 92.9376},
            "Nagaland": {"lat": 26.1584, "lon": 94.5624},
            "Odisha": {"lat": 20.9517, "lon": 85.0985},
            "Punjab": {"lat": 31.1471, "lon": 75.3412},
            "Puducherry": {"lat": 11.9416, "lon": 79.8083},
            "Rajasthan": {"lat": 27.0238, "lon": 74.2179},
            "Sikkim": {"lat": 27.5330, "lon": 88.5122},
            "Tamil Nadu": {"lat": 11.1271, "lon": 78.6569},
            "Telangana": {"lat": 18.1124, "lon": 79.0193},
            "Tripura": {"lat": 23.9408, "lon": 91.9882},
            "Uttar Pradesh": {"lat": 26.8467, "lon": 80.9462},
            "Uttarakhand": {"lat": 30.0668, "lon": 79.0193},
            "West Bengal": {"lat": 22.9868, "lon": 87.8550}
        }
        
        return centers.get(state, {"lat": 0, "lon": 0})
    Center= get_state_center(state)
    for feature in data['features']:
        district_names.append(feature['properties']['dtname'])    
    district_names.sort()
    
    figure_state=px.choropleth_mapbox(MT,geojson=data,locations="Districts",featureidkey="properties.dtname",color="Transaction_amount",
                            color_continuous_scale=px.colors.diverging.RdBu,color_continuous_midpoint=0,
                           hover_name="Districts",center=Center,mapbox_style="open-street-map",zoom=5.5,height=550,width=550)
    st.plotly_chart(figure_state)

def map_transaction_geotransactioncount(df,Year,Quarter,State):
    mt= df[(df['Years']==Year)&(df['Quarter']==Quarter)&(df['States']==State)]
    mt.reset_index(drop=True,inplace=True)

    MT=mt.groupby("Districts")[['Transaction_count',"Transaction_amount"]].sum()
    MT.reset_index(inplace=True)
    file_path="C:/Users/dhuwa/Downloads/project folder/phonepe/pulse/output.geojson"
    with open(file_path, "r") as file:
        data = json.load(file)
    district_names=[]

    for feature in data['features']:
        district_names.append(feature['properties']['dtname'])    
    district_names.sort()
    state=State
    def get_state_center(state):
        centers = {
            "Andaman & Nicobar Islands": {"lat": 10.7449, "lon": 92.5000},
            "Andhra Pradesh": {"lat": 15.9129, "lon": 79.74},
            "Arunachal Pradesh": {"lat": 28.2180, "lon": 94.7278},
            "Assam": {"lat": 26.2006, "lon": 92.9376},
            "Bihar": {"lat": 25.0961, "lon": 85.3131},
            "Chhattisgarh": {"lat": 21.2787, "lon": 81.8661},
            "Goa": {"lat": 15.2993, "lon": 74.1240},
            "Gujarat": {"lat": 22.2587, "lon": 71.1924},
            "Haryana": {"lat": 29.0588, "lon": 76.0856},
            "Himachal Pradesh": {"lat": 31.1048, "lon": 77.1734},
            "Jharkhand": {"lat": 23.6102, "lon": 85.2799},
            "Karnataka": {"lat": 15.3173, "lon": 75.7139},
            "Kerala": {"lat": 10.8505, "lon": 76.2711},
            "Madhya Pradesh": {"lat": 22.9734, "lon": 78.6569},
            "Maharashtra": {"lat": 19.7515, "lon": 75.7139},
            "Manipur": {"lat": 24.6637, "lon": 93.9063},
            "Meghalaya": {"lat": 25.4670, "lon": 91.3662},
            "Mizoram": {"lat": 23.1645, "lon": 92.9376},
            "Nagaland": {"lat": 26.1584, "lon": 94.5624},
            "Odisha": {"lat": 20.9517, "lon": 85.0985},
            "Punjab": {"lat": 31.1471, "lon": 75.3412},
            "Puducherry": {"lat": 11.9416, "lon": 79.8083},
            "Rajasthan": {"lat": 27.0238, "lon": 74.2179},
            "Sikkim": {"lat": 27.5330, "lon": 88.5122},
            "Tamil Nadu": {"lat": 11.1271, "lon": 78.6569},
            "Telangana": {"lat": 18.1124, "lon": 79.0193},
            "Tripura": {"lat": 23.9408, "lon": 91.9882},
            "Uttar Pradesh": {"lat": 26.8467, "lon": 80.9462},
            "Uttarakhand": {"lat": 30.0668, "lon": 79.0193},
            "West Bengal": {"lat": 22.9868, "lon": 87.8550}
        }
        
        return centers.get(state, {"lat": 0, "lon": 0})
    Center= get_state_center(state)

    figure_state=px.choropleth_mapbox(MT,geojson=data,locations="Districts",featureidkey="properties.dtname",color="Transaction_count",
                            color_continuous_scale=px.colors.diverging.RdBu,color_continuous_midpoint=0,
                           hover_name="Districts",center=Center,mapbox_style="open-street-map",zoom=5.5,height=550,width=550)
    st.plotly_chart(figure_state)

def map_transaction_transactioncount(df,State,Year,Quarter):
    mt= df[(df['Years']==Year)&(df['Quarter']==Quarter)&(df['States']==State)]
    mt.reset_index(drop=True,inplace=True)

    MT=mt.groupby("Districts")[['Transaction_count',"Transaction_amount"]].sum()
    MT.reset_index(inplace=True)
    MT.sort_values(by='Transaction_count', ascending=False, inplace=True)
    MT.reset_index(inplace=True)

    figure_count=px.bar(MT,x='Districts',y="Transaction_count",orientation='v',title=f"Transaction_count Q {Quarter}-{Year}",color='Transaction_count',height=600,width=800)
    st.plotly_chart(figure_count)

def map_transaction_transactionamount(df,State,Year,Quarter):
    mt= df[(df['Years']==Year)&(df['Quarter']==Quarter)&(df['States']==State)]
    mt.reset_index(drop=True,inplace=True)

    MT=mt.groupby("Districts")[['Transaction_count',"Transaction_amount"]].sum()
    MT.reset_index(inplace=True)
    MT.sort_values(by='Transaction_amount', ascending=False, inplace=True)
    MT.reset_index(inplace=True)

    figure_amount=px.bar(MT,x='Districts',y="Transaction_amount",orientation='v',title=f"Transaction_amount Q {Quarter}-{Year}",color='Transaction_amount',height=600,width=800)
    st.plotly_chart(figure_amount)

#User inforamation
#Registered PhonePe users
def map_user_RegisteredUserscount(df,year,quarter):
    mu= df[(df['Years']==year)&(df['Quarter']==quarter)]
    
    MU=mu['RegisteredUser'].sum()
    return MU

#PhonePe app opens in
def map_user_AppOpenscount(df,year,quarter):
    mu= df[(df['Years']==year)&(df['Quarter']==quarter)]
    MU=mu['AppOpens'].sum()
    if MU ==0:
        return "Unavailable"
    else:
        formatted_output = "{:,}".format(MU)
        return formatted_output
    
#states
def aggre_user_topstatetransactioncount(df,year,quarter):
    au= df[(df['Years']==year)&(df['Quarter']==quarter)]
    agg_user=au.groupby("States")['RegisteredUser'].sum()
    Agg_user=agg_user.sort_values(ascending=False).head(10)
    Agg_user_df=st.dataframe(Agg_user)
    return Agg_user_df

#district
def map_user_topdistricttransactioncount(df,year,quarter):
    mu= df[(df['Years']==year)&(df['Quarter']==quarter)]
    map_user=mu.groupby("Districts")['RegisteredUser'].sum()
    Map_user=map_user.sort_values(ascending=False).head(10)
    Map_user_df=st.dataframe(Map_user)
    return Map_user_df

#pincodes
def Top_user_toppincodestransactioncount(df,year,quarter):
    tu= df[(df['Years']==year)&(df['Quarter']==quarter)]
    top_user=tu.groupby("Pincodes")['RegisteredUser'].sum()
    Top_user=top_user.sort_values(ascending=False).head(10)
    Top_user_df=st.dataframe(Top_user)
    return Top_user_df

#geo states
def map_user_geoRegisteredUser(df,year,quarter):
    mu= df[(df['Years']==year)&(df['Quarter']==quarter)]
    mu.reset_index(drop=True,inplace=True)

    MU=mu.groupby("States")[['RegisteredUser',"AppOpens"]].sum()
    MU.reset_index(inplace=True)
    url="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response=requests.get(url)
    data=json.loads(response.content)
    state_names=[]

    for feature in data['features']:
        state_names.append(feature['properties']['ST_NM'])    
    state_names.sort()
    
    Figure_india=px.choropleth_mapbox(MU,geojson=data,locations="States",featureidkey="properties.ST_NM",color="RegisteredUser",
                            color_continuous_scale=px.colors.diverging.PuOr,color_continuous_midpoint=0,
                           hover_name="States",center={"lat": 24, "lon": 79},mapbox_style="carto-positron",zoom=3.3,height=900,width=800)
    st.plotly_chart(Figure_india)

def map_user_allRegisteredUser(df,year,quarter):
    at= df[(df['Years']==year)&(df['Quarter']==quarter)]
    at.reset_index(drop=True,inplace=True)

    AT=at.groupby("States")[['RegisteredUser',"AppOpens"]].sum()
    AT.sort_values(by='RegisteredUser', ascending=False, inplace=True)
    AT.reset_index(inplace=True)

    figure_amount=px.bar(AT,x='States',y="RegisteredUser",orientation='v',title=f'RegisteredUser Q {quarter}-{year}',color='RegisteredUser',height=600,width=800)
    st.plotly_chart(figure_amount)
#geo states
def map_user_geoAppOpens(df,year,quarter):
    mu= df[(df['Years']==year)&(df['Quarter']==quarter)]
    mu.reset_index(drop=True,inplace=True)

    MU=mu.groupby("States")[['RegisteredUser',"AppOpens"]].sum()
    MU.reset_index(inplace=True)
    url="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response=requests.get(url)
    data=json.loads(response.content)
    state_names=[]

    for feature in data['features']:
        state_names.append(feature['properties']['ST_NM'])    
    state_names.sort()
    
    fig_india=px.choropleth_mapbox(MU,geojson=data,locations="States",featureidkey="properties.ST_NM",color="AppOpens",
                            color_continuous_scale=px.colors.diverging.PuOr,color_continuous_midpoint=0,
                           hover_name="States",center={"lat": 24, "lon": 79},mapbox_style="carto-positron",zoom=3.3,height=900,width=800)
    st.plotly_chart(fig_india)

def map_user_allAppOpens(df,year,quarter):
    at= df[(df['Years']==year)&(df['Quarter']==quarter)]
    at.reset_index(drop=True,inplace=True)

    AT=at.groupby("States")[['RegisteredUser',"AppOpens"]].sum()
    AT.sort_values(by='AppOpens', ascending=False, inplace=True)
    AT.reset_index(inplace=True)

    figure_amount=px.bar(AT,x='States',y="AppOpens",orientation='v',title=f'AppOpens Q {quarter}-{year}',color='AppOpens',height=600,width=800)
    st.plotly_chart(figure_amount)

def aggre_user_individualtransactioncount(df,State,Year,Quarter):
    au= df[(df['Years']==Year)&(df['Quarter']==Quarter)&(df['States']==State)]
    au.reset_index(drop=True,inplace=True)

    AU=au.groupby("Brands")[['Transaction_count',"Percentage"]].sum()
    AU.reset_index(inplace=True)
    AU.sort_values(by='Transaction_count', ascending=False, inplace=True)
    AU.reset_index(inplace=True)

    fig_count=px.bar(AU,x='Brands',y="Transaction_count",orientation='v',color='Transaction_count',height=600,width=800)
    st.plotly_chart(fig_count)

def map_user_plot_1(df,Year,Quarter,State):
    muy=df[(df['Years']==Year)&(df['Quarter']==Quarter)&(df['States']==State)]
    muy.reset_index(drop=True,inplace=True)
    muyg= muy.groupby("Districts")[["RegisteredUser","AppOpens"]].sum()
    muyg.reset_index(inplace=True)
    fig_line_1= px.line(muyg,x="Districts",y=["RegisteredUser","AppOpens"],
                        width= 1000, height= 800, markers= True)
    st.plotly_chart(fig_line_1)

#insurance information
def aggre_insurance_transactioncount(df,year,quarter):
    ai= df[(df['Years']==year)&(Aggre_insurance['Quarter']==quarter)]
    ai.reset_index(drop=True,inplace=True)

    AI=ai.groupby("States")[['Transaction_count',"Transaction_amount"]].sum()
    AI.sort_values(by='Transaction_count', ascending=False, inplace=True)
    AI.reset_index(inplace=True)

    fig_count=px.bar(AI,x='States',y="Transaction_count",orientation='v',title=f"Transaction_count Q {quarter}-{year}",color='Transaction_count',height=600,width=800)
    st.plotly_chart(fig_count)

def aggre_insurance_transactionamount(df,year,quarter):
    ai= df[(df['Years']==year)&(Aggre_insurance['Quarter']==quarter)]
    ai.reset_index(drop=True,inplace=True)

    AI=ai.groupby("States")[['Transaction_count',"Transaction_amount"]].sum()
    AI.sort_values(by='Transaction_amount', ascending=False, inplace=True)
    AI.reset_index(inplace=True)

    fig_amount=px.bar(AI,x='States',y="Transaction_amount",orientation='v',title=f'Transaction_amount Q {quarter}-{year}',color='Transaction_amount',height=600,width=800)
    st.plotly_chart(fig_amount)

def aggre_insurance_totaltransactioncount(df,year,quarter):
    ai= df[(df['Years']==year)&(df['Quarter']==quarter)]
    
    AI=ai['Transaction_count'].sum()
    return AI

def aggre_insurance_totaltransactionamount(df,year,quarter):
    ai= df[(df['Years']==year)&(df['Quarter']==quarter)]
    
    AI=ai['Transaction_amount'].sum()
    return '₹'+'{:,.0f} Cr'.format(round(AI / 10000000))

def aggre_insurance_avgtransactionamount(df, year, quarter):
    ai = df[(df['Years'] == year) & (df['Quarter'] == quarter)]
    total_transaction_count = ai['Transaction_count'].sum()
    total_transaction_amount = ai['Transaction_amount'].sum()
    
    if total_transaction_count == 0:
        return "No data available"
    
    average_amount = total_transaction_amount / total_transaction_count
    if pd.isnull(average_amount): 
        return "No data available"
    
    average_amount_integer = int(average_amount)
    return "₹" + str(average_amount_integer)

def aggre_insurance_geotransactionamount(df,year,quarter):
    ai= df[(df['Years']==year)&(df['Quarter']==quarter)]
    ai.reset_index(drop=True,inplace=True)

    AI=ai.groupby("States")[['Transaction_count',"Transaction_amount"]].sum()
    AI.reset_index(inplace=True)
    url="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response=requests.get(url)
    data=json.loads(response.content)
    state_names=[]

    for feature in data['features']:
        state_names.append(feature['properties']['ST_NM'])    
    state_names.sort()
    
    fig_india=px.choropleth_mapbox(AI,geojson=data,locations="States",featureidkey="properties.ST_NM",color="Transaction_amount",
                            color_continuous_scale=px.colors.diverging.PuOr,color_continuous_midpoint=0,
                           hover_name="States",center={"lat": 24, "lon": 79},mapbox_style="carto-positron",zoom=3.3,height=900,width=800)
    st.plotly_chart(fig_india)

def aggre_insurance_geotransactioncount(df,year,quarter):
    ai= df[(df['Years']==year)&(df['Quarter']==quarter)]
    ai.reset_index(drop=True,inplace=True)

    AI=ai.groupby("States")[['Transaction_count',"Transaction_amount"]].sum()
    AI.reset_index(inplace=True)
    url="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response=requests.get(url)
    data=json.loads(response.content)
    state_names=[]

    for feature in data['features']:
        state_names.append(feature['properties']['ST_NM'])    
    state_names.sort()
    
    fig_india=px.choropleth_mapbox(AI,geojson=data,locations="States",featureidkey="properties.ST_NM",color="Transaction_count",
                            color_continuous_scale=px.colors.diverging.PuOr,color_continuous_midpoint=0,
                           hover_name="States",center={"lat": 24, "lon": 79},mapbox_style="carto-positron",zoom=3.3,height=900,width=800)
    st.plotly_chart(fig_india)
    
def aggre_insurance_topstatetransactioncount(df,year,quarter):
    ai= df[(df['Years']==year)&(df['Quarter']==quarter)]
    agg_insu=ai.groupby("States")['Transaction_count'].sum()
    Agg_insur=agg_insu.sort_values(ascending=False).head(10)
    Agg_ins_df=st.dataframe(Agg_insur)
    return Agg_ins_df        
       
def map_insurance_topdistricttransactioncount(df,year,quarter):
    ai= df[(df['Years']==year)&(df['Quarter']==quarter)]
    agg_insu=ai.groupby("Districts")['Transaction_count'].sum()
    Agg_insur=agg_insu.sort_values(ascending=False).head(10)
    Agg_ins_df=st.dataframe(Agg_insur)
    return Agg_ins_df

def Top_insurance_toppincodetransactioncount(df,year,quarter):
    ai= df[(df['Years']==year)&(df['Quarter']==quarter)]
    agg_insu=ai.groupby("Pincodes")['Transaction_count'].sum()
    Agg_insur=agg_insu.sort_values(ascending=False).head(10)
    Agg_ins_df=st.dataframe(Agg_insur)
    return Agg_ins_df

def map_insurance_transactioncount(df,State,Year,Quarter):
    ai= df[(df['Years']==Year)&(df['Quarter']==Quarter)&(df['States']==State)]
    ai.reset_index(drop=True,inplace=True)

    AI=ai.groupby("Districts")[['Transaction_count',"Transaction_amount"]].sum()
    AI.reset_index(inplace=True)
    AI.sort_values(by='Transaction_count', ascending=False, inplace=True)
    AI.reset_index(inplace=True)

    Fig_count=px.bar(AI,x='Districts',y="Transaction_count",orientation='v',title=f"Transaction_count Q {Quarter}-{Year}",color='Transaction_count',height=600,width=800)
    st.plotly_chart(Fig_count)

def map_insurance_transactionamount(df,State,Year,Quarter):
    ai= df[(df['Years']==Year)&(df['Quarter']==Quarter)&(df['States']==State)]
    ai.reset_index(drop=True,inplace=True)

    AI=ai.groupby("Districts")[['Transaction_count',"Transaction_amount"]].sum()
    AI.reset_index(inplace=True)
    AI.sort_values(by='Transaction_amount', ascending=False, inplace=True)
    AI.reset_index(inplace=True)

    Fig_amount=px.bar(AI,x='Districts',y="Transaction_amount",orientation='v',title=f"Transaction_amount Q {Quarter}-{Year}",color='Transaction_amount',height=600,width=800)
    st.plotly_chart(Fig_amount)

def map_insurance_geotransactionamount(df,Year,Quarter,State):
    ai= df[(df['Years']==Year)&(df['Quarter']==Quarter)&(df['States']==State)]
    ai.reset_index(drop=True,inplace=True)

    AI=ai.groupby("Districts")[['Transaction_count',"Transaction_amount"]].sum()
    AI.reset_index(inplace=True)
    file_path="C:/Users/dhuwa/Downloads/project folder/phonepe/pulse/output.geojson"
    with open(file_path, "r") as file:
        data = json.load(file)
    district_names=[]
    state=State
    def get_state_center(state):
        centers = {
            "Andaman & Nicobar Islands": {"lat": 10.7449, "lon": 92.5000},
            "Andhra Pradesh": {"lat": 15.9129, "lon": 79.74},
            "Arunachal Pradesh": {"lat": 28.2180, "lon": 94.7278},
            "Assam": {"lat": 26.2006, "lon": 92.9376},
            "Bihar": {"lat": 25.0961, "lon": 85.3131},
            "Chhattisgarh": {"lat": 21.2787, "lon": 81.8661},
            "Goa": {"lat": 15.2993, "lon": 74.1240},
            "Gujarat": {"lat": 22.2587, "lon": 71.1924},
            "Haryana": {"lat": 29.0588, "lon": 76.0856},
            "Himachal Pradesh": {"lat": 31.1048, "lon": 77.1734},
            "Jharkhand": {"lat": 23.6102, "lon": 85.2799},
            "Karnataka": {"lat": 15.3173, "lon": 75.7139},
            "Kerala": {"lat": 10.8505, "lon": 76.2711},
            "Madhya Pradesh": {"lat": 22.9734, "lon": 78.6569},
            "Maharashtra": {"lat": 19.7515, "lon": 75.7139},
            "Manipur": {"lat": 24.6637, "lon": 93.9063},
            "Meghalaya": {"lat": 25.4670, "lon": 91.3662},
            "Mizoram": {"lat": 23.1645, "lon": 92.9376},
            "Nagaland": {"lat": 26.1584, "lon": 94.5624},
            "Odisha": {"lat": 20.9517, "lon": 85.0985},
            "Punjab": {"lat": 31.1471, "lon": 75.3412},
            "Puducherry": {"lat": 11.9416, "lon": 79.8083},
            "Rajasthan": {"lat": 27.0238, "lon": 74.2179},
            "Sikkim": {"lat": 27.5330, "lon": 88.5122},
            "Tamil Nadu": {"lat": 11.1271, "lon": 78.6569},
            "Telangana": {"lat": 18.1124, "lon": 79.0193},
            "Tripura": {"lat": 23.9408, "lon": 91.9882},
            "Uttar Pradesh": {"lat": 26.8467, "lon": 80.9462},
            "Uttarakhand": {"lat": 30.0668, "lon": 79.0193},
            "West Bengal": {"lat": 22.9868, "lon": 87.8550}
        }
        
        return centers.get(state, {"lat": 0, "lon": 0})
    Center= get_state_center(state)
    for feature in data['features']:
        district_names.append(feature['properties']['dtname'])    
    district_names.sort()
    
    Fig_india=px.choropleth_mapbox(AI,geojson=data,locations="Districts",featureidkey="properties.dtname",color="Transaction_amount",
                            color_continuous_scale=px.colors.diverging.RdBu,color_continuous_midpoint=0,
                           hover_name="Districts",center=Center,mapbox_style="open-street-map",zoom=5.5,height=550,width=550)
    st.plotly_chart(Fig_india)

def map_insurance_geotransactioncount(df,Year,Quarter,State):
    ai= df[(df['Years']==Year)&(df['Quarter']==Quarter)&(df['States']==State)]
    ai.reset_index(drop=True,inplace=True)

    AI=ai.groupby("Districts")[['Transaction_count',"Transaction_amount"]].sum()
    AI.reset_index(inplace=True)
    file_path="C:/Users/dhuwa/Downloads/project folder/phonepe/pulse/output.geojson"
    with open(file_path, "r") as file:
        data = json.load(file)
    district_names=[]
    state=State
    def get_state_center(state):
        centers = {
            "Andaman & Nicobar Islands": {"lat": 10.7449, "lon": 92.5000},
            "Andhra Pradesh": {"lat": 15.9129, "lon": 79.74},
            "Arunachal Pradesh": {"lat": 28.2180, "lon": 94.7278},
            "Assam": {"lat": 26.2006, "lon": 92.9376},
            "Bihar": {"lat": 25.0961, "lon": 85.3131},
            "Chhattisgarh": {"lat": 21.2787, "lon": 81.8661},
            "Goa": {"lat": 15.2993, "lon": 74.1240},
            "Gujarat": {"lat": 22.2587, "lon": 71.1924},
            "Haryana": {"lat": 29.0588, "lon": 76.0856},
            "Himachal Pradesh": {"lat": 31.1048, "lon": 77.1734},
            "Jharkhand": {"lat": 23.6102, "lon": 85.2799},
            "Karnataka": {"lat": 15.3173, "lon": 75.7139},
            "Kerala": {"lat": 10.8505, "lon": 76.2711},
            "Madhya Pradesh": {"lat": 22.9734, "lon": 78.6569},
            "Maharashtra": {"lat": 19.7515, "lon": 75.7139},
            "Manipur": {"lat": 24.6637, "lon": 93.9063},
            "Meghalaya": {"lat": 25.4670, "lon": 91.3662},
            "Mizoram": {"lat": 23.1645, "lon": 92.9376},
            "Nagaland": {"lat": 26.1584, "lon": 94.5624},
            "Odisha": {"lat": 20.9517, "lon": 85.0985},
            "Punjab": {"lat": 31.1471, "lon": 75.3412},
            "Puducherry": {"lat": 11.9416, "lon": 79.8083},
            "Rajasthan": {"lat": 27.0238, "lon": 74.2179},
            "Sikkim": {"lat": 27.5330, "lon": 88.5122},
            "Tamil Nadu": {"lat": 11.1271, "lon": 78.6569},
            "Telangana": {"lat": 18.1124, "lon": 79.0193},
            "Tripura": {"lat": 23.9408, "lon": 91.9882},
            "Uttar Pradesh": {"lat": 26.8467, "lon": 80.9462},
            "Uttarakhand": {"lat": 30.0668, "lon": 79.0193},
            "West Bengal": {"lat": 22.9868, "lon": 87.8550}
        }
        
        return centers.get(state, {"lat": 0, "lon": 0})
    Center= get_state_center(state)
    for feature in data['features']:
        district_names.append(feature['properties']['dtname'])    
    district_names.sort()
    
    Fig_india=px.choropleth_mapbox(AI,geojson=data,locations="Districts",featureidkey="properties.dtname",color="Transaction_count",
                            color_continuous_scale=px.colors.diverging.RdBu,color_continuous_midpoint=0,
                           hover_name="Districts",center=Center,mapbox_style="open-street-map",zoom=5.5,height=550,width=550)
    st.plotly_chart(Fig_india)


#Top Charts
#states
def visual_statetransactionamount(df):
    at=df.groupby('States')[['Transaction_amount','Transaction_count']].sum()
    at.reset_index(inplace=True)
    at.sort_values(by="Transaction_amount",ascending=True,inplace=True)
    
    top_states=at.tail(10)
    least_states=at.head(10)
    TS=px.bar(top_states,x="Transaction_amount",y="States",orientation='h',title="Top 10 States Transaction Amount",color="Transaction_amount",height=600,width=650)
    LS=px.bar(least_states,x="Transaction_amount",y="States",orientation='h',title="Last 10 States Transaction Amount",color="Transaction_amount",height=600,width=650)

    col1,col2=st.columns(2)
    
    with col1:
        st.plotly_chart(TS)
    with col2:
        st.plotly_chart(LS)
        
def visual_totalstatetransactionamount(df):
    at=df.groupby('States')[['Transaction_amount','Transaction_count']].sum()
    at.reset_index(inplace=True)
    at.sort_values(by="Transaction_amount",ascending=True,inplace=True)
    at.reset_index(drop=True,inplace=True)
    VT=px.bar(at,x="Transaction_amount",y="States",orientation='h',title="Overall States Transaction Amount",color="Transaction_amount",height=1050,width=1000)
    st.plotly_chart(VT)

def visual_statetransactioncount(df):
    at=df.groupby('States')[['Transaction_amount','Transaction_count']].sum()
    at.reset_index(inplace=True)
    at.sort_values(by="Transaction_count",ascending=True,inplace=True)
    
    top_states=at.tail(10)
    least_states=at.head(10)
    TS=px.bar(top_states,x="Transaction_count",y="States",orientation='h',title="Top 10 States Transaction Count",color="Transaction_count",height=600,width=650)
    LS=px.bar(least_states,x="Transaction_count",y="States",orientation='h',title="Last 10 States Transaction Count",color="Transaction_count",height=600,width=650)

    col1,col2=st.columns(2)
    
    with col1:
        st.plotly_chart(TS)
    with col2:
        st.plotly_chart(LS)

def visual_totalstatetransactioncount(df):
    at=df.groupby('States')[['Transaction_amount','Transaction_count']].sum()
    at.reset_index(inplace=True)
    at.sort_values(by="Transaction_count",ascending=True,inplace=True)
    at.reset_index(drop=True,inplace=True)
    VT=px.bar(at,x="Transaction_count",y="States",orientation='h',title="Overall States Transaction Count",color="Transaction_count",height=1050,width=1000)
    st.plotly_chart(VT)

#districts
def visual_districtstransactionamount(df,states):
    at=df[df['States']==states]
    at=at.groupby('Districts')[['Transaction_amount','Transaction_count']].sum()
    at.reset_index(inplace=True)
    at.sort_values(by="Transaction_amount",ascending=True,inplace=True)
    
    top_districts=at.tail(10)
    last_districts=at.head(10)
    TS=px.bar(top_districts,x="Transaction_amount",y="Districts",orientation='h',title="Top 10 Districts Transaction Amount",color="Transaction_amount",height=600,width=650)
    LS=px.bar(last_districts,x="Transaction_amount",y="Districts",orientation='h',title="Last 10 Districts Transaction Amount",color="Transaction_amount",height=600,width=650)

    col1,col2=st.columns(2)
    
    with col1:
        st.plotly_chart(TS)
    with col2:
        st.plotly_chart(LS)

    OD=px.bar(at,x="Transaction_amount",y="Districts",orientation='h',title="Overall Districts Transaction Amount",color="Transaction_amount",height=900,width=950)
    st.plotly_chart(OD)


def visual_districtstransactioncount(df,states):
    at=df[df['States']==states]
    at=at.groupby('Districts')[['Transaction_amount','Transaction_count']].sum()
    at.reset_index(inplace=True)
    at.sort_values(by="Transaction_count",ascending=True,inplace=True)
    
    top_districts=at.tail(10)
    last_districts=at.head(10)
    TS=px.bar(top_districts,x="Transaction_count",y="Districts",orientation='h',title="Top 10 Districts Transaction Count",color="Transaction_count",height=600,width=650)
    LS=px.bar(last_districts,x="Transaction_count",y="Districts",orientation='h',title="Last 10 Districts Transaction Count",color="Transaction_count",height=600,width=650)

    col1,col2=st.columns(2)
    
    with col1:
        st.plotly_chart(TS)
    with col2:
        st.plotly_chart(LS)
    
    OD=px.bar(at,x="Transaction_amount",y="Districts",orientation='h',title="Overall Districts Transaction Amount",color="Transaction_amount",height=900,width=950)
    st.plotly_chart(OD)


#pincode
def visual_pincodestransactionamount(df,states):
    at=df[df['States']==states]
    at=at.groupby('Pincodes')[['Transaction_amount','Transaction_count']].sum()
    at.reset_index(inplace=True)
    at['Pincodes'] = at['Pincodes'].astype(str) +'P'
    at.sort_values(by="Transaction_amount",ascending=True,inplace=True)
    
    top_states=at.tail(10)
    last_states=at.head(10)
    TS=px.bar(top_states,x="Transaction_amount",y="Pincodes",orientation='h',title="Top 10 Postal Codes Transaction Amount",color="Transaction_amount",height=600,width=650)
    LS=px.bar(last_states,x="Transaction_amount",y="Pincodes",orientation='h',title="Last 10 Postal Codes Transaction Amount",color="Transaction_amount",height=600,width=650)
    col1,col2=st.columns(2)
    
    with col1:
        st.plotly_chart(TS)
    with col2:
        st.plotly_chart(LS)

    OD=px.bar(at,x="Transaction_amount",y="Pincodes",orientation='h',title="Overall Postal Codes Transaction Amount",color="Transaction_amount",height=1050,width=950)
    st.plotly_chart(OD)


def visual_pincodestransactioncount(df,states):
    at=df[df['States']==states]
    at=at.groupby('Pincodes')[['Transaction_amount','Transaction_count']].sum()
    at.reset_index(inplace=True)
    at['Pincodes'] = at['Pincodes'].astype(str) +'P'
    at.sort_values(by="Transaction_count",ascending=True,inplace=True)
    
    top_states=at.tail(10)
    least_states=at.head(10)
    TS=px.bar(top_states,x="Transaction_count",y="Pincodes",orientation='h',title="Top 10 Postal Codes Transaction Amount",color="Transaction_count",height=600,width=650)
    LS=px.bar(least_states,x="Transaction_count",y="Pincodes",orientation='h',title="Last 10 Postal Codes Transaction Amount",color="Transaction_count",height=600,width=650)
    
    col1,col2=st.columns(2)
    
    with col1:
        st.plotly_chart(TS)
    with col2:
        st.plotly_chart(LS)
    OD=px.bar(at,x="Transaction_count",y="Pincodes",orientation='h',title="Overall Postal Codes Transaction Count",color="Transaction_count",height=1050,width=950)
    st.plotly_chart(OD)


def visual_statetransactioncountu(df):
    at=df.groupby('States')[['Transaction_count','Percentage']].sum()
    at.reset_index(inplace=True)
    at.sort_values(by="Transaction_count",ascending=True,inplace=True)
    
    top_states=at.tail(10)
    least_states=at.head(10)
    TS=px.bar(top_states,x="Transaction_count",y="States",orientation='h',title="Top 10 States Transaction Count",color="Transaction_count",height=600,width=650)
    LS=px.bar(least_states,x="Transaction_count",y="States",orientation='h',title="Last 10 States Transaction Count",color="Transaction_count",height=600,width=650)

    col1,col2=st.columns(2)
    
    with col1:
        st.plotly_chart(TS)
    with col2:
        st.plotly_chart(LS)

def visual_totalstatetransactioncountu(df):
    at=df.groupby('States')[['Percentage','Transaction_count']].sum()
    at.reset_index(inplace=True)
    at.sort_values(by="Transaction_count",ascending=True,inplace=True)
    at.reset_index(drop=True,inplace=True)
    VT=px.bar(at,x="Transaction_count",y="States",orientation='h',title="Overall States Transaction Count",color="Transaction_count",height=1050,width=1000)
    st.plotly_chart(VT)

#Registered User
def visual_districtsRegisteredUser(df,states):
    at=df[df['States']==states]
    at=at.groupby('Districts')[['RegisteredUser','AppOpens']].sum()
    at.reset_index(inplace=True)
    at.sort_values(by="RegisteredUser",ascending=True,inplace=True)
    
    top_districts=at.tail(10)
    last_districts=at.head(10)
    TS=px.bar(top_districts,x="RegisteredUser",y="Districts",orientation='h',title="Top 10 Districts RegisteredUser",color="RegisteredUser",height=600,width=650)
    LS=px.bar(last_districts,x="RegisteredUser",y="Districts",orientation='h',title="Last 10 Districts RegisteredUser",color="RegisteredUser",height=600,width=650)

    col1,col2=st.columns(2)
    
    with col1:
        st.plotly_chart(TS)
    with col2:
        st.plotly_chart(LS)

    OD=px.bar(at,x="RegisteredUser",y="Districts",orientation='h',title="Overall Districts RegisteredUser",color="RegisteredUser",height=900,width=950)
    st.plotly_chart(OD)

#AppOpens
def visual_districtsAppOpens(df,states):
    at=df[df['States']==states]
    at=at.groupby('Districts')[['RegisteredUser','AppOpens']].sum()
    at.reset_index(inplace=True)
    at.sort_values(by="AppOpens",ascending=True,inplace=True)
    
    top_districts=at.tail(10)
    last_districts=at.head(10)
    TS=px.bar(top_districts,x="AppOpens",y="Districts",orientation='h',title="Top 10 Districts AppOpens",color="AppOpens",height=600,width=650)
    LS=px.bar(last_districts,x="AppOpens",y="Districts",orientation='h',title="Last 10 Districts AppOpens",color="AppOpens",height=600,width=650)

    col1,col2=st.columns(2)
    
    with col1:
        st.plotly_chart(TS)
    with col2:
        st.plotly_chart(LS)

    OD=px.bar(at,x="RegisteredUser",y="Districts",orientation='h',title="Overall Districts AppOpens",color="RegisteredUser",height=900,width=950)
    st.plotly_chart(OD)

#Registered User States
def visual_statesRegisteredUser(df):
    at=df.groupby("States")['RegisteredUser'].sum()
    at=pd.DataFrame(at)
    at.reset_index(inplace=True)
    at.sort_values(by="RegisteredUser",ascending=True,inplace=True)
    
    top_districts=at.tail(10)
    last_districts=at.head(10)
    TS=px.bar(top_districts,x="RegisteredUser",y="States",orientation='h',title="Top 10 States RegisteredUser",color="RegisteredUser",height=600,width=650)
    LS=px.bar(last_districts,x="RegisteredUser",y="States",orientation='h',title="Last 10 States RegisteredUser",color="RegisteredUser",height=600,width=650)

    col1,col2=st.columns(2)
    
    with col1:
        st.plotly_chart(TS)
    with col2:
        st.plotly_chart(LS)

    OD=px.bar(at,x="RegisteredUser",y="States",orientation='h',title="Overall States RegisteredUser",color="RegisteredUser",height=900,width=950)
    st.plotly_chart(OD)

#streamlit part
st.set_page_config(layout="wide")  
st.title(":violet[PHONEPE DATA VISUALIZATION AND EXPLORATION]")

tab1,tab2,tab3,tab4=st.tabs(['ABOUT','HOME','ANALYSIS','Top Charts'])

with tab1:
    col1,col2=st.columns(2)
    with col1:
        st.image("phonepayimage.jpg")
        st.write("PhonePe is a digital payment platform and financial technology company based in India. It was founded in December 2015 by Sameer Nigam, Rahul Chari, and Burzin Engineer. The company initially began as a Unified Payments Interface (UPI)-based app allowing users to make payments, recharge mobile phones, and pay utility bills among other services.")
        st.link_button("DOWNLOAD THE APP NOW", "https://www.phonepe.com/app-download/")

    with col2:
        st.image("mobile.png")

with tab2:
    col3,col4=st.columns(2)
    with col3:
        st.image("Pulse.jpg")

    with col4:
        st.subheader(":violet[Phonepe Pulse:]")
        st.write("<div style='text-align:left'>PhonePe Pulse served as a useful tool for businesses to understand market dynamics, tailor their offerings,and optimize their marketing strategies.For users,it provided a glimpse into their spending habits and allowed them to make more informed financial decisions.</div>", unsafe_allow_html=True)
        st.subheader(":violet[Phonepe Pulse Visualization:]")
        st.write("PhonePe Pulse Visualization is a feature within the PhonePe app that provides users and businesses with clear, graphical insights into digital payment trends. It offers intuitive graphs, charts, and heatmaps to visualize transaction volumes, spending patterns, and regional variations.")
        st.subheader("Done by: DHUWARAGANATH ")

        st.markdown("[LinkedIn](https://www.linkedin.com/in/dhuwaraganath-s)")
        st.markdown("[GitHub](https://github.com/DHUWARAGANATH)")

with tab3:
    st.header(":violet[Phonepe Pulse 2018 to 2023 Analysis]")
    options=st.selectbox("Select the Transaction",("PAYMENT","INSURANCE"))

    if options == "PAYMENT":
        check = st.selectbox("Select an option", ("TRANSACTION", "USER"))
        if check =="TRANSACTION":
            Col1,Col2=st.columns([8,4])
        
            with Col2:
                YEAR_selected, QUARTER_selected,Transaction_selected = st.columns(3)

                with YEAR_selected:
                    YEAR = st.selectbox("Select a year", Aggre_transaction['Years'].unique())

                with QUARTER_selected:
                    QUARTER = st.selectbox("Select a quarter", Aggre_transaction['Quarter'].unique())

                with Transaction_selected:
                    trans=["Transaction_count","Transaction_amount"]
                    Trans=st.selectbox("select a Transaction",trans)
                st.header(":blue[Transactions]")
                st.write("All PhonePe transactions (UPI + Cards + Wallets)")
                Total_count = aggre_transaction_totaltransactioncount(Aggre_transaction,YEAR,QUARTER)
                st.subheader(f":blue[{Total_count}]")
                
                colu1, colu2 = st.columns(2)
                
                with colu1:
                    st.write("Total payment value")
                    Total_amount = aggre_transaction_totaltransactionamount(Aggre_transaction,YEAR,QUARTER)
                    st.subheader(f":blue[{Total_amount}]")
                
                with colu2:
                    st.write("Avg. transaction value")
                    Total_average = aggre_transaction_avgtransactionamount(Aggre_transaction,YEAR,QUARTER)
                    st.subheader(f":blue[{Total_average}]")
                
                st.markdown('<hr>', unsafe_allow_html=True)
                st.subheader("Categories")
                aggre_transaction_transactiontypecount(Aggre_transaction,YEAR,QUARTER)

                st.markdown('<hr>', unsafe_allow_html=True)
                TAB1,TAB2,TAB3=st.tabs(['States','Districts','Postal Codes'])
                with TAB1:
                    st.subheader("Top 10 States")
                    aggre_transaction_topstatetransactioncount(Aggre_transaction,YEAR,QUARTER)
                with TAB2:
                    st.subheader("Top 10 Districts")
                    map_transaction_topdistricttransactioncount(Map_transaction,YEAR,QUARTER)
                with TAB3:
                    st.subheader("Top 10 Postal Codes")
                    Top_transaction_toppincodestransactioncount(Top_transaction,YEAR,QUARTER)
            with Col1:
                if Trans=="Transaction_amount":
                    st.header(f":violet[PhonePe Transactions Amount Q {QUARTER}-{YEAR}]")
                    aggre_transaction_geotransactionamount(Aggre_transaction,YEAR,QUARTER)
                    aggre_transaction_transactionamount(Aggre_transaction,YEAR,QUARTER)
                elif Trans=="Transaction_count":
                    st.header(f":violet[PhonePe Transactions Count Q {QUARTER}-{YEAR}]")
                    aggre_transaction_geotransactioncount(Aggre_transaction,YEAR,QUARTER)
                    aggre_transaction_transactioncount(Aggre_transaction,YEAR,QUARTER)
            
                
            State_Selected,Year_Selected, Quarter_Selected,Transactions = st.columns(4)
            with State_Selected:
                States=st.selectbox("Select a State", Map_transaction['States'].unique())
            
            with Year_Selected:
                Years = st.selectbox("Select a Year", Map_transaction['Years'].unique())

            with Quarter_Selected:
                Quarters = st.selectbox("Select a Quarter", Map_transaction['Quarter'].unique())

            with Transactions:
                transaction_Options =['Transaction_count', 'Transaction_amount']
                Transactions= st.selectbox("select a transaction",transaction_Options)

                    
            COLUMN1,COLUMN2=st.columns([4,5])

            with COLUMN1:
                if Transactions=="Transaction_count":
                    st.subheader(f":violet[PhonePe Transactions Counts {States} Q {Quarters}-{Years}]")
                    map_transaction_geotransactioncount(Map_transaction,Years,Quarters,States)
                elif Transactions=="Transaction_amount":
                    st.subheader(f":violet[PhonePe Transactions Amounts {States} Q {Quarters}-{Years}]")
                    map_transaction_geotransactionamount(Map_transaction,Years,Quarters,States)
                

            with COLUMN2:
                if Transactions=="Transaction_count":
                    map_transaction_transactioncount(Map_transaction,States,Years,Quarters)
                elif Transactions=="Transaction_amount":
                    map_transaction_transactionamount(Map_transaction,States,Years,Quarters)
        elif check =="USER":
            Ct1,Ct2=st.columns([8,4])
        
            with Ct2:
                YEAR_SELECTED, QUARTER_SELECTED,Metrics = st.columns(3)

                with YEAR_SELECTED:
                    Year_select = st.selectbox("Select a year", Map_user['Years'].unique())

                with QUARTER_SELECTED:
                    Quarter_select = st.selectbox("Select a quarter", Map_user['Quarter'].unique())
                
                with Metrics:
                    metrics=["RegisteredUser","AppOpens"]
                    Metric=st.selectbox("select a metric",metrics)
                st.header(":blue[Users]")
                st.write(f"Registered PhonePe users till Q{Quarter_select} {Year_select}")
                registed_users = map_user_RegisteredUserscount(Map_user,Year_select,Quarter_select)
                st.subheader(f":blue[{registed_users}]")
                
                st.write(f"PhonePe app opens in Q{Quarter_select} {Year_select}")
                app_opens=map_user_AppOpenscount(Map_user,Year_select,Quarter_select)
                st.subheader(f":blue[{app_opens}]")
                
                st.markdown('<hr>', unsafe_allow_html=True)
                TABB1,TABB2,TABB3=st.tabs(['States','Districts','Postal Codes'])
                with TABB1:
                    st.subheader("Top 10 States")
                    aggre_user_topstatetransactioncount(Map_user,Year_select,Quarter_select)
                with TABB2:
                    st.subheader("Top 10 Districts")
                    map_user_topdistricttransactioncount(Map_user,Year_select,Quarter_select)
                with TABB3:
                    st.subheader("Top 10 Postal Codes")
                    Top_user_toppincodestransactioncount(Top_user,Year_select,Quarter_select)
            with Ct1:
                if Metric=="RegisteredUser":
                    st.header(f":violet[Registered PhonePe users Q {Quarter_select}-{Year_select}]")
                    map_user_geoRegisteredUser(Map_user,Year_select,Quarter_select)
                    map_user_allRegisteredUser(Map_user,Year_select,Quarter_select)
                elif Metric=="AppOpens":
                    st.header(f":violet[PhonePe AppOpens Q {Quarter_select}-{Year_select}]")
                    map_user_geoAppOpens(Map_user,Year_select,Quarter_select)
                    map_user_allAppOpens(Map_user,Year_select,Quarter_select)
            STATES_Selected,YEARS_Selected, QUARTERS_Selected,Method = st.columns(4)
            with STATES_Selected:
                STATES=st.selectbox("Select a State", Map_user['States'].unique())
        
            with YEARS_Selected:
                YEARS = st.selectbox("Select a Year", Map_user['Years'].unique())

            with QUARTERS_Selected:
                QUARTERS = st.selectbox("Select a Quarter", Map_user['Quarter'].unique())

            with Method:
                method_options=["Brands and Transaction Count","RegisteredUser AppOpens"]
                method=st.selectbox("select a method",method_options)

            if method=="Brands and Transaction Count":
                st.subheader(f"Brands and Transaction Count Q {QUARTERS} {YEARS}")
                aggre_user_individualtransactioncount(Aggre_user,STATES,YEARS,QUARTERS)
            elif method=="RegisteredUser AppOpens":
                st.subheader(f"RegisteredUser AppOpens Q {QUARTERS} {YEARS}")
                map_user_plot_1(Map_user,YEARS,QUARTERS,STATES)
            
    elif options == "INSURANCE":

        cl1,cl2=st.columns([8,4])
        
        with cl2:
            year_selected, quarter_selected,Transaction_Selected = st.columns(3)

            with year_selected:
                year = st.selectbox("Select a year", Aggre_insurance['Years'].unique())

            with quarter_selected:
                quarter = st.selectbox("Select a quarter", Aggre_insurance['Quarter'].unique())
            with Transaction_Selected:
                transact=["Transaction_Count","Transaction_Amount"]
                Transact=st.selectbox("select a transaction",transact)
            st.header(":blue[Insurance]")
            st.write("*All India Insurance Policies Purchased (Nos.)*")
            total_count = aggre_insurance_totaltransactioncount(Aggre_insurance, year, quarter)
            st.subheader(f":blue[{total_count}]")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("Total premium value")
                total_amount = aggre_insurance_totaltransactionamount(Aggre_insurance, year, quarter)
                st.subheader(f":blue[{total_amount}]")
            
            with col2:
                st.write("Average premium value")
                total_average = aggre_insurance_avgtransactionamount(Aggre_insurance, year, quarter)
                st.subheader(f":blue[{total_average}]")

            st.markdown('<hr>', unsafe_allow_html=True)
            Tab1,Tab2,Tab3=st.tabs(['States','Districts','Postal Codes'])
            with Tab1:
                st.subheader("Top 10 States")
                aggre_insurance_topstatetransactioncount(Aggre_insurance,year,quarter)
            with Tab2:
                st.subheader("Top 10 Districts")
                map_insurance_topdistricttransactioncount(Map_insurance,year,quarter)
            with Tab3:
                st.subheader("Top 10 Postal Codes")
                Top_insurance_toppincodetransactioncount(Top_insurance,year,quarter)
        with cl1:
            if Transact=="Transaction_Count":
                st.header(f":violet[PhonePe Transactions Count Q {quarter}-{year}]")
                aggre_insurance_geotransactioncount(Aggre_insurance,year,quarter)
                aggre_insurance_transactioncount(Aggre_insurance,year,quarter)
            elif Transact=="Transaction_Amount":
                st.header(f":violet[PhonePe Transactions Amount Q {quarter}-{year}]")
                aggre_insurance_geotransactionamount(Aggre_insurance,year,quarter)
                aggre_insurance_transactionamount(Aggre_insurance,year,quarter)

        
        States_selected,Years_selected, Quarters_selected,Transaction = st.columns(4)
        with States_selected:
            State=st.selectbox("Select a State", Map_insurance['States'].unique())
        
        with Years_selected:
            Year = st.selectbox("Select a Year", Map_insurance['Years'].unique())

        with Quarters_selected:
            Quarter = st.selectbox("Select a Quarter", Map_insurance['Quarter'].unique())

        with Transaction:
            Transaction_options =['Transaction_count', 'Transaction_amount']
            Transaction= st.selectbox("select a transaction",Transaction_options)

                
        Column1,Column2=st.columns([4,5])

        with Column1:
            if Transaction=="Transaction_count":
                st.subheader(f":violet[PhonePe Transactions Counts {State} Q {Quarter}-{Year}]")
                map_insurance_geotransactioncount(Map_insurance,Year,Quarter,State)
            elif Transaction=="Transaction_amount":
                st.subheader(f":violet[PhonePe Transactions Amounts {State} Q {Quarter}-{Year}]")
                map_insurance_geotransactionamount(Map_insurance,Year,Quarter,State)

        with Column2:
            if Transaction=="Transaction_count":
                map_insurance_transactioncount(Map_insurance,State,Year,Quarter)
            elif Transaction=="Transaction_amount":
                map_insurance_transactionamount(Map_insurance,State,Year,Quarter)

with tab4:
    question=st.selectbox('select a Question',["1.Overall Transaction Amount and Count of the States Transaction",
                                               "2.Overall Transaction Amount and Count of the Districts Transaction",
                                               "3.Overall Transaction Amount and Count of the Postal Codes Transaction",
                                               "4.Overall Transaction Amount and Count of the States Insurance",
                                               "5.Overall Transaction Amount and Count of the Districts Insurance",
                                               "6.Overall Transaction Amount and Count of the Postal Codes Insurance",
                                               "7.Overall Transaction Count of States User",
                                               "8.Registered users of Districts User",
                                               "9.App opens of Districts User",
                                               "10.Registered users of States User"])  

    if question=="1.Overall Transaction Amount and Count of the States Transaction":
        st.header("States Transaction Amount")
        visual_statetransactionamount(Aggre_transaction)
        visual_totalstatetransactionamount(Aggre_transaction)

        st.header("States Transaction Count")
        visual_statetransactioncount(Aggre_transaction)
        visual_totalstatetransactioncount(Aggre_transaction)

        
    elif question=="2.Overall Transaction Amount and Count of the Districts Transaction":
        st.header('Districts Transaction Amount')
        Select_State = st.selectbox('Select a State',options=Map_transaction['States'].unique(),key="select_state_widget")
        visual_districtstransactionamount(Map_transaction, Select_State)

        
        st.header('Districts Transaction Count')
        visual_districtstransactioncount(Map_transaction,Select_State)
        

    elif question=="3.Overall Transaction Amount and Count of the Postal Codes Transaction":
        st.header('Postal Codes Transaction Amount')
        Choose_State=st.selectbox('Select a State',options=Top_transaction['States'].unique(),key="select_state_widget")
        visual_pincodestransactionamount(Top_transaction,Choose_State)
        

        st.header('Postal Codes Transaction Count')
        visual_pincodestransactioncount(Top_transaction,Choose_State)
        
    elif question=="4.Overall Transaction Amount and Count of the States Insurance":
        st.header("States Transaction Amount")
        visual_statetransactionamount(Aggre_insurance)
        visual_totalstatetransactionamount(Aggre_insurance)

        st.header("States Transaction Count")
        visual_statetransactioncount(Aggre_insurance)
        visual_totalstatetransactioncount(Aggre_insurance)

    elif question=="5.Overall Transaction Amount and Count of the Districts Insurance":
        st.header('Districts Transaction Amount')
        Select_state = st.selectbox('Select a State',options=Map_insurance['States'].unique(),key="select_state_widget")
        visual_districtstransactionamount(Map_insurance,Select_state)
        
        st.header('Districts Transaction Count')
        visual_districtstransactioncount(Map_insurance,Select_state)
        

    elif question=="6.Overall Transaction Amount and Count of the Postal Codes Insurance":
        st.header('Postal Codes Transaction Amount')
        choose_state=st.selectbox('select a state',options=Top_insurance['States'].unique(),key="select_state_widget")
        visual_pincodestransactionamount(Top_insurance,choose_state)
        

        st.header('Postal Codes Transaction Count')
        visual_pincodestransactioncount(Top_insurance,choose_state)
        
    elif question=="7.Overall Transaction Count of States User":
        st.header('States Transaction Count')
        visual_statetransactioncountu(Aggre_user)
        visual_totalstatetransactioncountu(Aggre_user)

    elif question=="8.Registered users of Districts User":
        st.header('District Registered users')
        Select_states = st.selectbox('Select a State',options=Map_user['States'].unique(),key="select_state_widget")
        visual_districtsRegisteredUser(Map_user,Select_states)


    elif question=="9.App opens of Districts User":
        st.header('District App opens')
        select_states = st.selectbox('Select a State',options=Map_user['States'].unique(),key="select_state_widget")
        visual_districtsAppOpens(Map_user,select_states)

    elif question=="10.Registered users of States User":
        st.header("States Registered users")
        visual_statesRegisteredUser(Top_user)
    






    
