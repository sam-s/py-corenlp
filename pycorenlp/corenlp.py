import json, requests

class NoStanfordCoreNLPServer(Exception):
    def __init__(self, server_url):
        self.server_url = server_url

    def __str__(self):
        return ('Cannot connect to <%s>.\nPlease start the CoreNLP server, e.g.:\n'
                '$ cd stanford-corenlp-full-2015-12-09/\n'
                '$ java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer'
                % (self.server_url))

class StanfordCoreNLPError(Exception):
    def __init__(self, reason, message):
        self.reason = reason
        self.message = message

    def __str__(self):
        return "%s(%s): %s" % (self.__class__.__name__,self.reason,self.message)

class StanfordCoreNLP:
    def __init__(self, server_url):
        if server_url[-1] == '/':
            server_url = server_url[:-1]
        self.server_url = server_url

    def annotate(self, text, properties=None):
        assert isinstance(text, str)
        if properties is None:
            properties = {}
        else:
            assert isinstance(properties, dict)

        # Checks that the Stanford CoreNLP server is started.
        try:
            requests.get(self.server_url)
        except requests.exceptions.ConnectionError:
            raise NoStanfordCoreNLPServer(self.server_url)

        r = requests.post(
            self.server_url, params={
                'properties': str(properties)
            }, data=text.encode(), headers={'Connection': 'close'})
        if not r.ok:
            raise StanfordCoreNLPError(r.reason, r.text)
        if properties.get('outputFormat') == 'json':
            return json.loads(r.text)
        return r.text

    def tokensregex(self, text, pattern, filter):
        return self.regex('/tokensregex', text, pattern, filter)

    def semgrex(self, text, pattern, filter):
        return self.regex('/semgrex', text, pattern, filter)

    def regex(self, endpoint, text, pattern, filter):
        r = requests.get(
            self.server_url + endpoint, params={
                'pattern':  pattern,
                'filter': filter
            }, data=text)
        if not r.ok:
            raise StanfordCoreNLPError(r.reason, r.text)
        return json.loads(r.text)
