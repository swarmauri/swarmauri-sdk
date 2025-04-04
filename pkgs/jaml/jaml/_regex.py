import re

# ---------------------------
# Regex for Reserved Keywords
# ---------------------------
def regex_keywords():
    pattern = r'\b(?:is|not|and|or|if|elif|else|for|in|include)\b'
    return re.compile(pattern)

# ---------------------------
# Regex for Reserved Special Functions
# ---------------------------
def regex_reserved_functions():
    pattern = r'\b(?:File\(\)|Git\(\))\b'
    return re.compile(pattern)

# ---------------------------
# Regex for Boolean Literals
# ---------------------------
def regex_boolean():
    pattern = r'\b(?:true|false)\b'
    return re.compile(pattern)

# ---------------------------
# Regex for Null Literal
# ---------------------------
def regex_null():
    pattern = r'\bnull\b'
    return re.compile(pattern)

# ---------------------------
# Regex for Identifiers
# ---------------------------
def regex_identifier():
    pattern = r'\b[a-zA-Z_][a-zA-Z0-9_-]*\b'
    return re.compile(pattern)

def regex_illegal_identifier():
    # This regex matches identifiers that include at least one disallowed special character.
    # Disallowed characters include: !, @, #, $, %, ^, &, *, (, ), +, =, {, }, [, ], |, \, :, ;, ", ', <, >, ,, ., ?, /
    pattern = r'\b[a-zA-Z_][a-zA-Z0-9_-]*[!@#$%^&*()+={}\[\]|\\:;"\'<>,.?/][a-zA-Z0-9_-]*\b'
    return re.compile(pattern)

def regex_exclamation_outside():
    pattern = r'(?<![\[{(])!([^)\]}]*?(?=[\[{(]|$)|(?=[\]}\)]))'
    return re.compile(pattern, re.DOTALL)

# ---------------------------
# Regex for Numeric Types: Integers
# ---------------------------
def regex_integer():
    pattern = r'\b(?:0[oO][0-7]+|0[xX][0-9a-fA-F]+|0[bB][01]+|[+-]?(?:0|[1-9]\d*))\b'
    return re.compile(pattern)

# ---------------------------
# Regex for Numeric Types: Floats
# ---------------------------
def regex_float():
    part = r'\b[+-]?(?:(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?|(?:inf|nan))'
    pattern = part + r'\b'
    return re.compile(pattern)

# ---------------------------
# Regex for Strings (with Multiline Support)
# ---------------------------
def regex_f_string_prefix():
    return r"(?:f)?"

def regex_triple_single_quote():
    return r"'''(.*?)'''"

def regex_triple_double_quote():
    return r'"""(.*?)"""'

def regex_triple_backtick():
    return r"```(.*?)```"

def regex_single_quote():
    return r"'(?:\\.|[^'\\])*'"

def regex_double_quote():
    return r'"(?:\\.|[^"\\])*"'

def regex_backtick():
    return r"`(?:\\.|[^`\\])*`"

def regex_string():
    pattern = (
        "("                        # Start outer capturing group
        + regex_f_string_prefix()  # Optional f-string prefix
        + "(?:"                    # Begin non-capturing group for alternatives
        + regex_triple_single_quote()
        + "|"
        + regex_triple_double_quote()
        + "|"
        + regex_triple_backtick()
        + "|"
        + regex_single_quote()
        + "|"
        + regex_double_quote()
        + "|"
        + regex_backtick()
        + ")"
        + ")"                      # End outer capturing group
    )
    return re.compile(pattern, re.DOTALL)

# ---------------------------
# Regex for Arrays (Inline and Multiline)
# ---------------------------
def regex_array():
    pattern = r'\[\s*.*?\s*\]'
    return re.compile(pattern, re.DOTALL)

# ---------------------------
# Regex for Inline Tables (including Multiline)
# ---------------------------
def regex_inline_table():
    # Handles one level of nesting: { ... { ... } ... }
    # by allowing either "normal" non-brace characters
    # or a complete nested { ... } segment inside.
    pattern = r'\{(?:[^{}]|\{[^{}]*\})*\}'
    return re.compile(pattern, re.DOTALL)

# ---------------------------
# Regex for Standard Table Sections (header lines)
# ---------------------------
def regex_table_section():
    # Allow letters, digits, underscores, hyphens, and dots.
    pattern = r'\[[A-Za-z0-9_.\-]+\]'
    return re.compile(pattern)

# ---------------------------
# (MEP-0028) Placeholder Regex for Conditional Table Sections 
# ---------------------------
def regex_conditional_table_section():
    # e.g., only letters/digits/hyphens/underscores allowed in the name,
    # no commas or spaces.
    pass

# ---------------------------
# Regex for Table Arrays (header lines)
# ---------------------------
def regex_table_array():
    pattern = r'\[\[[^\]\n]+\]\]'
    return re.compile(pattern)

# ---------------------------
# Regex for Operators
# ---------------------------
def regex_operator():
    pattern = r'(\*\*|==|!=|>=|<=|=|->|<<|\+|-|\*|/|%|>|<|\|)'
    return re.compile(pattern)

# ---------------------------
# Regex for Punctuation
# ---------------------------
def regex_punctuation():
    pattern = r'[{}:\.,;~!\!\*\^&/\\()\]]'
    return re.compile(pattern)

# ---------------------------
# Regex for Comments
# ---------------------------
def regex_comment():
    pattern = r'\#[^\n]*'
    return re.compile(pattern)

# ---------------------------
# Regex for Scoped Variables
# ---------------------------
def regex_scoped_variable():
    pattern = r'[@%$]\{[^}]+\}'
    return re.compile(pattern)

# ---------------------------
# Regex for Whitespace
# ---------------------------
def regex_whitespace():
    pattern = r'\s+'
    return re.compile(pattern)

# ---------------------------
# NEW: Regex for {~ ... ~} blocks (TILDE_BLOCK)
# ---------------------------
def regex_tilde_block():
    pattern = r'\{~.*?~\}'
    return re.compile(pattern, re.DOTALL)

# ---------------------------
# NEW: Regex for {^ ... ^} blocks (FOLDER_BLOCK)
# ---------------------------
def regex_folder_block():
    pattern = r'\{\^.*?\^\}'
    return re.compile(pattern, re.DOTALL)