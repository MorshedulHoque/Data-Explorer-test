from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import plotly.express as px

app = Flask(__name__)

# Global variable to store DataFrame
uploaded_dataframe = None

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global uploaded_dataframe

    if request.method == 'POST':
        # Get the uploaded file
        file = request.files['file']

        # Check if the file is valid
        if file and file.filename.endswith('.csv'):
            # Read the CSV file into a Pandas DataFrame
            uploaded_dataframe = pd.read_csv(file)

            # Redirect to the chart configuration page
            return redirect(url_for('configure_chart'))

    return render_template('upload.html')

@app.route('/configure_chart', methods=['GET', 'POST'])
def configure_chart():
    global uploaded_dataframe

    if uploaded_dataframe is None:
        # Redirect to the upload page if no DataFrame is available
        return redirect(url_for('upload_file'))

    if request.method == 'POST':
        # Get the selected columns for X and Y axes
        selected_x_column = request.form['x_column']
        selected_y_column = request.form['y_column']

        # Create a bar chart using Plotly Express
        fig = px.bar(uploaded_dataframe, x=selected_x_column, y=selected_y_column, title='Bar Chart')

        # Convert the Plotly figure to JSON for rendering in the template
        chart_json = fig.to_json()

        # Provide a list of available columns for selection
        columns = list(uploaded_dataframe.columns)

        # Render the chart template with the chart JSON and selected columns
        return render_template('chart.html', chart_json=chart_json, selected_x_column=selected_x_column, selected_y_column=selected_y_column, columns=columns, uploaded_dataframe=uploaded_dataframe.head())

    # Provide a list of available columns for selection
    columns = list(uploaded_dataframe.columns)

    # Render the chart template without the chart JSON
    return render_template('chart.html', columns=columns, uploaded_dataframe=uploaded_dataframe.head())

if __name__ == '__main__':
    app.run(debug=True)
