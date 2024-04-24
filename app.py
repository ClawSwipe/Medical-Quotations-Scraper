from flask import Flask, render_template, request, send_file
from bs4 import BeautifulSoup
import csv
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'html_file' not in request.files:
        return "No file part"
    
    html_file = request.files['html_file']
    
    if html_file.filename == '':
        return "No selected file"
    
    if html_file:
        filename = html_file.filename
        output_filename = os.path.splitext(filename)[0] + '_output.csv'

        html_content = html_file.read()
        
        # Create a BeautifulSoup object with the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        headings = soup.find_all("tr", class_="heading")

        # Generate CSV file
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Code', 'Item Name', 'Trader', 'Offer', 'Bonus', 'T.P'])
            for i, heading in enumerate(headings):
                heading_name = heading.find('td').text.strip()
                next_heading = headings[i + 1] if i + 1 < len(headings) else None
                items = heading.find_next_siblings('tr', class_='item')
                for item in items:
                    snum = item.find('td', align='center').text.strip()
                    item_name = item.find("td", style=" text-align: left;").text.strip()
                    w = item_name.split()
                    percentage_index = next((i for i, x in enumerate(w) if x.endswith('%')), None)            
                    if percentage_index is not None:
                        if w[-1].endswith('%'):
                            offer = w[-1]  
                            tp = w[-2]     
                            item_name = ' '.join(w[:-2])  
                            bonus = ''  
                        else:
                            offer = w[percentage_index]
                            bonus = ' '.join(w[percentage_index+1:])
                            tp = w[percentage_index-1]
                            item_name = ' '.join(w[:percentage_index-1])
                    else:
                        try:
                            offer = item.find_all("td", align="center")[2].text.strip()
                        except IndexError:
                            offer = ""
                        try:
                            bonus = item.find_all("td", align="center")[3].text.strip()
                        except IndexError:
                            bonus = ""
                        try:
                            tp = item.find_all("td", align="center")[4].text.strip()
                        except IndexError:
                            tp = ""
                    csv_writer.writerow([snum, item_name, heading_name, offer, bonus, tp])
                    if next_heading is not None and item.find_next_sibling('tr') == next_heading:
                        break

        # Serve the generated CSV file for download
        return send_file(output_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
