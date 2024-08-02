def match_job_description_prompt(file_name, ai_text, job_description):
  prompt = f"""
    As an Interviwer, Your task is to determine how well a resume matches a given job description. First understand the Job description and then understand the resume text. After understanding both the requirement. As an Interviwer you will give the response.

    Calculate the percentage of the resume that matches the job description.
    Return a JSON object with exactly three fields: "file_name", "percentage", and "explanation".
    The JSON object must be properly formatted and enclosed in curly braces.
    Do not return any extra text outside of the JSON object.
    If Job description is empty or any random irrelvent text, then in this case give 0% with proper explanation
    Input details:

    Job description: {job_description}
    File name: {file_name}
    Resume text: {ai_text}
    
    In Return only return the JSON.
  """
        
  return prompt 

def parsed_resume_prompt(resume_text):
  prompt = f"""You are Experience Software Developer. You will have to make summary of resumes section wise.
    Your role is to summarize the resume in a way that it is easy to read and understand.
    Divide the summary in following sections:
    1. Personal_Information
    2. Objective
    3. Work Experience
    4. Education
    5. Skills
    6. Projects
    7. Certifications
    8. Hobbies
    9. Languages
    10. References

    If some section is missing, you can skip that section.
    Only give the response in JSON format.
    Don't give any text outside the JSON. Only provide JSON. 
    Even Don't include Here is the summary of the resume in JSON format: 
    Here is the text from the resume: {resume_text}"""

  return prompt
