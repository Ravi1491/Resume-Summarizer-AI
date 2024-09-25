def match_job_description_prompt(file_name, ai_text, job_description):
  prompt = f"""
    As an experienced HR professional and technical recruiter, your task is to evaluate how well a candidate's resume matches a given job description. Follow these steps:

    1. Carefully analyze the job description, noting key requirements, skills, and qualifications.
    2. Thoroughly examine the resume text, identifying relevant experiences, skills, and achievements.
    3. Compare the resume against the job description, considering the following factors:
       - Technical skills match
       - Relevant work experience
       - Educational background
       - Soft skills and personal attributes
       - Industry-specific knowledge
       - Project experience relevance
       - Years of experience (if specified)

    4. Calculate a percentage match based on how well the resume fulfills the job requirements.
    5. Provide a brief explanation for your percentage, highlighting key matches and any significant gaps.

    Return a JSON object with exactly three fields:
    - "file_name": The name of the resume file
    - "percentage": The calculated match percentage (0-100)
    - "explanation": A concise explanation for the given percentage

    Rules:
    - The JSON object must be properly formatted and enclosed in curly braces.
    - Do not return any text outside of the JSON object.
    - If the job description is empty or contains irrelevant text, assign a 0% match with an appropriate explanation.
    - Be objective and fair in your assessment, considering both explicit and implicit matches.

    Input details:
    Job description: {job_description}
    File name: {file_name}
    Resume text: {ai_text}

    Respond only with the JSON object.
    """
    
  return prompt 

def parsed_resume_prompt(resume_text):
  prompt = f"""As an experienced Software Developer and Resume Analyst, your task is to create a structured summary of the given resume. Follow these guidelines:

1. Carefully analyze the provided resume text.
2. Summarize the content into the following sections:
   - Personal_Information: Full name, contact details, location, etc.
   - Objective: Career goals or professional summary (if present)
   - Work_Experience: List of jobs with company names, titles, dates, and key responsibilities/achievements
   - Education: Degrees, institutions, graduation dates, and relevant coursework
   - Skills: Technical skills, programming languages, tools, and frameworks
   - Projects: Notable projects with brief descriptions and technologies used
   - Certifications: Professional certifications with dates (if any)
   - Hobbies: Personal interests or extracurricular activities (if mentioned)
   - Languages: Language proficiencies (if specified)
   - References: Any reference information (if provided)

3. Format the summary as a JSON object with these sections as keys.
4. If a section is not present in the resume, include the key with an empty list or null value.
5. For Work_Experience and Education, provide details in chronological order (most recent first).
6. Ensure all dates are formatted consistently (e.g., YYYY-MM or MM/YYYY).
7. Limit each section to essential information, focusing on relevance and clarity.

Rules:
- Provide only the JSON object in your response, with no additional text.
- Ensure the JSON is properly formatted and valid.
- Use consistent formatting for lists and nested objects within the JSON structure.
- Do not infer or add information not present in the original resume text.

Resume text to analyze:
{resume_text}

Respond only with the JSON object containing the structured resume summary.
"""
  
  return prompt
