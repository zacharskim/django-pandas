import base64
import io
import pandas as pd
import plotly.express as px
from django.http import JsonResponse
from rest_framework.decorators import api_view
from plotApp.serializers import CSVInputSerializer
from django.shortcuts import render
import openai
import asyncio
import functools
import json
import plotly
from decouple import config

openai.api_key = config('OPENAI_API_KEY')

#use gpt3.5 turbo model to generate some plot meta data to use in plotly
async def getPlotObj(csv_file):
    loop = asyncio.get_event_loop()
    func = functools.partial(openai.ChatCompletion.create, model="gpt-3.5-turbo", messages=[{"role": "system", "content": "You are a helpful ai plot generator. You will be given the head of a datatable and should determine a useful graph that can be made from the data using plotly. Your response should be like: {'plot_type': 'bar', 'x': 'column_name', 'y': 'column_name', 'title': 'Bar plot of Column A and Column B'}. Feel free to make time series, bar plots, or anything you see fit but make sure that the plot_type is a valid plotly plot type. Only respond with one plot per input, the response should only be a single dictionary. Nothing more than a dictionary, no additional text please."}, {"role": "user", "content": csv_file},])
    res = await loop.run_in_executor(None, func)
 
    return json.loads(res['choices'][0]['message']['content'].replace("'", "\""))

def index(request):
    return render(request, 'plotApp/index.html')


#post csv file to this endpoint
@api_view(['POST'])
def process_csv(request):
    serializer = CSVInputSerializer(data=request.data)
    if serializer.is_valid():
        csv_file = serializer.validated_data['file']
        df = pd.read_csv(csv_file)
        
        plotObj = asyncio.run(getPlotObj(df.head(n=5).to_csv()))

        fig = create_plot_from_response(plotObj, df)

        plot_data = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return JsonResponse({'plot_data': plot_data})
    
    else:
        return JsonResponse(serializer.errors, status=400)

#create ploty plot from plotObj
def create_plot_from_response(plotObj, df):
    try:
        plot_type, title = plotObj['plot_type'], plotObj['title']

        if plot_type == 'histogram':
            fig = px.histogram(df, x=plotObj['x'])
            fig.update_layout(title=title)
        elif plot_type == 'bar':
            fig = px.bar(df, x=plotObj['x'], y=plotObj['y'])
            fig.update_layout(title=title)
        elif plot_type == 'scatter':
            fig = px.scatter(df, x=plotObj['x'], y=plotObj['y'])
            fig.update_layout(title=title)
        elif plot_type == 'line':
            fig = px.line(df, x=plotObj['x'], y=plotObj['y'])
            fig.update_layout(title=title)
        else:
            
            raise ValueError(f"Invalid plot type: {plot_type}")

        return fig

    except Exception as e:
        print(f"Error creating plot: {e}")
        return None