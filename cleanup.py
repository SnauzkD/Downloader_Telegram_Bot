import shutil


class CleanUp:
    def clean(self, user_folder):
        if user_folder.exists():
            shutil.rmtree(user_folder)
