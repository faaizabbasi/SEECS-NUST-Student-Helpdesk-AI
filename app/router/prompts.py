from langchain_core.prompts import ChatPromptTemplate

ROUTER_PROMPT = ChatPromptTemplate.from_template("""
Classify the query into exactly one of these intents:

- document_qa: any question that could be answered by looking something up in
  SEECS/NUST handbooks or course documents — policies, rules, CGPA/grading,
  attendance, thesis, deadlines, fees, course codes/titles/descriptions,
  prerequisites, forms, procedures, eligibility, etc.
- help_request: the user wants to submit, file, or draft a form/request/complaint
  (e.g. elective change, deadline extension, transcript correction).
- general_chat: greetings, thanks, or questions about the assistant itself —
  nothing that requires looking anything up.

Examples:
Query: What percentage of attendance is required for the End Semester Exam?
Intent: document_qa

Query: What courses are available on Antennas and Wave Propagation?
Intent: document_qa

Query: Is there a course on Computer Vision, and what's its code?
Intent: document_qa

Query: What's the minimum CGPA to avoid probation?
Intent: document_qa

Query: I want to add an elective and drop another one, can you help me submit that?
Intent: help_request

Query: My transcript has an error, help me file a complaint.
Intent: help_request

Query: Hi, how are you?
Intent: general_chat

Query: What can you help me with?
Intent: general_chat

Rule: If the query mentions a specific policy, number, course, deadline, form,
or anything that sounds like it could be looked up in a document, choose
document_qa — even if you already think you know the answer. Only choose
general_chat when there is clearly nothing to look up. When unsure between
document_qa and general_chat, choose document_qa.

Query: {query}
""")
