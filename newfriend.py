import os
import cherrypy
from nbt import nbt
import requests
import json
import uuid
import newfriendconfig

NBT_FILE_PATH = ""


class ByUsername(object):
    exposed = True

    @cherrypy.tools.accept(media='text/plain')
    def GET(self, username=None):
        r = requests.get("https://api.mojang.com/users/profiles/minecraft/" + username)
        if r.status_code == 200:
            resp = json.loads(r.content)
            id = resp["id"]
            valid_id = uuid.UUID(id)
            try:
                nbt_file = nbt.NBTFile(sanitize(NBT_FILE_PATH + str(valid_id) + ".dat"), "rb")
                for tag in nbt_file["bukkit"].tags:
                    if tag.name == "firstPlayed":
                        return json.dumps({"uuid": str(valid_id),"joindate": str(tag.value)})
                return json.dumps({"uuid": str(valid_id),"joindate": "old"})
            except IOError :
                return json.dumps({"uuid": str(valid_id),"joindate": "unknown"})
        else:
            return json.dumps({"uuid": "none","joindate": "unknown"})


class ByUUID(object):
    exposed = True

    @cherrypy.tools.accept(media='text/plain')
    def GET(self, uuid=None):
        try:
            nbt_file = nbt.NBTFile(sanitize(NBT_FILE_PATH + uuid + ".dat"), "rb")
            for tag in nbt_file["bukkit"].tags:
                if tag.name == "firstPlayed":
                    return json.dumps({"uuid": str(uuid),"joindate": str(tag.value)})
            return json.dumps({"uuid": str(uuid),"joindate": "old"})
        except IOError :
            return json.dumps({"uuid": str(uuid),"joindate": "unknown"})


class WebService:
    # a blocking call that starts the web application listening for requests
    def start(self, port=80):
        cherrypy.config.update({'server.socket_host': '0.0.0.0',})
        cherrypy.config.update({'server.socket_port': port,})
        cherrypy.engine.start()
        cherrypy.engine.block()

    # stops the web application
    def stop(self):
        cherrypy.engine.stop()


# Dummy class for static file serving
class Root(object):
    pass


def main():
    path = os.path.abspath(os.path.dirname(__file__))
    config = newfriendconfig.Configuration(path + os.sep + "config.json")
    global NBT_FILE_PATH
    NBT_FILE_PATH = config.nbt_file_path
    api_config = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        }
    }
    app_config = {
        '/': {
            # enable serving up static resource files
            'tools.staticdir.root': path,
            'tools.staticdir.on': True,
            'tools.staticdir.dir': "static",
            'tools.staticdir.index': 'index.html',
        },
    }

    if config.frontend:
        cherrypy.tree.mount(Root(), '/', config=app_config)
    cherrypy.tree.mount(ByUUID(), '/a/uuid/', config=api_config)
    cherrypy.tree.mount(ByUsername(), '/a/username/', config=api_config)

    web = WebService()
    try:
        web.start(port=config.port)
    except KeyboardInterrupt:
        web.stop()


def sanitize(file_name):
    sanitized = os.path.normpath(os.sep + file_name).lstrip(os.sep)
    return sanitized


if __name__ == '__main__':
    main()