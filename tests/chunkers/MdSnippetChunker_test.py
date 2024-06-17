import pytest
from swarmauri.standard.chunkers.concrete.MdSnippetChunker import MdSnippetChunker

@pytest.mark.unit
def test_ubc_resource():
	def test():
		chunker = MdSnippetChunker()
		assert chunker.resource == 'Chunker'
	test()

@pytest.mark.unit
def test_chunk_text():
	def test():
		unchunked_text = """
```python

print('hello world')

```

Above is an example of some code.

```bash
echo 'test'
```
	
Here we have some text:

```md
# Hello
- list item
- list item
```
"""
		chunks = [('', 'python', "print('hello world')")]
		assert MdSnippetChunker(language='python').chunk_text(unchunked_text) == chunks
	test()

@pytest.mark.unit
def test_chunk_text_2():
	def test():
		unchunked_text = """
```python

print('hello world')

```

Above is an example of some code.

```bash
echo 'test'
```

Here we have some text:

```md
# Hello
- list item
- list item
```
"""
		chunks = [('', 'python', "print('hello world')"),
 				  ('', 'bash', "echo 'test'"),
 				 ('Above is an example of some code.',
  				  'md',
  				 '# Hello\n- list item\n- list item')]
		assert MdSnippetChunker().chunk_text(unchunked_text) == chunks
	test()
