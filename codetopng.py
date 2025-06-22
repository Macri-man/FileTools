from pygments import highlight
from pygments.lexers import PythonLexer  # Change if you want other languages
from pygments.formatters import ImageFormatter

code = '''
def hello_world():
    print("Hello, world!")
'''

# Customize font, style, and line numbers here:
formatter = ImageFormatter(
    font_name='DejaVu Sans Mono',
    font_size=18,
    line_numbers=True,
    style='monokai',
    image_pad=10
)

# Generate highlighted image and save to file
with open('code_snippet.png', 'wb') as f:
    f.write(highlight(code, PythonLexer(), formatter))
    
print("Image saved as code_snippet.png")
