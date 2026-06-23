from typing import Any, Dict, List

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    VectorSearch,
    VectorSearchProfile,
)
from azure.search.documents.models import VectorizedQuery

from config import Config


class AzureSearchClient:
    def __init__(self, config: Config):
        self.config = config
        self.credential = AzureKeyCredential(config.AZURE_SEARCH_API_KEY)
        self.index_client = SearchIndexClient(
            endpoint=config.AZURE_SEARCH_ENDPOINT,
            credential=self.credential,
        )
        self._study_client: SearchClient | None = None
        self._code_client: SearchClient | None = None

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _get_study_client(self) -> SearchClient:
        if not self._study_client:
            self._study_client = SearchClient(
                endpoint=self.config.AZURE_SEARCH_ENDPOINT,
                index_name=self.config.AZURE_SEARCH_STUDY_INDEX,
                credential=self.credential,
            )
        return self._study_client

    def _get_code_client(self) -> SearchClient:
        if not self._code_client:
            self._code_client = SearchClient(
                endpoint=self.config.AZURE_SEARCH_ENDPOINT,
                index_name=self.config.AZURE_SEARCH_CODE_INDEX,
                credential=self.credential,
            )
        return self._code_client

    def _vector_search_config(self) -> VectorSearch:
        return VectorSearch(
            algorithms=[HnswAlgorithmConfiguration(name="hnsw-config")],
            profiles=[
                VectorSearchProfile(
                    name="vector-profile",
                    algorithm_configuration_name="hnsw-config",
                )
            ],
        )

    # ------------------------------------------------------------------ #
    #  Index management                                                    #
    # ------------------------------------------------------------------ #

    def create_study_index(self) -> None:
        fields = [
            SearchField(name="id", type=SearchFieldDataType.String, key=True),
            SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
            SearchField(name="title", type=SearchFieldDataType.String, searchable=True, filterable=True),
            SearchField(name="source", type=SearchFieldDataType.String, filterable=True),
            SearchField(name="chunk_index", type=SearchFieldDataType.Int32, filterable=True),
            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=self.config.EMBEDDING_DIMENSIONS,
                vector_search_profile_name="vector-profile",
            ),
        ]
        index = SearchIndex(
            name=self.config.AZURE_SEARCH_STUDY_INDEX,
            fields=fields,
            vector_search=self._vector_search_config(),
        )
        self.index_client.create_or_update_index(index)

    def create_code_index(self) -> None:
        fields = [
            SearchField(name="id", type=SearchFieldDataType.String, key=True),
            SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
            SearchField(name="filename", type=SearchFieldDataType.String, searchable=True, filterable=True),
            SearchField(name="language", type=SearchFieldDataType.String, filterable=True),
            SearchField(name="source", type=SearchFieldDataType.String, filterable=True),
            SearchField(name="chunk_index", type=SearchFieldDataType.Int32, filterable=True),
            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=self.config.EMBEDDING_DIMENSIONS,
                vector_search_profile_name="vector-profile",
            ),
        ]
        index = SearchIndex(
            name=self.config.AZURE_SEARCH_CODE_INDEX,
            fields=fields,
            vector_search=self._vector_search_config(),
        )
        self.index_client.create_or_update_index(index)

    # ------------------------------------------------------------------ #
    #  Upload & Search                                                     #
    # ------------------------------------------------------------------ #

    def upload_documents(self, documents: List[Dict[str, Any]], index_type: str = "study") -> None:
        client = self._get_study_client() if index_type == "study" else self._get_code_client()
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            client.upload_documents(documents=documents[i : i + batch_size])

    def search(
        self,
        query: str,
        query_vector: List[float],
        index_type: str = "study",
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        client = self._get_study_client() if index_type == "study" else self._get_code_client()

        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=top_k,
            fields="content_vector",
        )

        select_fields = (
            ["id", "content", "source", "title"]
            if index_type == "study"
            else ["id", "content", "source", "filename", "language"]
        )

        results = client.search(
            search_text=query,
            vector_queries=[vector_query],
            top=top_k,
            select=select_fields,
        )

        return [dict(r) for r in results]
