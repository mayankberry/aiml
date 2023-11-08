import base64
from django.shortcuts import render, redirect
from django.http import HttpResponse
import pandas as pd
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from io import BytesIO

def base(request):
    return render(request, 'base.html')


def data():
    df = pd.read_csv('static/waterPollution.csv')
    return df

def column_select(request):
    df = data()

    columns = df.columns
    if request.method == 'POST':
        selected_columns = request.POST.getlist('columns')
        if len(selected_columns) != 2:
            return HttpResponse('Please select exactly 2 columns.')
        request.session['selected_columns'] = selected_columns
        print(selected_columns[0])
        print('this', selected_columns[1])
        return redirect('predictions')

    context = {
        'columns' : columns
    }

    return render(request, 'selection.html', context)


def predictions(request):
    df = data()

    columns = df.columns
    count = df.shape[1]

    selected_columns = request.session.get('selected_columns', None)

    if selected_columns is None:
        return HttpResponse("No columns Selected")

    x = selected_columns[0]
    y = selected_columns[1]

    fig1, ax1 = plt.subplots(figsize=(12, 6))
    sns.boxplot(data=df, x=x, y=y)
    plt.title(f"{x} vs {y}")
    plt.xlabel(x)
    plt.ylabel(y)
    plt.xticks(rotation=90)
    
    buf1 = BytesIO()
    canvas1 = FigureCanvasAgg(fig1)
    canvas1.print_png(buf1)
    
    image_base64_1 = base64.b64encode(buf1.getvalue()).decode('utf-8')
    
    plt.close(fig1)

    fig2, ax2 = plt.subplots(figsize=(8, 6))
    df['parameterWaterBodyCategory'].value_counts().plot(kind='bar')
    plt.title('Water Body Categories')
    plt.xlabel('Category')
    plt.ylabel('Count')
    plt.xticks(rotation=45)

    buf2 = BytesIO()
    canvas2 = FigureCanvasAgg(fig2)
    canvas2.print_png(buf2)
    
    image_base64_2 = base64.b64encode(buf2.getvalue()).decode('utf-8')
    
    plt.close(fig2)

    context = {
        'image_base64_1': image_base64_1, 
        'image_base64_2': image_base64_2,
        'columns' : columns,

    }

    return render(request, 'predictions.html', context)



