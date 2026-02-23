from crewai import Task

from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from tools import search_tool, FinancialDocumentTool


# FIX: description was telling agent to make up answers, hallucinate URLs, ignore the query
# FIX: was assigned to wrong agent — all tasks were pointing to financial_analyst only
verification = Task(
    description=(
        "Read the financial document at the provided file path and verify it is a legitimate "
        "financial document. Check for the presence of standard financial sections such as: "
        "balance sheet, income statement, cash flow statement, or financial ratios. "
        "User query: {query}. File path: {file_path}. "
        "Clearly state whether this is a valid financial document and summarize what type it is."
    ),
    expected_output=(
        "A clear verification report stating: "
        "1. Whether the document is a valid financial document (Yes/No) "
        "2. The type of financial document (annual report, balance sheet, etc.) "
        "3. The company name and reporting period if found "
        "4. Any issues or concerns with the document format or content"
    ),
    agent=verifier,                                    # FIX: was financial_analyst
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)


# FIX: description told agent to make things up and ignore the query
analyze_financial_document = Task(
    description=(
        "Using the verified financial document at {file_path}, perform a comprehensive financial analysis "
        "to address the user's query: {query}. "
        "Extract and analyze key financial metrics including revenue, profit margins, debt ratios, "
        "liquidity ratios, and year-over-year growth. "
        "Base your entire analysis strictly on the data present in the document. "
        "Do not fabricate any figures or reference external sources not in the document."
    ),
    expected_output=(
        "A structured financial analysis report containing: "
        "1. Executive summary answering the user's query "
        "2. Key financial metrics and ratios extracted from the document "
        "3. Year-over-year trends if multiple periods are available "
        "4. Strengths and weaknesses identified from the financial data "
        "5. All figures cited directly from the document"
    ),
    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
    context=[verification]                             # FIX: depends on verification completing first
)


# FIX: was making up investment products, recommending crypto, ignoring the document
investment_analysis = Task(
    description=(
        "Based on the financial analysis of the document at {file_path}, provide balanced investment insights "
        "relevant to the user's query: {query}. "
        "Your recommendations must be grounded in the actual financial data — revenue trends, profitability, "
        "debt levels, and growth metrics. "
        "Clearly state that these are informational insights and not personalized investment advice. "
        "Do not recommend specific products or make up market data."
    ),
    expected_output=(
        "A balanced investment insights report containing: "
        "1. Summary of the company's financial health based on document data "
        "2. Key investment considerations (both positive and negative) backed by document figures "
        "3. Relevant financial ratios and what they indicate "
        "4. A clear disclaimer that this is informational analysis, not personalized financial advice"
    ),
    agent=investment_advisor,                          # FIX: was financial_analyst
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
    context=[analyze_financial_document]               # FIX: depends on analysis completing first
)


# FIX: was telling agent to be extreme, make up risk models, recommend YOLO strategies
risk_assessment = Task(
    description=(
        "Conduct a thorough risk assessment based on the financial document at {file_path} "
        "and the user's query: {query}. "
        "Identify real risk factors present in the data such as high debt-to-equity ratio, "
        "declining revenue, negative cash flow, or liquidity concerns. "
        "Use standard risk frameworks and provide practical, data-backed mitigation strategies. "
        "Do not exaggerate or fabricate risk scenarios."
    ),
    expected_output=(
        "A structured risk assessment report containing: "
        "1. Key risk factors identified from the document with supporting figures "
        "2. Risk severity classification (Low / Medium / High) for each factor "
        "3. Practical risk mitigation strategies grounded in the financial data "
        "4. Overall risk profile summary of the company or document"
    ),
    agent=risk_assessor,                               # FIX: was financial_analyst
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
    context=[analyze_financial_document]               # FIX: depends on analysis completing first
)
