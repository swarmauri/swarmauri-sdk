import pytest
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.vector_stores.concrete.Doc2VecVectorStore import Doc2VecVectorStore

@pytest.mark.unit
def test_1():
	def test():
		vs = Doc2VecVectorStore()
		assert vs.embedder.resource == 'Embedding'
	test()

@pytest.mark.unit
def test_2():
	def test():
		vs = Doc2VecVectorStore()
		documents = [Document(content="test"),
             Document(content='test1'),
             Document(content='test2'),
             Document(content='test3')]

		vs.add_documents(documents)
		assert len(vs.retrieve(query='test', top_k=2)) == 2
	test()
