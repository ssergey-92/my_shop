"""Start bank app at flask development server."""

if __name__ == '__main__':
    from os import getenv as os_getenv
    from dotenv import load_dotenv
    load_dotenv()

    from bank.routes import app
    app.run(
        debug=True, host=os_getenv("BANK_HOST"), port=os_getenv("BANK_POST"),
    )
