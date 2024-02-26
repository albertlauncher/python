# Albert Local Bookmark Plugin

Open the URLs defined in the local plain text file.

## The format of the bookmark file

```
# Keyword 1
http://example1.com

# Keyword 2, Keyword 3
http://example2.com

# keyword 4
http://a.example3.com
http://b.example3.com

# Keyword 5
http://a.example4.com

# Keyword 5
http://b.example4.com
```

That is:
- The keywords are preceded by a `#` and are comma-separated, and the URLs are listed below the keywords.
- Empty lines are ignored.
- The keyword and URL mappings can be 1 to 1, 1 to many, or many to 1.
- URLs with the same keyword are allowed, as the "Keyword 5" shown in the example above.
- Keywords are case-insensitive.
