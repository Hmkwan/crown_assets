from
werkzeug.urls
import
urlencode
import
sys
sys.modules['werkzeug.urls'].url_encode = urlencode
