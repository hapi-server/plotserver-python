import flask
from shelljob import proc
from time import sleep
from flask import send_file

#Seems to not be needed anymore although used at [1].
#import eventlet
#eventlet.monkey_patch()

app = flask.Flask(__name__)

@app.route( '/stream' )
def stream():

    if False:  # Also works

        g = proc.Group()
        p = g.run( [ "bash", "-c", "for ((i=0;i<5;i=i+1)); do echo $i; sleep 1; done" ] )

        def read_process():
            while g.is_pending():
                lines = g.readlines()
                for proc, line in lines:
                    # Two newlines needed to signal end of event to browser.
                    yield "data:" + line.decode().rstrip() + "\n\n"


        return flask.Response(read_process(), mimetype='text/event-stream')

    def read_process2():
        for i in range(4):
            sleep(1)
            yield "data:" + str(i) + "\n" + "id:" + str(i) + "\n\n"
        yield "data:https://google.com/" + "\n" + "id:-1\n\n"

    return flask.Response(read_process2(), mimetype='text/event-stream')


@app.route('/')
def get_page():
    return flask.send_file('log.htm')


# Serve static file; used to serve tail.htm with CORS (via methods=...).
@app.route("/<path:filename>", methods=['GET', 'HEAD', 'POST', 'OPTIONS'])
def staticfile(filename):
    return send_file(filename)


if __name__ == "__main__":
    app.run(debug=True)