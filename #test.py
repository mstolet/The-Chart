import pandas as pd
from flask import Flask, render_template, request
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from pyvis.network import Network
import networkx as nx
import pandas as pd
import os

app = Flask(__name__)

# define credentials for Google Sheets API
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("C:\\Users\\marin\\Downloads\\jupyter\\The Chart\\the-chart-383719-a6b18eb7d9fa.json", scope)
client = gspread.authorize(creds)
sheet = client.open('Sheet1').sheet1

def create_network_chart():
    df = pd.DataFrame(sheet.get_all_records())
    G = nx.from_pandas_edgelist(df, source='Name', target='Lover', edge_attr='Relationship')
    net1 = Network('500px', '1300px')
    net1.from_nx(G)
    # Set edge labels
    edge_labels = {(edge[0], edge[1]): str(G.get_edge_data(edge[0], edge[1])['Relationship']) for edge in G.edges}
    net1.set_edge_smooth('dynamic')
    net1.show_buttons(filter_=['physics'])
    net1.edges = net1.edges or []
    for e in net1.edges:
        e["title"] = edge_labels.get((e["from"], e["to"]), "")
    net1.save_graph("chart.html")
    with open("chart.html", "r") as f:
        chart_html = f.read()
    os.remove("chart.html")
    return chart_html

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        lover = request.form['lover']
        relationship = request.form['relationship']
        row = [name, lover, relationship]
        sheet.append_row(row)

    # Define the dropdown menu options
    relationship_options = ["Kissed", "Fucked", "Exes", "Ex friends", "Dating"]
    # Generate the HTML code for the dropdown menu
    dropdown_html = '<select id="relationship" name="relationship">'
    for option in relationship_options:
        dropdown_html += '<option value="{}">{}</option>'.format(option, option)
    dropdown_html += '</select>'

    chart_html = create_network_chart()

    # Copy the contents of index.html and assign it to a variable
    html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>The Chart Brasília</title>
        </head>
        <body>
            <div style="text-align:center;">
                <h1>The Chart Brasília</h1>
                <h2>Pau no cu do rebuceteio</h2>
                <form method="POST" action="/">
                    <label for="name">Name:</label>
                    <input type="text" id="name" name="name">
                    <label for="lover">Lover:</label>
                    <input type="text" id="lover" name="lover">
                    <label for="relationship">Relationship:</label>
                    {}
                    <button type="submit">Add Relationship</button>
                </form>
                <br>
                <div>
                    {}
                </div>
            </div>
        </body>
        </html>
    """.format(dropdown_html, chart_html)

    # Replace the return statement with the HTML contents
    return html_content

if __name__ == '__main__':
    app.run(debug=True)
