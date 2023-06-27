from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


url = 'https://vnexpress.net'

def get_title(url):
    # Gửi yêu cầu HTTP đến trang web

    response = requests.get(url)

    # Lấy HTML của trang web
    html = response.text

    # Phân tích HTML bằng BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Tìm tất cả các thẻ h3 chứa tiêu đề trên trang
    titles = soup.find_all('h3')

    titles_list = []
    for title in titles:
        titles_list.append(title.text)
    titles_list = [s.replace('\n', '') for s in titles_list]
    for i in range(len(titles_list)):
        titles_list[i] = titles_list[i].strip()
    return titles_list

def get_link_by_title(title, url):
    # Gửi yêu cầu HTTP đến trang web

    response = requests.get(url)

    # Lấy HTML của trang web
    html = response.text

    # Phân tích HTML bằng BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Tìm tất cả các thẻ a chứa tiêu đề trên trang
    links = soup.find_all('a', {'title': title})

    # Kiểm tra xem có tìm thấy liên kết không
    if len(links) == 0:
        print('Không tìm thấy liên kết cho tiêu đề này')
    else:
        # Trả về liên kết đầu tiên tìm được
        return links[0]['href']
    
def get_content(url):

    # Lấy nội dung của trang web
    response = requests.get(url)
    html_content = response.content

    # Phân tích cú pháp HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    # Lấy phần tử p  cí class description
    description =soup.find(['p'], class_= 'description')
    # Lấy tất cả các phần tử p và figure có class là Normal
    normal_elements = soup.find_all(['p', 'figure'], class_='Normal')

    # In ra nội dung của các phần tử đó
    content = []
    if description:
        content.append(description.text.strip())
    for i in normal_elements:
        content.append(i.text.strip())
    return content

title = get_title(url)[0]
content = get_content(get_link_by_title(title, url))

def write_newspaper_to_pdf(articles):
    filename = "newspaper.pdf"
    doc = canvas.Canvas(filename, pagesize=letter)

    font_name = "Arial"  
    font_size = 14

    font_path = "C:\\Users\\Admin\\Downloads\\arial-unicode-ms.ttf"  
    pdfmetrics.registerFont(TTFont(font_name, font_path))

    first_page = True  

    for article in articles:
        label = article["label"]
        content = article["content"]

        if not first_page:
            doc.showPage()  


        doc.setFont(font_name, font_size)

        y = letter[1] - inch


        label_lines = []
        words = label.split(' ')
        current_line = ''
        for word in words:
            if doc.stringWidth(current_line + word) < letter[0] - 2 * inch:
                current_line += word + ' '
            else:
                label_lines.append(current_line.strip())
                current_line = word + ' '
        label_lines.append(current_line.strip())

        for line in label_lines:
            doc.drawString(inch, y, line)
            y -= font_size + 2
        y -= 0.5 * inch

        doc.setFont(font_name, 12)

        lines = []
        for line in content:
            words = line.split(' ')
            current_line = ''
            for word in words:
                if doc.stringWidth(current_line + word) < letter[0] - 2 * inch:
                    current_line += word + ' '
                else:
                    lines.append(current_line.strip())
                    current_line = word + ' '
            lines.append(current_line)
        for line in lines:
            if y <= 0.5 * inch:
                doc.showPage() 
                doc.setFont(font_name, 12)  
                y = letter[1] - 2 * inch - font_size - 2
            doc.drawString(inch, y, line)
            y -= font_size + 2

        first_page = False  
    doc.save()
N = 5
articles =[]
for i in range(N):
    label = get_title(url)[i]
    content = get_content(get_link_by_title(title, url))
    article = {
        "label": label,
        "content": content
    }
    articles.append(article)

write_newspaper_to_pdf(articles)
