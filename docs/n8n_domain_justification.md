# Graded Task 2 Domain Justification

Student hostel planning benefits from the Tool Use Pattern because hostel room costs, nearby university areas, and inter-city transport prices are real-world values that change over time.
An LLM cannot reliably know current local room rent or travel cost from training data alone.
Tool use lets the n8n workflow fetch or simulate those facts, inject the results into the LLM context, and return a grounded hostel plan.
