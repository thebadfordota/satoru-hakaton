from squats import detect_squats
from pushups import detect_pushups
from emotions import detect_emotions

def main(task: str) -> None:
    if task == 'squats':
        detect_squats()
    elif task == 'pushups':
        detect_pushups()
    elif task == 'emotions':
        detect_emotions()
    else:
        return

if __name__ == '__main__':
    main('emotions')