import HTMLParser
import urlparse
import urllib

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

class ENLHTMLParser(HTMLParser.HTMLParser):
    """A simple parser which exchange relative URLs with absolute ones"""

    def __init__(self, context):

        self.context = context
        self.html = u""
        self.image_urls = []
        self.image_number = 0

        HTMLParser.HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        """
        """
        self.html += u"<%s" % tag


        for attr in attrs:
            if attr[0] == "href":
                try:
                    # split anchor from url
                    baseurl, anchor = urlparse.urldefrag(attr[1])
                    o = self.context.restrictedTraverse(urllib.unquote(baseurl))
                    if getattr(o, 'absolute_url', None):
                        url = o.absolute_url()
                    else:
                        # maybe we got a view instead of an traversal object:
                        if getattr(o, 'context', None):
                            url = o.context.absolute_url()
                        else:
                            url = attr[1]
                    if anchor:
                        url = '#' + anchor
                except:
                    url = attr[1]
                if isinstance(url, unicode):
                    plone_utils = getToolByName(self.context, 'plone_utils')
                    encoding = plone_utils.getSiteEncoding()
                    url = url.encode(encoding)
                self.html += u' href="%s"' % url
            else:
                self.html += u' %s="%s"' % (attr)

        self.html += u">"

    def handle_endtag(self, tag):
        """
        """
        self.html += u"</%s>" % tag

    def handle_data(self, data):
        """
        """
        self.html += safe_unicode(data)

    def handle_charref(self, name):
        self.html += u"&#%s;" % name

    def handle_entityref(self, name):
        self.html += u"&%s;" % name

    def handle_comment(self, data):
        self.html += u"<!--%s-->" % data

    def handle_decl(self, decl):
        self.html += u"<!%s>" % decl

    def handle_startendtag(self, tag, attrs):
        """
        """
        self.html += u"<%s" % tag
        for attr in attrs:
            if attr[0] == u"src":
                if attr[1].startswith(self.context.portal_url()):
                    self.html += u' src="cid:image_%s"' % self.image_number
                    self.image_number += 1
                    path = attr[1][len(self.context.portal_url()):]
                    path = '/'.join(self.context.getPhysicalPath()) + path
                    self.image_urls.append(path)
                elif u'http' in attr[1]:
                    url = attr[1]
                    self.html += u' src="%s"' % url
                else:
                    self.html += u' src="cid:image_%s"' % self.image_number
                    self.image_number += 1
                    self.image_urls.append(attr[1])
            else:
                self.html += u' %s="%s"' % (attr)

        self.html += u" />"
