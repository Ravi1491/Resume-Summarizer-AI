import io
from pdfminer3.layout import LAParams
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer3.converter import TextConverter
from groq import Groq
from flask import current_app

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def get_resume_pdf_text(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()

    converter.close()
    fake_file_handle.close()
    return text

def groq_response(prompt):
    client = Groq(api_key=current_app.config['GROQ_API_KEY'])
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-70b-8192",
    )
    
    return chat_completion.choices[0].message.content

def match_job_description(file_name, ai_text, job_description):
    client = Groq(api_key=current_app.config['GROQ_API_KEY'])
    
    prompt = f"""
            Your task is to determine how well a resume matches a given job description.

            Calculate the percentage of the resume that matches the job description.
            Return a JSON object with exactly three fields: "file_name", "percentage", and "explanation".
            The JSON object must be properly formatted and enclosed in curly braces.
            Do not return any extra text outside of the JSON object.
            Input details:

            Job description: {job_description}
            File name: {file_name}
            Resume text: {ai_text}
            
            In Return only return the JSON.
        """
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-70b-8192",
    )
    return chat_completion.choices[0].message.content

def dict_to_html_table(data):
    html = '''
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
            margin: auto;
            font-size: 18px;
            text-align: left;
        }
        th, td {
            padding: 12px;
            border: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #f1f1f1;
        }
        .nested-table {
            width: 100%;
            margin: 10px 0;
        }
    </style>
    <table>
    '''
    for key, value in data.items():
        if isinstance(value, dict):
            html += f'<tr><th colspan="2">{key}</th></tr>'
            for sub_key, sub_value in value.items():
                html += f'<tr><td>{sub_key}</td><td>{sub_value}</td></tr>'
        elif isinstance(value, list):
            html += f'<tr><th colspan="2">{key}</th></tr>'
            for item in value:
                if isinstance(item, dict):
                    html += '<tr><td colspan="2"><table class="nested-table">'
                    for sub_key, sub_value in item.items():
                        if isinstance(sub_value, list):
                            html += f'<tr><td>{sub_key}</td><td>{"<br>".join(sub_value)}</td></tr>'
                        else:
                            html += f'<tr><td>{sub_key}</td><td>{sub_value}</td></tr>'
                    html += '</table></td></tr>'
                else:
                    html += f'<tr><td colspan="2">{item}</td></tr>'
        else:
            html += f'<tr><td>{key}</td><td>{value}</td></tr>'
    html += '</table>'
    return html
  