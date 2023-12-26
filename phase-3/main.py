from gamedis import createApp
from decouple import config as en_var  # import the environment var


if __name__ == "__main__":
    app = createApp()
    app.run(debug=True, port=en_var("port", 5500))
