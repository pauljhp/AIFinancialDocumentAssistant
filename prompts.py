prompt_pay="""You are an intelligent critical analyst doing a gender pay gap analysis of the company {}.
Your task is to thoroughly assess the 2022 Sustainability and  Annual reports of the company mentioned, which is {}.
List out all the statistics related to gender pay gap analysis for this company and the goals mentioned relevant to reaching a certain pay gap percentage. Include any relevant specific facts, figures, and names of the programs and initiatives from text and tables, along with supporting facts.
Return EVERYTHING you can find about the company's commitment to talent development for women. Present several sentences worth of answers and each should be in a bullet point.
The following key words should help you search for relevant text when formulating the answer: pay gap, pay equity for women, fair compensation, dollar-for-dollar, pay gap report.
the following is a fictional sample answer (FOR YOUR FORMATTING REFERENCE ONLY.):
-  X has have dollar-for-dollar, 100% pay equity for women compared to men in every country where they operate.
- For every dollar a male employee is paid, a female employee is paid 99.4 cents
- female employees earn more than 99 cents for every dollar earned by similarly situated male employees
- Women earned 99.8 cents for every dollar that men earned performing the same jobs
- X conducted gender pay gap analysis across our global operations
- X is committed to pay equity and we regularly review and adapt compensation when needed to ensure fair and equitable pay practices
- X conducted an enterprise-wide gender pay gap analysis in 2021, which did not identify any gender pay gaps in respect of like-for-like roles.
- There is no gender or regional gap in the same qualification grade
- -0.7% gender pay gap
- 65.5% wage gap between male and female
- 81.2% difference between male and female average salaries
- Each year X produces a Gender Pay Gap Report, showing the difference between the average hourly pay for men and women across all ages, roles and levels of the business.
 
""".format(company_name, company_name)