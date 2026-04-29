# In Python shell or test file:
from models import QueryRequest, DiagnosticResponse, EvidenceChunk
q = QueryRequest(query="What does city mean?", age=45, sex="Male")
print(q)  # Should print QueryRequest(query='test', age=45, ...)