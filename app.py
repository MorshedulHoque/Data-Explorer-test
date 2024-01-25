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

    # Default values for variables
    chart_json = None
    selected_x_column = None
    selected_y_column = None
    chart_type = None
    data_types_df = None
    describe_df = None
    unique_values_df = None

    if request.method == 'POST':
        # Get the selected columns for X and Y axes
        selected_x_column = request.form['x_column']
        selected_y_column = request.form['y_column']
        chart_type = request.form['chart_type']

        # Create the selected chart type using Plotly Express
        if chart_type == 'bar':
            fig = px.bar(uploaded_dataframe, x=selected_x_column, y=selected_y_column, title='Bar Chart')
        elif chart_type == 'scatter':
            fig = px.scatter(uploaded_dataframe, x=selected_x_column, y=selected_y_column, title='Scatter Plot')

        # Convert the Plotly figure to JSON for rendering in the template
        chart_json = fig.to_json()

        # Calculate additional descriptive statistics for each column
        numeric_dataframe = uploaded_dataframe.select_dtypes(include=['int64', 'float64'])
        describe_df = numeric_dataframe.describe(include='all').transpose()

        # Round float values to 2 decimal places
        describe_df = describe_df.round(2)

        # Calculate unique values for object columns
        object_columns = uploaded_dataframe.select_dtypes(include='object').columns
        unique_values_data = []
        if not object_columns.empty:  # Check if there are object columns
            for column in object_columns:
                unique_values_data.append({
                    'Column': column,
                    'Unique Values': uploaded_dataframe[column].nunique(),
                    'Top Value': uploaded_dataframe[column].mode().iloc[0],
                    'Frequency': uploaded_dataframe[column].value_counts().iloc[0]
                })

            unique_values_df = pd.DataFrame(unique_values_data)

    # Get data types information into a DataFrame
    if uploaded_dataframe is not None:
        column_info = uploaded_dataframe.dtypes
        missing_values_info = uploaded_dataframe.isnull().sum()
        missing_percentage = ((uploaded_dataframe.isnull().sum() / len(uploaded_dataframe)) * 100).round()

        data_types_df = pd.DataFrame({
            'Column': column_info.index,
            'Data Type': column_info.values,
            'Missing Values': missing_values_info.values,
            'Missing Values (%)' : missing_percentage.values
        })
        # Convert 'Missing Values (%)' column to integer before adding the percentage sign
        data_types_df['Missing Values (%)'] = data_types_df['Missing Values (%)'].astype(int).astype(str) + '%'

        # Provide a list of available columns for selection
        columns = list(uploaded_dataframe.columns)

    # Render the chart template with the chart JSON and selected columns
    return render_template('chart.html', chart_json=chart_json, selected_x_column=selected_x_column, 
                           selected_y_column=selected_y_column, columns=columns, uploaded_dataframe=uploaded_dataframe,
                           chart_type=chart_type, data_types_df=data_types_df, describe_df=describe_df,
                           unique_values_df=unique_values_df)

if __name__ == '__main__':
    app.run(debug=True)
