'''
This code creates a RAG application with a Streamlit UI that allows users to ask questions about a PDF document. 
It uses LangChain LLM Framework to load, chunk, and embed the PDF, and then stores it in a FAISS vector database. 
When a user asks a question, the application retrieves relevant chunks from the vector database and 
uses a large language model (GPT-4) to answer the question based on those chunks.
'''
# Dependencies installation:
# pip install langchain openai streamlit python-dotenv langchain_community faiss

# Import Libraries
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os

# You should have created your OpenAI account and OpenAI API Key.
# The API Key should be in the .env file as: OPENAI_API_KEY=sk-....
# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def ingest_pdf(pdf_file_path):
    """
    Ingests a PDF file, chunks it, and saves it in a FAISS vector store.
    Args:
        pdf_file_path: Path to the PDF file.
    """

    loader = PyPDFLoader(pdf_file_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(texts, embeddings)

    # Save the vectorstore
    vectorstore.save_local("faiss_sepq")


if __name__ == "__main__":
    # Paths
    pdf_file_path = "Introduction-cyber-security.pdf" 

    # Ingest the PDF file (only run this once to create the vectorstore)
    ingest_pdf(pdf_file_path)

    # Load the FAISS vectorstore
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.load_local("faiss_sepq", embeddings, allow_dangerous_deserialization=True)

    # Define the prompt template for the language model
    prompt = ChatPromptTemplate.from_template("""Answer the following question based only on the provided context:

    <context>
    {context}
    </context>  

    Question: {input}""")

    # Initialize the language model (GPT-4)
    llm = ChatOpenAI(temperature=0, model_name="gpt-4o")

    # Create a chain to stuff documents into the prompt template
    document_chain = create_stuff_documents_chain(llm, prompt)

    # Create a retriever to fetch relevant documents from the vectorstore
    retriever = vectorstore.as_retriever()

    # Create a retrieval chain to combine the retriever and document chain
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    # Streamlit UI
    st.title("PDF Question Answering")
    question = st.text_input("Ask a question about the PDF:")
    if st.button("Get Answer"):
        if question:
            # Get the answer from the retrieval chain
            response = retrieval_chain.invoke({"input": question})
            # Display the answer in the Streamlit app
            st.write(response["answer"])
            # Print the full response to the console (for debugging)
            print(response)
        else:
            st.warning("Please enter a question.")