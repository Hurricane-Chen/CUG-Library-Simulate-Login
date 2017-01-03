import libApi

def create_app():
    app = libApi.app
    return app

application = create_app()

if __name__ == "__main__":
    application.run()

