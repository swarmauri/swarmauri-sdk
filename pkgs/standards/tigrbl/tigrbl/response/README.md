# Response and Template Specs

Tigrbl exposes flexible response configuration through the `ResponseSpec` and `TemplateSpec` dataclasses in `tigrbl.response.types`.

## `ResponseSpec`

`ResponseSpec` controls how an operation returns data:

- **`kind`** – response mode: `"auto"`, `"json"`, `"html"`, `"text"`, `"file"`, `"stream"`, or `"redirect"`.
- **`media_type`** – explicit `Content-Type` header.
- **`status_code`** – HTTP status override.
- **`headers`** – mapping of additional headers.
- **`envelope`** – wrap payloads in a standard envelope when `True`.
- **`template`** – optional [`TemplateSpec`](#templatespec) to render an HTML response.
- **`filename`** – file name for `file` responses.
- **`download`** – force browser downloads when `True`.
- **`etag`** – ETag header value.
- **`cache_control`** – `Cache-Control` header value.
- **`redirect_to`** – target location for `redirect` responses.

## `TemplateSpec`

`TemplateSpec` defines how templates are resolved and rendered:

- **`name`** – template identifier passed to the renderer.
- **`search_paths`** – directories to search for template files.
- **`package`** – Python package providing templates via `importlib.resources`.
- **`auto_reload`** – when `True`, reload templates on each request (useful in development).
- **`filters`** – custom Jinja2 filters.
- **`globals`** – additional template globals.

A `TemplateSpec` may be nested inside a `ResponseSpec`'s `template` field to render HTML output. When provided, the runtime invokes `render_template` and populates the response body with the rendered HTML.

These specs offer a declarative way to tailor outbound responses and integrate server-side templates without manual response handling.
