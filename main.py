from dotenv import load_dotenv
load_dotenv()
from kivy import app
from AI import Assistant

class MykivyApp(app.App):
    def build(self):
        AI = Assistant()
        AI.start_listening()

        if AI.start_listening:
            print("AI is in listening mode.")




        return AI


if __name__ == '__main__':
    MykivyApp = MykivyApp()
    MykivyApp.run()