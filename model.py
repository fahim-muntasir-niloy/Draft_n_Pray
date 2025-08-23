import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.embeddings.base import Embeddings
from google import genai
from google.genai import types

load_dotenv()


os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

llm = init_chat_model("google_genai:gemini-2.5-flash", temperature=0.7)


class CustomGoogleGenAIEmbeddings(Embeddings):
    def __init__(
        self, model: str = "gemini-embedding-001", output_dimensionality: int = 768
    ):
        self.client = genai.Client()
        self.model = model
        self.output_dimensionality = output_dimensionality

    def embed_query(self, text: str) -> list[float]:
        result = self.client.models.embed_content(
            model=self.model,
            contents=text,
            config=types.EmbedContentConfig(
                output_dimensionality=self.output_dimensionality
            ),
        )
        [embedding_obj] = result.embeddings
        return embedding_obj.values

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        result = self.client.models.embed_content(
            model=self.model,
            contents=texts,
            config=types.EmbedContentConfig(
                output_dimensionality=self.output_dimensionality
            ),
        )
        return [embedding.values for embedding in result.embeddings]


embedding_engine = CustomGoogleGenAIEmbeddings(
    model="gemini-embedding-001", output_dimensionality=768
)


def get_model():
    return llm


def get_embedding_engine():
    return embedding_engine
