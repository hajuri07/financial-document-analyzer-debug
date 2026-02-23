import os
from dotenv import load_dotenv
load_dotenv()

from crewai_tools import SerperDevTool
from langchain_community.document_loaders import PyPDFLoader  # FIX: Pdf was never imported
from crewai.tools import tool                                  # FIX: missing @tool decorator

## Creating search tool
search_tool = SerperDevTool()

## Creating custom pdf reader tool
class FinancialDocumentTool():
    
    @tool("Read Financial Document")                           # FIX: added @tool decorator
    def read_data_tool(path: str = 'data/sample.pdf') -> str: # FIX: removed async (CrewAI needs sync tools)
        """Tool to read data from a PDF file.

        Args:
            path (str): Path of the PDF file. Defaults to 'data/sample.pdf'.

        Returns:
            str: Full text content of the financial document.
        """
        if not os.path.exists(path):                          # FIX: added file existence check
            return f"Error: File not found at path '{path}'"

        loader = PyPDFLoader(file_path=path)                  # FIX: use PyPDFLoader instead of undefined Pdf
        docs = loader.load()

        full_report = ""
        for data in docs:
            content = data.page_content

            # Remove extra whitespaces
            while "\n\n" in content:
                content = content.replace("\n\n", "\n")

            full_report += content + "\n"

        return full_report if full_report.strip() else "No readable content found in the document."


class InvestmentTool:

    @tool("Analyze Investment Data")                          # FIX: added @tool decorator
    def analyze_investment_tool(financial_document_data: str) -> str:  # FIX: removed async
        """Analyzes financial document data for investment insights.

        Args:
            financial_document_data (str): Extracted text from a financial document.

        Returns:
            str: Cleaned and processed financial data ready for analysis.
        """
        processed_data = financial_document_data

        # Clean up double spaces
        i = 0
        result = []
        while i < len(processed_data):
            if i + 1 < len(processed_data) and processed_data[i] == ' ' and processed_data[i+1] == ' ':
                i += 1  # skip one of the double spaces
            else:
                result.append(processed_data[i])
                i += 1

        return "".join(result)


class RiskTool:

    @tool("Create Risk Assessment")                           # FIX: added @tool decorator
    def create_risk_assessment_tool(financial_document_data: str) -> str:  # FIX: removed async
        """Creates a risk assessment based on financial document data.

        Args:
            financial_document_data (str): Extracted text from a financial document.

        Returns:
            str: Structured risk assessment data.
        """
        if not financial_document_data or not financial_document_data.strip():
            return "Error: No financial data provided for risk assessment."

        return financial_document_data
