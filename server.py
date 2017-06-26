import sqlite3, os
from flask import Flask, request, g, render_template, make_response
from metadata import Metadata
from lxml import etree

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update({
    'DATABASE'      : os.path.join(app.root_path, 'dev.db'),
    'SECRET_KEY'    : 'devkey',
    'USERNAME'      : 'admin',
    'PASSWORD'      : 'default'
    })
app.config.from_envvar('PLUGIN_REPO_SETTINGS', silent=True)


def dict_factory(cursor, row):
    """Function to turn DB queries into dicts"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = dict_factory
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/plugin-release', methods = ['POST'])
def event_handler():
    """Handle POST requests by Github Webhooks
    """
    if request.headers.get('X-GitHub-Event') == 'release':
        repository = request.json.get('repository')
        release = request.json.get('release')
        m = Metadata(repository, release)
        entry = m.getMetadata()
        if entry:
            db = get_db()
            print entry
            db.execute('''
                INSERT INTO plugins
                (name, version, version_major, version_minor, version_revision,
                description, qgis_minimum_version, qgis_maximum_version,
                homepage, file_name, author_name, download_url, uploaded_by,
                create_date, update_date, experimental)
                VALUES
                (:name, :version, :version_major, :version_minor, :version_revision,
                :description, :qgis_minimum_version, :qgis_maximum_version,
                :homepage, :file_name, :author_name, :download_url, :uploaded_by,
                :create_date, :update_date, :experimental)
                ''', entry)
            db.commit()
        else:
            return "metadata invalid"
        return "received valid request"
    else:
        return "invalid request"

@app.route('/plugins.xml')
def show_plugin_list():
    """Generate XML with plugins"""
    db = get_db()
    cur = db.execute('SELECT * FROM plugins')
    plugins = cur.fetchall()
    selection = request.args.get('selection')
    plugins = get_plugin_selection(plugins, selection = selection)
    root = etree.Element('plugins')
    for p in plugins:
        child = etree.Element('pyqgis_plugin', name = p.get('name'), version = p.get('version'))
        props = ['description', 'version', 'trusted', 'qgis_minimum_version', 'qgis_maximum_version',
                'homepage', 'file_name', 'author_name', 'download_url', 'uploaded_by', 'create_date',
                'update_date', 'experimental', 'deprecated', 'tracker', 'repository', 'tags']
        for k in props:
            subelement = etree.SubElement(child, k)
            subelement.text = str(p.get(k))
        root.append(child)
    response = make_response(etree.tostring(root))
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.route('/plugins.html')
def show_plugins():
    """Display the list of available plugins"""
    db = get_db()
    cur = db.execute('SELECT * FROM plugins')
    plugins = cur.fetchall()
    selection = request.args.get('selection')
    plugins = get_plugin_selection(plugins, selection = selection)
    template = render_template('plugins.html', plugins = plugins)
    response = make_response(template)
    return response

def get_plugin_selection(plugins, selection):
    """Extract the latest version of each plugin"""
    if not selection in ['last','latest']:
        return plugins
    res = []
    # for every distinct plugin name
    for name in set(map(lambda x: x.get('name'), plugins)):
        pl_name = filter(lambda x: x.get('name') == name, plugins)
        pl_sorted = sorted(pl_name, key =
                lambda k: (k.get('version_major'), k.get('version_minor'), k.get('version_revision')))
        if selection == 'latest':
            res.append(pl_sorted.pop())
        if selection == 'last':
            if len(pl_sorted) > 1:
                res.append(pl_sorted[len(pl_sorted) - 2])
            else:
                res.append(pl_sorted.pop())
    return res

if __name__ == '__main__':
    app.run()
