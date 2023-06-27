from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
import openai
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from PIL import Image
from io import BytesIO
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from fpdf import FPDF


req = requests.get('https://vnexpress.net/')
soup = BeautifulSoup(req.content, "html.parser")
openai.api_key = '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'
model_engine = "text-davinci-003"

N = 10
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

prompt = "Please summarize and extract the important content in the text in Vietnamese with a summary of no more than 40 words"  #có thể thực hiện giới hạn từ ở đây
def summarize_gpt3(text):
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt + f"/n{text}/n/Summary:",
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    summarization = response.choices[0].text.strip()
    return summarization

def page(request):
    context= {'heading1': list_title[0], 
              'heading2': list_title[1], 
              'heading3': list_title[2], 
              'heading4': list_title[3], 
              'heading5': list_title[4],  
              'heading6': list_title[5],  
              'heading7': list_title[6],  
              'heading8': list_title[7],  
              'heading9': list_title[8],  
              'heading10': list_title[9]}  
    return render(request,'news.html', context)


list_title=get_title(url)

def test(request):
    #next = request.GET('next','')
    choose = []
    for i in range(N):
        choose.append(0)

    s1 =  request.POST.get('select1')
    if s1 == "on":
        choose[0] = 1

    s2 =  request.POST.get('select2')
    if s2 == "on":
        choose[1] = 1

    s3 =  request.POST.get('select3')
    if s3 == "on":
        choose[2] = 1

    s4 =  request.POST.get('select4')
    if s4 == "on":
        choose[3] = 1
    s5 =  request.POST.get('select5')
    if s5 == "on":
        choose[4] = 1
    s6 =  request.POST.get('select6')
    if s6 == "on":
        choose[5] = 1
    s7 =  request.POST.get('select7')
    if s7 == "on":
        choose[6] = 1
    s8 =  request.POST.get('select8')
    if s8 == "on":
        choose[7] = 1
    s9 =  request.POST.get('select9')
    if s9 == "on":
        choose[8] = 1


    submit = request.POST.get('submit')

    #viet=trans(viet)
    #print (viet)

    #englist = preprocessing(eng)
    #vietlist= preprocessing(viet)
    
    #result = 0.5 * simiS(englist,vietlist) + 0.5 * simiR(englist,vietlist) 
    #context= {'engsenten': preprocessing(eng), 'vietsenten': preprocessing(viet), 'submit': submit, 'result': result}
    #print ("result: ",choose)
    print ("Loading.....")
    articles = []
    for i in range(N):
        if choose[i] == 1:
            content_line = get_content(get_link_by_title(list_title[i],url))
            content = ""
            for line in content_line:
                content += line + " "
            summarization= []
            for line in content_line:
                summarization.append(summarize_gpt3(line))
            article= {
                "label" :list_title[i],
                "content": summarization
                #"content": get_content(get_link_by_title(list_title[i],url))
            }
            articles.append(article)
    
    pdf = canvas.Canvas("News.pdf")   
    pdf.setFont("Helvetica", 12)   
    write_newspaper_to_pdf(articles)
    #write_pdf(articles)
    #print(articles)
    print ("Success")
    return page(request)
    #return 0

def write_newspaper_to_pdf(articles):
    filename = "News.pdf"
    doc = canvas.Canvas(filename, pagesize=letter)

    font_name = "Arial"  
    font_size = 14

    font_path = "C:\\Users\\Admin\\Downloads\\arial-unicode-ms.ttf"  
    pdfmetrics.registerFont(TTFont(font_name, font_path))

    first_page = True  
    #doc.setFont(font_name, font_size)

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
def get_home(request):
    return render(request,'news.html')


"""
#0. run XAMPP
#1. cd mysite
#2. python manage.py migrate
#3. python manage.py runserver 8888
"""

