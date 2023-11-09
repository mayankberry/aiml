import base64
import pickle
from django.shortcuts import render, redirect
from django.http import HttpResponse
import pandas as pd
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from io import BytesIO
from .forms import CsvUploadForm


def base(request):
    return render(request, 'index.html')

def fileupload(request):
    if request.method == 'POST':
        form = CsvUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                file = form.cleaned_data['file']
                

                df = pd.read_csv(file, delimiter=',', encoding='utf-8', skiprows=0, header=0)
                df.dropna(axis=0,inplace=True)

                df_base64 = base64.b64encode(pickle.dumps(df)).decode('utf-8')
                request.session['df'] = df_base64
                return redirect('column_select')
            except Exception as e:

                return HttpResponse(f'Error: {str(e)}')
    else:
        form = CsvUploadForm()

    return render(request, 'file_upload.html', {'form': form})

def column_select(request):
    df_base64 = request.session.get('df', '') 
    df = pickle.loads(base64.b64decode(df_base64))

    columns = df.columns
    if request.method == 'POST':
        selected_columns = request.POST.getlist('columns')
        if len(selected_columns) != 2:
            return HttpResponse('Please select exactly 2 columns.')
        request.session['selected_columns'] = selected_columns

        return redirect('predictions')

    context = {
        'columns': columns
    }

    return render(request, 'selection.html', context)


def predictions(request):
    df_base64 = request.session.get('df', '') 
    df = pickle.loads(base64.b64decode(df_base64))

    columns = df.columns
    count = df.shape[1]

    selected_columns = request.session.get('selected_columns', None)

    if selected_columns is None:
        return HttpResponse("No columns Selected")

    x = selected_columns[0]
    y = selected_columns[1]

# Boxplot

    fig1, ax1 = plt.subplots(figsize=(12, 6))
    sns.boxplot(data=df, x=x, y=y)
    plt.title(f"Box Plot of {x} vs {y}")
    plt.xlabel(x)
    plt.ylabel(y)
    plt.xticks(rotation=90)
    
    buf1 = BytesIO()
    canvas1 = FigureCanvasAgg(fig1)
    canvas1.print_png(buf1)
    
    image_base64_1 = base64.b64encode(buf1.getvalue()).decode('utf-8')
    plt.close(fig1)

# Bar Chart of x

    fig2, ax2 = plt.subplots(figsize=(8, 6))
    df[x].value_counts().plot(kind='bar')
    plt.title(f"{x} counts representation")
    plt.xlabel(x)
    plt.ylabel('Count')
    plt.xticks(rotation=45)

    buf2 = BytesIO()
    canvas2 = FigureCanvasAgg(fig2)
    canvas2.print_png(buf2)
    
    image_base64_2 = base64.b64encode(buf2.getvalue()).decode('utf-8')
    plt.close(fig2)

# Bar chart of y

    fig3, ax3 = plt.subplots(figsize=(8, 6))
    df[y].value_counts().plot(kind='bar')
    plt.title(f"Bar Chart of : {y}")
    plt.xlabel(x)
    plt.ylabel('Count')
    plt.xticks(rotation=45)

    buf3 = BytesIO()
    canvas3 = FigureCanvasAgg(fig3)
    canvas3.print_png(buf3)

    image_base64_3 = base64.b64encode(buf3.getvalue()).decode('utf-8')
    plt.close(fig3)

# Scatter plot
    er = None
    image_base64_4 = None
    if x in df.columns and y in df.columns:
        x_col = df[x].astype(float)
        y_col = df[y].astype(float)

        if len(x) == len(y):

            fig4, ax4 = plt.subplots(figsize=(12,6))
            plt.scatter(x_col, y_col)
            plt.title(f"Scatter Plot of {x_col} vs {y_col}")
            plt.xlabel(x_col)
            plt.ylabel(y_col)
    
            buf4 = BytesIO()
            canvas4 = FigureCanvasAgg(fig4)
            canvas4.print_png(buf4)
            image_base64_4 = base64.b64encode(buf4.getvalue()).decode('utf-8')
            plt.close(fig4)
        else:
            er = "Scatter Plot Can't be generated as the columns are not of the same length"
            print("Error Not of same length")

# lineplot

    fig5, ax5 = plt.subplots(figsize=(12,6))
    sns.lineplot(data=df, x=x, y=y)
    plt.title(f"Line plot of : {x} vs {y}")
    plt.xlabel(x)
    plt.ylabel(y)

    buf5 = BytesIO()
    canvas5 = FigureCanvasAgg(fig5)
    canvas5.print_png(buf5)

    image_base64_5 = base64.b64encode(buf5.getvalue()).decode('utf-8')
    plt.close(fig5)

# piechart

    fig6, ax6 = plt.subplots(figsize=(8, 6))
    col = df[x].value_counts()
    plt.pie(col, labels=col.index, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title(f"{x} counts representation in Pie Chart")
    buf6 = BytesIO()
    canvas6 = FigureCanvasAgg(fig6)
    canvas6.print_png(buf6)

    image_base64_6 = base64.b64encode(buf6.getvalue()).decode('utf-8')
    plt.close(fig6)


    context = {
        'image_base64_1': image_base64_1, 
        'image_base64_2': image_base64_2,
        'image_base64_3': image_base64_3,
        'image_base64_4': image_base64_4,
        'image_base64_5': image_base64_5,
        'image_base64_6': image_base64_6,
        'columns' : columns,
        'er' : er,
        'x' : x,
        'y' : y,

    }

    return render(request, 'predictions.html', context)



