
## Installation

```bash
pip install git+http://muteklab.com:9000/root/python-mstr.git
```

```bash
pip uninstall mstr
```

## Example

```python
from mstr import mstr
mstr('string').get_pattern_index('pattern')
mstr('string').get_pattern_index_from_to('pattern_from', 'pattern_to')
mstr('string').remove_pattern('pattern')
mstr('string').tokenize(r'[a|b]', remain=True)
mstr('string').msplit(r'[a|b]')
mstr('string').mstrip(r'[a|b]')
mstr('string').mreplace('c<a|b')
mstr('string').mmreplace('b<a|d<c')
mstr('string').mcapitalize('a|b')
mstr('string').insert(0, 'inserted')
mstr('string').auto_bracket()
mstr('string').remove_after('pattern')
mstr('string').place_dot_between()
mstr('string').lower_after_wordbase('a')
mstr('string').get_alpha_tags()
mstr('string').get_hash_tags()
mstr('string').guess_datetime()
mstr('string').ymd_to_digit()
mstr('string').month_to_digit()
mstr('string').week_to_digit()
mstr('string').get_md5()
mstr('string').get_sha256()
mstr('string').get_path_split(0)
```

## Repository

```bash
git clone http://muteklab.com:9000/root/python-mstr.git
```
