import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.embeddings.base import Embeddings
from google import genai
from google.genai import types

load_dotenv()


def get_model(api_key: str):
    # Pass the key directly instead of relying on environment variables
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", temperature=0.7, google_api_key=api_key
    )


class CustomGoogleGenAIEmbeddings(Embeddings):
    def __init__(
        self,
        model: str = "gemini-embedding-001",
        output_dimensionality: int = 768,
        api_key: str = None,
    ):
        try:
            if api_key:
                # Use the new API key parameter in the client constructor
                self.client = genai.Client(api_key=api_key)
            else:
                self.client = genai.Client()
            self.model = model
            self.output_dimensionality = output_dimensionality
            self.use_custom = True
        except Exception as e:
            # Fallback to LangChain integration if custom implementation fails
            print(f"Warning: Custom embedding failed, using LangChain fallback: {e}")
            self.use_custom = False
            self.langchain_embeddings = GoogleGenerativeAIEmbeddings(
                model=model,
                google_api_key=api_key,
                task_type="retrieval_document",
                title="CV Document",
            )

    def embed_query(self, text: str) -> list[float]:
        if hasattr(self, "use_custom") and self.use_custom:
            try:
                result = self.client.models.embed_content(
                    model=self.model,
                    contents=text,
                    config=types.EmbedContentConfig(
                        output_dimensionality=self.output_dimensionality
                    ),
                )
                [embedding_obj] = result.embeddings
                return embedding_obj.values
            except Exception as e:
                print(f"Custom embedding failed, falling back to LangChain: {e}")
                return self.langchain_embeddings.embed_query(text)
        else:
            return self.langchain_embeddings.embed_query(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if hasattr(self, "use_custom") and self.use_custom:
            try:
                result = self.client.models.embed_content(
                    model=self.model,
                    contents=texts,
                    config=types.EmbedContentConfig(
                        output_dimensionality=self.output_dimensionality
                    ),
                )
                return [embedding.values for embedding in result.embeddings]
            except Exception as e:
                print(f"Custom embedding failed, falling back to LangChain: {e}")
                return self.langchain_embeddings.embed_documents(texts)
        else:
            return self.langchain_embeddings.embed_documents(texts)


def get_embedding_engine(api_key: str = None):
    return CustomGoogleGenAIEmbeddings(
        model="gemini-embedding-001", output_dimensionality=768, api_key=api_key
    )


def get_langchain_embedding_engine(api_key: str = None):
    """Get embedding engine using LangChain integration (more reliable)"""
    try:
        return GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001",
            google_api_key=api_key,
            task_type="retrieval_document",
            title="CV Document",
        )
    except Exception as e:
        print(f"LangChain embedding engine failed: {e}")
        # Fallback to custom implementation
        return CustomGoogleGenAIEmbeddings(
            model="gemini-embedding-001", output_dimensionality=768, api_key=api_key
        )


def test_embedding_engine(api_key: str = None):
    """Test if the embedding engine is working properly"""
    try:
        engine = get_langchain_embedding_engine(api_key)
        # Test with a simple text
        test_embedding = engine.embed_query("Test text for embedding")
        if test_embedding and len(test_embedding) > 0:
            return (
                True,
                f"✅ Embedding engine working! Generated {len(test_embedding)}-dimensional vector",
            )
        else:
            return False, "❌ Embedding engine returned empty result"
    except Exception as e:
        return False, f"❌ Embedding engine test failed: {str(e)}"
