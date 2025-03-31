from flask import Flask, render_template_string
import pandas as pd

app = Flask(__name__)

df = pd.DataFrame({
    "Stock": ["AAPL", "GOOGL", "MSFT"],
    "Daily Price": [150, 2800, 300],
    "Volatility": [1.2, 1.8, 1.5],
    "Volume": [5000000, 3000000, 4000000]
})

@app.route("/")
def home():
    return render_template_string("""
    <html>
    <head>
        <link rel="stylesheet" 
              href="https://cdn.datatables.net/1.10.21/css/jquery.dataTables.min.css">
    </head>
    <body>
        <table id="stock_table" class="display">
            <thead>
                <tr>{{ df.columns.to_list() | join('</th><th>') }}</th></tr>
            </thead>
            <tbody>
                {% for row in df.values.tolist() %}
                    <tr>{{ row | join('</td><td>') }}</td></tr>
                {% endfor %}
            </tbody>
        </table>
        <script src="https://code.jquery.com/jquery-3.5.1.js"></script>
        <script src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.min.js"></script>
        <script>
            $(document).ready(function() {
                $('#stock_table').DataTable();
            });
        </script>
    </body>
    </html>
    """, df=df)

if __name__ == "__main__":
    app.run(debug=True)
