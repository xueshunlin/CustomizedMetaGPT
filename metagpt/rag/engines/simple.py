"""Simple Engine."""

import json
import os
import time
import nest_asyncio
from typing import Any, Optional, Union

from llama_index.core import SimpleDirectoryReader, ServiceContext, VectorStoreIndex
from llama_index.core.callbacks.base import CallbackManager
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.embeddings.mock_embed_model import MockEmbedding
from llama_index.core.indices.base import BaseIndex
from llama_index.core.ingestion.pipeline import run_transformations
from llama_index.core.llms import LLM
from statistics import mean
from llama_index.core.node_parser import SentenceSplitter, SemanticSplitterNodeParser
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.readers.base import BaseReader
from llama_index.core.response_synthesizers import (
    BaseSynthesizer,
    get_response_synthesizer,
)
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import (
    BaseNode,
    Document,
    NodeWithScore,
    QueryBundle,
    QueryType,
    TransformComponent,
)

from llama_index.core.evaluation import (
    DatasetGenerator,
    FaithfulnessEvaluator,
    RelevancyEvaluator,
    BatchEvalRunner
)

from metagpt.config2 import config
from metagpt.rag.factories import (
    get_index,
    get_rag_embedding,
    get_rag_llm,
    get_rankers,
    get_retriever,
)
from metagpt.rag.interface import NoEmbedding, RAGObject
from metagpt.rag.parsers import OmniParse
from metagpt.rag.retrievers.base import ModifiableRAGRetriever, PersistableRAGRetriever
from metagpt.rag.retrievers.hybrid_retriever import SimpleHybridRetriever
from metagpt.rag.schema import (
    BaseIndexConfig,
    BaseRankerConfig,
    BaseRetrieverConfig,
    BM25RetrieverConfig,
    ObjectNode,
    OmniParseOptions,
    OmniParseType,
    ParseResultType,
)
from metagpt.utils.common import import_class


class SimpleEngine(RetrieverQueryEngine):
    """SimpleEngine is designed to be simple and straightforward.

    It is a lightweight and easy-to-use search engine that integrates
    document reading, embedding, indexing, retrieving, and ranking functionalities
    into a single, straightforward workflow. It is designed to quickly set up a
    search engine from a collection of documents.
    """

    def __init__(
        self,
        retriever: BaseRetriever,
        response_synthesizer: Optional[BaseSynthesizer] = None,
        node_postprocessors: Optional[list[BaseNodePostprocessor]] = None,
        callback_manager: Optional[CallbackManager] = None,
        transformations: Optional[list[TransformComponent]] = None,
    ) -> None:
        super().__init__(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
            node_postprocessors=node_postprocessors,
            callback_manager=callback_manager,
        )
        self._transformations = transformations or self._default_transformations()

    @staticmethod
    def get_eval_results(key, eval_results):
        results = eval_results[key]
        correct = 0
        for result in results:
            if result.passing:
                correct += 1
        score = correct / len(results)
        print(f"{key} Score: {score:.2f}")
        return score
    
    @classmethod
    async def from_docs_to_nodes(
        cls,
        input_dir: str = None,
        input_files: list[str] = None,
        transformations: Optional[list[TransformComponent]] = None,
        optimize_chunk_size: bool = False,
        enable_chunking: bool = True,
    ) -> list[BaseNode]:
        """From docs.

        Must provide either `input_dir` or `input_files`.

        Args:
            input_dir: Path to the directory.
            input_files: List of file paths to read (Optional; overrides input_dir, exclude).
            transformations: Parse documents to nodes. Default [SentenceSplitter].
            embed_model: Parse nodes to embedding. Must supported by llama index. Default OpenAIEmbedding.
            llm: Must supported by llama index. Default OpenAI.
            retriever_configs: Configuration for retrievers. If more than one config, will use SimpleHybridRetriever.
            ranker_configs: Configuration for rankers.
        """
        if not input_dir and not input_files:
            raise ValueError("You have no modularized files to evaluate")

        file_extractor = cls._get_file_extractor()
        documents = SimpleDirectoryReader(
            input_dir=input_dir, input_files=input_files, file_extractor=file_extractor
        ).load_data()
        
        #### Automatic Chunk Size Optimization (archived for unstable performance)
        # best_chunk_size = None
        # best_score = 0
        # chunk_size_scores = {}
            
        # if optimize_chunk_size:
        #     nest_asyncio.apply()
        #     data_generator = DatasetGenerator.from_documents(documents,llm=get_rag_llm())
        #     eval_questions = data_generator.generate_questions_from_nodes(num = 10)
        #     # Define service context for GPT-4 for evaluation
        #     service_context = ServiceContext.from_defaults(llm=get_rag_llm(), embed_model=cls._resolve_embed_model())

        #     # Define Faithfulness and Relevancy Evaluators
        #     faithfulness = FaithfulnessEvaluator(service_context=service_context)
        #     relevancy = RelevancyEvaluator(service_context=service_context)

        #     num_workers = os.cpu_count()
        #     print("Number of workers (CPU cores):", num_workers)

        #     for chunk_size in [128, 256, 512, 1024, 2048]:
        #         overlap = chunk_size // 10
        #         splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
        #         vector_index = VectorStoreIndex.from_documents(
        #             documents, transformations=[splitter],llm=get_rag_llm(), embed_model=cls._resolve_embed_model()
        #         )

        #         runner = BatchEvalRunner(
        #                 {"faithfulness": faithfulness, "relevancy": relevancy},
        #                 workers=num_workers,
        #             )
                
        #         eval_results = await runner.aevaluate_queries(
        #             vector_index.as_query_engine(llm=get_rag_llm()),queries=eval_questions
        #         )
                
        #         faithfulness_score = cls.get_eval_results("faithfulness", eval_results)
        #         relevancy_score = cls.get_eval_results("relevancy", eval_results)
        #         avg_score = mean([faithfulness_score, relevancy_score])

        #         chunk_size_scores[chunk_size] = avg_score

        #         print(f"Chunk size {chunk_size}: Faithfulness={faithfulness_score:.2f}, Relevancy={relevancy_score:.2f}, Avg={avg_score:.2f}")

        #         if avg_score > best_score:
        #             best_score = avg_score
        #             best_chunk_size = chunk_size

        #     print(f"Best chunk size determined: {best_chunk_size} with Avg Score: {best_score:.2f}")

        # best_chunk_size = 512
        cls._fix_document_metadata(documents)

        if enable_chunking:
            # splitter = SentenceSplitter(chunk_size=best_chunk_size, chunk_overlap=0)
            splitter = SemanticSplitterNodeParser(
                buffer_size=1, breakpoint_percentile_threshold=95, embed_model=cls._resolve_embed_model()
            )
            transformations = [splitter]

        nodes = run_transformations(documents, transformations=transformations if transformations else [])

        return nodes
    
    
    @classmethod
    def from_nodes_to_engine(cls, nodes: list[BaseNode], transformations: Optional[list[TransformComponent]] = None,
                             embed_model: BaseEmbedding = None, llm: LLM = None,
                             retriever_configs: list[BaseRetrieverConfig] = None,
                             ranker_configs: list[BaseRankerConfig] = None) -> "SimpleEngine":

        return cls._from_nodes(
            nodes=nodes,
            transformations=transformations,
            embed_model=embed_model,
            llm=llm,
            retriever_configs=retriever_configs,
            ranker_configs=ranker_configs,
        )
    
    @classmethod
    def from_objs(
        cls,
        objs: Optional[list[RAGObject]] = None,
        transformations: Optional[list[TransformComponent]] = None,
        embed_model: BaseEmbedding = None,
        llm: LLM = None,
        retriever_configs: list[BaseRetrieverConfig] = None,
        ranker_configs: list[BaseRankerConfig] = None,
    ) -> "SimpleEngine":
        """From objs.

        Args:
            objs: List of RAGObject.
            transformations: Parse documents to nodes. Default [SentenceSplitter].
            embed_model: Parse nodes to embedding. Must supported by llama index. Default OpenAIEmbedding.
            llm: Must supported by llama index. Default OpenAI.
            retriever_configs: Configuration for retrievers. If more than one config, will use SimpleHybridRetriever.
            ranker_configs: Configuration for rankers.
        """
        objs = objs or []
        retriever_configs = retriever_configs or []

        if not objs and any(isinstance(config, BM25RetrieverConfig) for config in retriever_configs):
            raise ValueError("In BM25RetrieverConfig, Objs must not be empty.")

        nodes = [ObjectNode(text=obj.rag_key(), metadata=ObjectNode.get_obj_metadata(obj)) for obj in objs]

        return cls._from_nodes(
            nodes=nodes,
            transformations=transformations,
            embed_model=embed_model,
            llm=llm,
            retriever_configs=retriever_configs,
            ranker_configs=ranker_configs,
        )

    @classmethod
    def from_index(
        cls,
        index_config: BaseIndexConfig,
        embed_model: BaseEmbedding = None,
        llm: LLM = None,
        retriever_configs: list[BaseRetrieverConfig] = None,
        ranker_configs: list[BaseRankerConfig] = None,
    ) -> "SimpleEngine":
        """Load from previously maintained index by self.persist(), index_config contains persis_path."""
        index = get_index(index_config, embed_model=cls._resolve_embed_model(embed_model, [index_config]))
        return cls._from_index(index, llm=llm, retriever_configs=retriever_configs, ranker_configs=ranker_configs)

    async def asearch(self, content: str, **kwargs) -> str:
        """Inplement tools.SearchInterface"""
        return await self.aquery(content)

    def from_engine_to_nodes(self) -> list[BaseNode]:
        return self.retriever.retrieve_all_nodes()
    
    def retrieve(self, query: QueryType) -> list[NodeWithScore]:
        query_bundle = QueryBundle(query) if isinstance(query, str) else query

        nodes = super().retrieve(query_bundle)
        self._try_reconstruct_obj(nodes)
        return nodes

    async def aretrieve(self, query: QueryType) -> list[NodeWithScore]:
        """Allow query to be str."""
        query_bundle = QueryBundle(query) if isinstance(query, str) else query

        nodes = await super().aretrieve(query_bundle)
        self._try_reconstruct_obj(nodes)
        return nodes

    def add_docs(self, input_files: list[str]):
        """Add docs to retriever. retriever must has add_nodes func."""
        self._ensure_retriever_modifiable()

        documents = SimpleDirectoryReader(input_files=input_files).load_data()
        self._fix_document_metadata(documents)

        nodes = run_transformations(documents, transformations=self._transformations)
        self._save_nodes(nodes)

    def add_objs(self, objs: list[RAGObject]):
        """Adds objects to the retriever, storing each object's original form in metadata for future reference."""
        self._ensure_retriever_modifiable()

        nodes = [ObjectNode(text=obj.rag_key(), metadata=ObjectNode.get_obj_metadata(obj)) for obj in objs]
        self._save_nodes(nodes)

    def persist(self, persist_dir: Union[str, os.PathLike], **kwargs):
        """Persist."""
        self._ensure_retriever_persistable()

        self._persist(str(persist_dir), **kwargs)

    @classmethod
    def _from_nodes(
        cls,
        nodes: list[BaseNode],
        transformations: Optional[list[TransformComponent]] = None,
        embed_model: BaseEmbedding = None,
        llm: LLM = None,
        retriever_configs: list[BaseRetrieverConfig] = None,
        ranker_configs: list[BaseRankerConfig] = None,
    ) -> "SimpleEngine":
        embed_model = cls._resolve_embed_model(embed_model, retriever_configs)
        llm = llm or get_rag_llm()

        retriever = get_retriever(configs=retriever_configs, nodes=nodes, embed_model=embed_model)
        rankers = get_rankers(configs=ranker_configs, llm=llm)  # Default []

        return cls(
            retriever=retriever,
            node_postprocessors=rankers,
            response_synthesizer=get_response_synthesizer(llm=llm),
            transformations=transformations,
        )

    @classmethod
    def _from_index(
        cls,
        index: BaseIndex,
        llm: LLM = None,
        retriever_configs: list[BaseRetrieverConfig] = None,
        ranker_configs: list[BaseRankerConfig] = None,
    ) -> "SimpleEngine":
        llm = llm or get_rag_llm()

        retriever = get_retriever(configs=retriever_configs, index=index)  # Default index.as_retriever
        rankers = get_rankers(configs=ranker_configs, llm=llm)  # Default []

        return cls(
            retriever=retriever,
            node_postprocessors=rankers,
            response_synthesizer=get_response_synthesizer(llm=llm),
        )

    def _ensure_retriever_modifiable(self):
        self._ensure_retriever_of_type(ModifiableRAGRetriever)

    def _ensure_retriever_persistable(self):
        self._ensure_retriever_of_type(PersistableRAGRetriever)

    def _ensure_retriever_of_type(self, required_type: BaseRetriever):
        """Ensure that self.retriever is required_type, or at least one of its components, if it's a SimpleHybridRetriever.

        Args:
            required_type: The class that the retriever is expected to be an instance of.
        """
        if isinstance(self.retriever, SimpleHybridRetriever):
            if not any(isinstance(r, required_type) for r in self.retriever.retrievers):
                raise TypeError(
                    f"Must have at least one retriever of type {required_type.__name__} in SimpleHybridRetriever"
                )

        if not isinstance(self.retriever, required_type):
            raise TypeError(f"The retriever is not of type {required_type.__name__}: {type(self.retriever)}")

    def _save_nodes(self, nodes: list[BaseNode]):
        self.retriever.add_nodes(nodes)

    def _persist(self, persist_dir: str, **kwargs):
        self.retriever.persist(persist_dir, **kwargs)

    @staticmethod
    def _try_reconstruct_obj(nodes: list[NodeWithScore]):
        """If node is object, then dynamically reconstruct object, and save object to node.metadata["obj"]."""
        for node in nodes:
            if node.metadata.get("is_obj", False):
                obj_cls = import_class(node.metadata["obj_cls_name"], node.metadata["obj_mod_name"])
                obj_dict = json.loads(node.metadata["obj_json"])
                node.metadata["obj"] = obj_cls(**obj_dict)

    @staticmethod
    def _fix_document_metadata(documents: list[Document]):
        """LlamaIndex keep metadata['file_path'], which is unnecessary, maybe deleted in the near future."""
        for doc in documents:
            doc.excluded_embed_metadata_keys.append("file_path")

    @staticmethod
    def _resolve_embed_model(embed_model: BaseEmbedding = None, configs: list[Any] = None) -> BaseEmbedding:
        if configs and all(isinstance(c, NoEmbedding) for c in configs):
            return MockEmbedding(embed_dim=1)

        return embed_model or get_rag_embedding()

    @staticmethod
    def _default_transformations():
        return [SentenceSplitter()]

    @staticmethod
    def _get_file_extractor() -> dict[str:BaseReader]:
        """
        Get the file extractor.
        Currently, only PDF use OmniParse. Other document types use the built-in reader from llama_index.

        Returns:
            dict[file_type: BaseReader]
        """
        file_extractor: dict[str:BaseReader] = {}
        if config.omniparse.base_url:
            pdf_parser = OmniParse(
                api_key=config.omniparse.api_key,
                base_url=config.omniparse.base_url,
                parse_options=OmniParseOptions(parse_type=OmniParseType.PDF, result_type=ParseResultType.MD),
            )
            file_extractor[".pdf"] = pdf_parser

        return file_extractor