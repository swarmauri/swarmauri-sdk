from ._regex import (
    regex_keywords, regex_reserved_functions, regex_boolean, regex_null,
    regex_identifier, regex_integer, regex_float, regex_f_string_prefix,
    regex_triple_single_quote, regex_triple_double_quote, regex_triple_backtick,
    regex_single_quote, regex_double_quote, regex_backtick, regex_string,
    regex_array, regex_inline_table, regex_table_section, regex_table_array,
    regex_operator, regex_punctuation, regex_comment, regex_scoped_variable,
    regex_whitespace, regex_tilde_block, regex_folder_block, regex_illegal_identifier,
    regex_illegal_special_char
) 

__PRECEDENCE_SPECIFICATION__ = [
    # 1) ILLEGAL_ID must come before IDENTIFIER in order to catch it first
    ('ILLEGAL_ID',  regex_illegal_identifier().pattern),
    ('ILLEGAL_SPECIAL_CHAR', regex_illegal_special_char().pattern),
    ('STRING',      regex_string().pattern),
    ('SCOPED_VAR',  regex_scoped_variable().pattern),
    ('COMMENT',     regex_comment().pattern),
    ('FLOAT',       regex_float().pattern),
    ('INTEGER',     regex_integer().pattern),
    ('BOOLEAN',     regex_boolean().pattern),
    ('NULL',        regex_null().pattern),
    ('RESERVED_FUNC', regex_reserved_functions().pattern),
    ('KEYWORD',     regex_keywords().pattern),
    ('TABLE_ARRAY', regex_table_array().pattern),
    ('TABLE_SECTION', regex_table_section().pattern),
    ('TILDE_BLOCK', regex_tilde_block().pattern),
    ('FOLDER_BLOCK', regex_folder_block().pattern),
    ('INLINE_TABLE', regex_inline_table().pattern),
    ('ARRAY',       regex_array().pattern),
    ('IDENTIFIER',  regex_identifier().pattern),
    ('OPERATOR',    regex_operator().pattern),
    ('PUNCTUATION', regex_punctuation().pattern),
    ('WHITESPACE',  regex_whitespace().pattern),
    ('MISMATCH',    r'.'),
]