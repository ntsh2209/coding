from jinja2 import Environment, FileSystemLoader
import pandas as pd
import os

def generate_html_report(output_path, basic_stats, jumps_df, delta_stats, delta_rows_df):
    # Save styled tables to HTML fragments
    stats_df = pd.DataFrame.from_dict(basic_stats, orient='index', columns=['value'])
    stats_html = stats_df.to_html(classes='table table-striped', escape=False)

    jumps_html = jumps_df.to_html(classes='table table-bordered', index=False)
    delta_rows_html = delta_rows_df.to_html(classes='table table-bordered', index=False)

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(searchpath="./"))
    template = env.get_template("template.html")

    html_out = template.render(
        stats_html=stats_html,
        jumps_html=jumps_html,
        delta_stats=delta_stats,
        delta_rows_html=delta_rows_html
    )

    with open(output_path, "w") as f:
        f.write(html_out)
    print(f"✅ Report written to: {output_path}")
