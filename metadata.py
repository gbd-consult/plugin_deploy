import requests
import ConfigParser
import StringIO

class Metadata():

    def __init__(self, repository, release):
        self.repository = repository
        self.release = release
        repo = repository.get('full_name')
        tag = release.get('tag_name')
        self.url = 'https://raw.githubusercontent.com/{}/{}/metadata.txt'.format(repo, tag)

    def getMetadata(self):
        r = requests.get(self.url)
        if r.status_code == requests.codes.ok:
            conf = ConfigParser.ConfigParser()
            buf = StringIO.StringIO(r.text)
            try:
                conf.readfp(buf)
            except:
                print "could not parse metadata"
                return {}

            if conf.get('general','experimental') == "True":
                experimental = 1
            else:
                experimental = 0
            metadata = {
                    'name'                  : conf.get('general','name'),
                    'version'               : self.release.get('tag_name'),
                    'description'           : conf.get('general','description'),
                    'qgis_minimum_version'  : conf.get('general','qgisMinimumVersion'),
                    'qgis_maximum_version'  : conf.get('general','qgisMaximumVersion'),
                    'homepage'              : self.release.get('html_url'),
                    'file_name'             : "tbd",
                    'author_name'           : conf.get('general','author'),
                    'download_url'          : self.release.get('zipball_url'),
                    'uploaded_by'           : self.release.get('author').get('login'),
                    'create_date'           : "tbd",
                    'update_date'           : "tbd",
                    'experimental'          : conf.get('general','experimental')
                    }
            return metadata
        print "could not open url"
        return {}
