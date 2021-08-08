#IMPORT PUSTAKA
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import altair as alt
import pandas as pd

app = dash.Dash(__name__, assets_folder='assets')
app.config['suppress_callback_exceptions'] = True

server = app.server
app.title = 'Analisa Penjualan Supermarket Dashboard'

# DATA LOADING

df = pd.read_csv('supermarket_sales - Sheet1.csv')


#Buat Fungsi Diagram Heat
def make_heat_map(branch_index, func, plot_title):
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    times = ['Morning', 'Afternoon', 'Evening']
    
    heat_map = (alt
                .Chart(df)
                .mark_rect()
                .encode(alt.X('Day_of_week:N', title=None, sort=days),
                        alt.Y('Time_of_day:N', title=None, sort=times),
                        alt.Color(func, type = 'quantitative' ,title=None, scale=alt.Scale(scheme='OrangeRed')),
                        tooltip=[alt.Tooltip(func, type='quantitative', title=plot_title, format=',.0f')])
                .configure_axisX(labelAngle=70)
                .transform_filter(alt.FieldEqualPredicate(field='Branch', equal= branch_index))
                .configure_axis(labelFontSize=30, titleFontSize=30)
                .configure_title(fontSize=30)
                .properties(width=300, height=250, title=plot_title)
    )   
    return heat_map

#fungsi untuk total sales    
def make_total_sales(branch_index='A'):
    
    total_sales = make_heat_map(branch_index, 'sum(Total)', 'Total Sales')

    return total_sales

#fungsi untuk customer traffic
def make_customer_traffic(branch_index='A'):
  
    customer_traffic = make_heat_map(branch_index, 'count(Invoice ID)', 'Customer Traffic')

    return customer_traffic

#fungsi untuk transaksi size
def make_transaction_size(branch_index='A'):
   
    transaction_size = make_heat_map(branch_index, 'mean(Total)', 'Average Transaction Size')

    return transaction_size

#fungsi untuk rating
def make_customer_satisfaction(branch_index='A'):
   
    customer_satisfaction = make_heat_map(branch_index, 'mean(Rating)', 'Average Customer Satisfaction')

    return customer_satisfaction

#Fungsi untuk grafik bar
def make_bar_plot(day_of_week, time_of_day, branch_index, func, plot_title, y_title):
  
    bar_plot = (alt
                .Chart(df)
                .mark_bar(color = 'OrangeRed')
                .encode(alt.X('Product line:N', title=None),
                        alt.Y(func, type='quantitative', title=y_title),
                        tooltip=[alt.Tooltip('Product line', title='Product line'),
                                alt.Tooltip(func, title=plot_title)])
                .transform_filter(alt.FieldEqualPredicate(field='Branch', equal=branch_index))
                .transform_filter(alt.FieldEqualPredicate(field='Day_of_week', equal=day_of_week))
                .transform_filter(alt.FieldEqualPredicate(field='Time_of_day', equal=time_of_day))
                .properties(width=220, height=175, title= plot_title)
    )
    return bar_plot

def con_plt(day_of_week='Monday', time_of_day='Morning', branch_index='A'):
   
    bar_plot_sales = make_bar_plot(day_of_week, time_of_day, branch_index, 'sum(Total)', 'Total Sales', 'Sales in ($)')
    bar_plot_traffic = make_bar_plot(day_of_week,time_of_day, branch_index, 'count(Invoice ID)', 'Customer Traffic', 'Transactions')
    bar_plot_trans = make_bar_plot(day_of_week, time_of_day, branch_index, 'mean(Total)', 'Average Transaction Size', 'Sales in ($)')
    bar_plot_rating = make_bar_plot(day_of_week, time_of_day, branch_index, 'mean(Rating)', 'Average Customer Satisfaction', 'Rating')
    
    return (alt.concat(bar_plot_sales, bar_plot_traffic, bar_plot_trans, bar_plot_rating, columns=4)
                .configure_axis(labelFontSize=13, titleFontSize=13)
                .configure_title(fontSize=14)
                .configure_axisX(labelAngle=45)
            )

#Header Judul Penjelasan
app.layout = html.Div([
    html.Div([ 
        html.H1(
            children = 'Analisa Penjualan Supermarket',
            className="header-title",
                ),

        dcc.Markdown(['''
                Milestone 1 FTDS Batch 001 submission oleh [sutisna](https://github.com/sutasaa)
                    '''], className="header-author",
                    ),

        dcc.Markdown(['''
                o Download dataset [disini](https://www.kaggle.com/aungpyaeap/supermarket-sales).
                    '''], className="header-description",
                    ),
        
        html.Label(['Pilih Kota (Tempat toko berada):'],className="header-description",),

        # Arrange radio buttoms to select branch
        dcc.RadioItems(
            id='Store',
            options=[
                {'label': 'Yangon', 'value': 'A'},
                {'label': 'Mandalay', 'value': 'B'},
                {'label': 'Naypyitaw', 'value': 'C'}
            ],
            value='A'),
    ], className="header",
    ),

  #Akan dibagi menjadi 3 Tab
  #Tab 1 untuk Store Performance Summary per Kota
  #Tab 2 untuk Perbadingan Performance Setiap Kota Per Lini Produk
  #Tab 3 untuk hypothesis
    dcc.Tabs(id='tabs', children=[
        # The first tab 
        dcc.Tab(label='Performance Summary', className="header-tab", children=[
            html.Div(children = [
                html.Div([
                    html.H3('**Objective:**'),

                    dcc.Markdown('''
                    Kita ingin mengidentifikasi hari dan waktu dalam seminggu di mana toko mungkin kelebihan/kekurangan pegawai.
                    
                    **Note**: *Morning* adalah 9:00-12:59, *Afternoon* adalah 13:00-16:59 dan *Evening* adalah 17:00-20:59. 
                    ''')
                    ], style = {'backgroundColor': 'Bisque', 'font-size' : '20px', 'border-width' : '3px'}
                ),

                dbc.Row([
                    # total sales heat map
                    html.Iframe(sandbox='allow-scripts',
                                id='total_sales',
                                height='500',
                                width='570',
                                style={'border-width': '4px'},
                                srcDoc=make_total_sales().to_html()
                    ),
                                
                    # customer traffic heat map
                    html.Iframe(sandbox='allow-scripts',
                                id='customer_traffic',
                                height='500',
                                width='570',
                                style={'border-width': '4px'},
                                srcDoc=make_customer_traffic().to_html()
                    ),
                                
                    # average transaction size heat map
                    html.Iframe(sandbox='allow-scripts',
                                id='transaction_size',
                                height='500',
                                width='570',
                                style={'border-width': '4px'},
                                srcDoc=make_transaction_size().to_html()
                    ),
                                
                    # customer satisfaction heat map
                    html.Iframe(sandbox='allow-scripts',
                                id='customer_satisfaction',
                                height='500',
                                width='570',
                                style={'border-width': '4px'},
                                srcDoc=make_customer_satisfaction().to_html()
                    )
                ]),
            ], className='container'), 
        ]),

        # the second tab
        dcc.Tab(label='Performance by Product Line', className="header-tab", children=[
            html.Div(children = [
                html.Div([
                    html.H3('**Objective:**'),

                    dcc.Markdown('''
                    Kita ingin mengidentifikasi hari dan waktu dalam seminggu di mana toko mungkin kelebihan/kekurangan pegawai per bagian lini produk.  
                    ''')
                ], style = {'backgroundColor': 'Bisque', 'font-size' : '20px', 'border-width' : '3px'}),

            
                html.H3('''Pilih shift pertama untuk membandingkan:'''),
            
                html.Div([
                    # dropdown menu untuk memilih day of week
                    html.Label('Day of week:'),

                    dcc.Dropdown(
                        id='day_of_week',
                        options=[{'label': i, 'value': i} for i in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']]
                        value='Monday',
                        style={'width': '60%'}),
            
                    html.Label('Time of day:'),
            
                    # dropdown menu untuk memilih time of day
                    dcc.Dropdown(
                        id='time_of_day',
                        options=[{'label': i, 'value': i} for i in df['Time_of_day'].unique()],
                        value='Morning',
                        style={'width': '60%'})
                ], style={'columnCount': 2}),

                # bar plots
                html.Iframe(
                    sandbox='allow-scripts',
                    id='bar_plots',
                    height='400',
                    width='1500',
                    style={'border-width': '4px'},
                    srcDoc=con_plt().to_html()
                ),

                html.H3('''Pilih shift kedua untuk membandingkan:'''),

                html.Div([
                    # dropdown menu untuk memilih day of week
                    html.Label('Day of week:'),

                    dcc.Dropdown(
                        id='day_of_week2',
                        options=[{'label': i, 'value': i} for i in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']]
                        value='Monday',
                        style={'width': '60%'}),
            
                    html.Label('Time of day:'),
            
                    # dropdown menu untuk memilih time of day
                    dcc.Dropdown(
                        id='time_of_day2',
                        options=[{'label': i, 'value': i} for i in df['Time_of_day'].unique()],
                        value='Morning',
                        style={'width': '60%'})
                ], style={'columnCount': 2}),

                # bar plots
                html.Iframe(
                    sandbox='allow-scripts',
                    id='bar_plots2',
                    height='400',
                    width='1500',
                    style={'border-width': '4px'},
                    srcDoc=con_plt().to_html()
                ),    
            ], className='container'),
        ]),

        # the third tab
        dcc.Tab(label='Hypothesis', className="header-tab", children=[
            html.Div(children = [
                html.Div([
                    html.H1('Student t-test dan Mann-Whitney'),

                    dcc.Markdown(['''
                    ### Objective: 
                      
                    Dalam analisa hypothesis testing kita ingin menguji apakah ada perbedaan nilai rata-rata gross income untuk saat weekday dan weekend?
                    
                    sehingga kita dapat menyatakan Hypothesis sebagai berikut.
                
                    - Hypothesis Null (H0) adalah  𝜇1=𝜇2 , Tidak ada perbedaan antara nilai rata-rata gross income untuk Weekday dan Weekend
                    - Hypothesis alternatif (H1) adalah 𝜇1≠𝜇2,  Ada perbedaan antara nilai rata-rata gross income untuk Weekday dan Weekend

                    ### Metode

                    Kita akan menggunakan student t-test

                    ### Hypothesis Testing

                    nilai p adalah: 0.190, Kita dapatkan hasilnya adalah H0 diterima, yang berarti nilai rata-rata gross income pada weekday dan weekend adalah sama.

                    Kita lupa seharusnya sebelum melakukan t-test asumsi penting yang harus dijalankan untuk test kita adalah, apakah sampel test kita berdistribusi normal? kita akan melakukan shapiro test.
                    
                    ### Shapiro-Wilk test
                    '''],
                    className = "mb-5 mt-5",),

                    html.Img(src="/assets/img/shapiro.png"),

                    dcc.Markdown(['''
                    
                    Untuk weekend di dapatkan nilai p = 0.00 dan weekday nilai p = 0.00, kita dapatkan hasilnya adalah reject null hypothesis berarti reject hypothesis dari observasi adalah berdistribusi normal. sehingga t-test kita tidak valid. 
                    
                    Kita seharusnya melakukan test Man-Whitney.

                    ### Man-Whitney test

                    kita dapatkan p value adalah 0.0503 berarti H0 diterima, dengan kata lain nilai rata-rata gross income di hari weekday dan weekend adalah sama (kali ini dengan test yang tepat).
                    '''],
                    className = "mb-5 mt-5",),

                    html.H1('ANNOVA'),

                    dcc.Markdown(['''
                    ### Objective:

                    kita akan melakukan test kembali untuk gross income terhadap 3 kategori branch (city), kali ini t-test atau Man-Whitney test tidak bisa dilakukan. 
                    
                    ### Metode

                    kita akan lakukan test ANNOVA. dimana asumsinya harus berdistribusi normal.

                    ### Hypothesis Testing
                     
                    Kita dapatkan nilai p-value adalah 0.949 berarti  H0 diterima, atau dengan kata lain tidak ada perbedaan rata-rata gross income untuk ke-3 cabang kota. 
                    
                    '''],
                    className = "mb-5 mt-5",),

                    html.Img(src="/assets/img/annova.png"),

                    html.H1('Kesimpulan'),

                    dcc.Markdown(['''
                    Dari Hypothesis diatas dapat disimpulan bahwa:

                    1. Nilai rata-rata gross income yang dihasilkan saat weekday dan saat income adalah sama.

                    2. Nilai rata-rata gross income dari ketiga cabang toko (kota) adalah sama
                    '''],
                    className = "mb-5 mt-5",),
                ], style = {'backgroundColor': 'Bisque', 'border-width': '0px'}),
            ], className='container'),
        ]),
    ]),       
])

@app.callback(
    [Output('total_sales', 'srcDoc'),
     Output('customer_traffic', 'srcDoc'),
     Output('transaction_size', 'srcDoc'),
     Output('customer_satisfaction','srcDoc')],
     [dash.dependencies.Input('Store', 'value')])

def update_plot(branch_index):

    updated_total_sales = make_total_sales(branch_index).to_html()
    updated_customer_traffic = make_customer_traffic(branch_index).to_html()
    updated_transaction_size= make_transaction_size(branch_index).to_html()
    updated_customer_satisfaction = make_customer_satisfaction(branch_index).to_html()

    return updated_total_sales, updated_customer_traffic, updated_transaction_size, updated_customer_satisfaction

@app.callback(
    dash.dependencies.Output('bar_plots', 'srcDoc'),
    [dash.dependencies.Input('day_of_week', 'value'),
     dash.dependencies.Input('time_of_day', 'value'),
     dash.dependencies.Input('Store', 'value')])

def update_plot(day_of_week, time_of_day, branch_index):
 
    bar_plots = con_plt(day_of_week, time_of_day, branch_index).to_html()
    return bar_plots

@app.callback(
    dash.dependencies.Output('bar_plots2', 'srcDoc'),
    [dash.dependencies.Input('day_of_week2', 'value'),
     dash.dependencies.Input('time_of_day2', 'value'),
     dash.dependencies.Input('Store', 'value')])

def update_plot(day_of_week, time_of_day, branch_index):
 
    bar_plots = con_plt(day_of_week, time_of_day, branch_index).to_html()
    return bar_plots

if __name__ == '__main__':
    app.run_server(debug=True)