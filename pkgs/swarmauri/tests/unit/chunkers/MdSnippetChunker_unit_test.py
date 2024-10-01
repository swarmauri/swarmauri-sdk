import pytest
from swarmauri.chunkers.concrete.MdSnippetChunker import MdSnippetChunker

@pytest.mark.unit
def test_ubc_resource():
	chunker = MdSnippetChunker()
	assert chunker.resource == 'Chunker'


@pytest.mark.unit
def test_ubc_type():
	chunker = MdSnippetChunker()
	assert chunker.type == 'MdSnippetChunker'


@pytest.mark.unit
def test_chunk_text():
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

@pytest.mark.unit
def test_chunk_text_2():
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

@pytest.mark.unit
def test_serialization():
	chunker = MdSnippetChunker()
	assert chunker.id == MdSnippetChunker.model_validate_json(chunker.model_dump_json()).id