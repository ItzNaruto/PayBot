from Bot import app, OWNER_ID

if __name__ == "__main__":
     app.run()
     with app:
        app.send_message(1430742022, "**I'm Successfully Started ✨**")
