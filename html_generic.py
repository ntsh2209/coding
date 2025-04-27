import pandas as pd
import base64

html_content = custom_table_style  # your earlier defined styles
toc_html = "<h1 style='text-align:center;'>Table of Contents</h1><ul style='list-style-type:none;'>"
full_body_html = ""
exhibit_counter = 1

for section_idx, section in enumerate(sections, start=1):
    section_anchor = f"section-{section_idx}"

    # Add Section link to TOC
    toc_html += f"<li><a href='#{section_anchor}' style='text-decoration:none; font-size:18px; color:#003366;'>{section['section_title']}</a><ul style='list-style-type:none; margin-left:20px;'>"

    section_body = f"<h1 id='{section_anchor}' style='text-align:center; color:#003366; margin-top:40px;'>{section['section_title']}</h1><br>"

    for exhibit in section["exhibits"]:
        exhibit_anchor = f"exhibit-{exhibit_counter}"

        # Add Exhibit link to TOC
        toc_html += f"<li><a href='#{exhibit_anchor}' style='text-decoration:none; color:#555;'>{exhibit_counter}. {exhibit['title']}</a></li>"

        # Add Exhibit to body
        section_body += f"<h2 id='{exhibit_anchor}' style='text-align:center;'>Exhibit {exhibit_counter}: {exhibit['title']}</h2>"

        if exhibit["type"] == "table":
            df = pd.read_csv(exhibit["source"])
            html_table = df.to_html(index=False, classes="custom-table", border=0)
            section_body += html_table
        elif exhibit["type"] == "plot":
            with open(exhibit["source"], "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode()
            section_body += f'<div style="text-align:center;"><img src="data:image/png;base64,{img_base64}" style="width:600px;"></div><br><br>'

        # Add Description if available
        if "description" in exhibit:
            section_body += f"<p style='text-align:center; font-size:12px; font-style:italic; color:#888; margin-top:5px; margin-bottom:20px;'>{exhibit['description']}</p><br>"

        exhibit_counter += 1

    toc_html += "</ul></li>"  # Close exhibits list under section
    full_body_html += section_body

toc_html += "</ul><br><hr style='border:1px solid #ccc;'><br>"  # Close TOC list and add separator

# Final HTML
html_content += toc_html + full_body_html
