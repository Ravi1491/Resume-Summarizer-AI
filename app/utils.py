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
  
def resume_template(data):
    html = f'''
    <body style="font-family: Calibri, sans-serif; line-height: 1.75; color: #333; margin: 0; padding: 20px;">
        <header style="text-align: center; margin-bottom: 20px;">
            <h1 style="font-size: 24px; margin-bottom: 5px; margin: 0;">{data['personnal_info']['name']}</h1>
            <div style="font-size: 14px;">
                <span>{data['personnal_info']['email']}</span> • <span>{data['personnal_info']['phone']}</span> •
                <span>{data['personnal_info']['linkedin']}</span> •
                <span>{data['personnal_info']['github']}</span>
            </div>
        </header>

        <div style="margin-bottom: 15px;">
            <h2 style="font-size: 18px; border-bottom: 1px solid #333; margin-bottom: 10px; margin: 0;">
                EXPERIENCE
            </h2>
            <div style="margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: baseline;">
                    <h3 style="font-size: 16px; margin: 0;">Software Developer Engineer</h3>
                    <span style="font-style: italic;">January 2023 - Present</span>
                </div>
                <div style="font-weight: bold;">Glue Labs Private Limited</div>
                <ul style="margin: 5px 0; padding-left: 20px;">
                    <li>
                        Architected AI-Driven Backend Infrastructure: Led development of
                        backend systems with NodeJs and NestJs, defining API flows, database
                        schemas, and implementing robust security for scalability and
                        performance.
                    </li>
                    <li>
                        Event-Driven Architecture with KafkaJS: Integrated KafkaJS to enable
                        real-time data processing and seamless communication between
                        microservices, resulting in significant improvements in real-time
                        data handling.
                    </li>
                    <li>
                        Role-Based Access Control (RBAC): Established RBAC mechanisms to
                        bolster data security, reducing access-related incidents by 40%.
                    </li>
                    <li>
                        Analytics Server: Developed an analytics server in Flask to process
                        Shopify store data, using ClickHouse for high-performance storage
                        and querying. Improving data processing speeds by 50%.
                    </li>
                    <li>
                        CRM and Workflow Automation: Integrated CRM and automated email
                        workflows for Shopify customers, boosting engagement and efficiency.
                    </li>
                    <li>
                        Front-End Development: Created features using NextJs for user
                        onboarding, Shopify interfaces, and workflow management, ensuring
                        seamless user experiences.
                    </li>
                </ul>
            </div>
            <div style="margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: baseline;">
                    <h3 style="font-size: 16px; margin: 0;">Software Developer Engineer Intern</h3>
                    <span style="font-style: italic;">March 2022 - December 2022</span>
                </div>
                <div style="font-weight: bold;">Glue Labs Private Limited</div>
                <ul style="margin: 5px 0; padding-left: 20px;">
                    <li>
                        Caching with Redis: Utilized Redis and its sorted set to achieve
                        significant reductions in latency around 60-70% for both the
                        product's feed and user profiles.
                    </li>
                    <li>
                        API Services: Defined REST APIs services with Swagger and Graphql
                        APIs integration for both internal and external services.
                    </li>
                    <li>
                        Enhanced Search Capabilities: Implemented MeiliSearch to build
                        complex search API's. Integrated account deletion and blocking
                        features in a people engaging platform designed for meetings,
                        knowledge sharing, and podcasts.
                    </li>
                    <li>
                        Database Management: Used Sequelize and TypeORM for efficient
                        database management and reliable data flows.
                    </li>
                    <li>
                        Optimized Backend Infrastructure: Engineered and optimized backend
                        systems using Node.js (Express.js, Nest.js), TypeScript, PostgreSQL
                        and TimescaleDB, ensuring robust and efficient web applications.
                    </li>
                </ul>
            </div>
        </div>

        <div style="margin-bottom: 15px;">
            <h2 style="font-size: 18px; border-bottom: 1px solid #333; margin-bottom: 10px; margin: 0;">
                PROJECTS
            </h2>
            <div style="margin-bottom: 10px;">
                <h3 style="font-size: 16px; margin: 0;">
                    Vexio (Shopify Product Review Management)
                </h3>
                <div>github.com/Ravi1491/Vexio</div>
                <ul style="margin: 5px 0; padding-left: 20px;">
                    <li>
                        Vexio is a powerful Shopify App designed to simplify and enhance
                        your product review management process. With it, you can
                        effortlessly collect and manage customer reviews for your Shopify
                        store products.
                    </li>
                    <li>
                        Engineered a robust automation system using NodeJs, Sequelize,
                        PostgreSQL, and webhooks within Vexio, automatically dispatching
                        review emails to customers post-purchase, fostering engagement and
                        insights
                    </li>
                </ul>
            </div>
            <div style="margin-bottom: 10px;">
                <h3 style="font-size: 16px; margin: 0;">Resume Summarizer AI</h3>
                <div>github.com/Ravi1491/Resume-Summarizer-AI</div>
                <ul style="margin: 5px 0; padding-left: 20px;">
                    <li>
                        Leveraging the AI capabilities of the Groq service, the application
                        generates concise and relevant summaries of the extracted resume
                        text.
                    </li>
                    <li>
                        Users can easily upload their PDF resumes. The application employs
                        the pdfminer3 library to accurately extract text from these PDFs and
                        are stored in an SQLite database.
                    </li>
                    <li>
                        Users can compare their resumes with job descriptions to identify
                        key matches and gaps, helping them tailor their applications
                        effectively.
                    </li>
                </ul>
            </div>
        </div>

        <div style="margin-bottom: 15px;">
            <h2 style="font-size: 18px; border-bottom: 1px solid #333; margin-bottom: 10px; margin: 0;">
                SKILLS
            </h2>
            <p style="margin: 5px 0;">
                NodeJs, Express, NestJS, JavaScript, TypeScript, Python, ReactJS,
                NextJS, Timescale DB, PostgreSQL, MongoDB, Clickhouse, Docker, Redis,
                KafkaJs, AWS, Postman, Cloudinary, Sequelize ORM, TypeORM, HTML, MJML,
                Flask, Fast API, REST APIs, GraphQL
            </p>
        </div>

        <div style="margin-bottom: 15px;">
            <h2 style="font-size: 18px; border-bottom: 1px solid #333; margin-bottom: 10px; margin: 0;">
                EDUCATION
            </h2>
            <h3 style="font-size: 16px; margin: 0;">
                Bachelor of Technology in Computer Science
            </h3>
            <div>Bennett University • Greater Noida • 2023 • 8.94</div>
        </div>
    </body>
    </html>
      '''
    return html