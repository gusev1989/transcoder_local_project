import io
import os
import subprocess
import sys
import platform
import PySimpleGUI as sg

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

settings_file_path = "settings.txt"

with open(settings_file_path, "r") as settings_file:
    settings = settings_file.read().splitlines()
    ffmpeg_path = settings[0]
    ffprobe_path = settings[1]

layout = [
    [sg.Text('Путь к файлу: ')],
    [sg.Input(key='input_file', disabled=True), sg.FileBrowse(key='browse_file')],
    [sg.Button('Вызвать ffprobe')],
    [sg.Text('Входящие дорожки: ')],
    [sg.Multiline(key='result', size=(45, 10), disabled=True)],
    [sg.Text('Добавить аудио дорожки'), sg.Checkbox('', key='add_audio')],
    [sg.Text('Введите количество аудиодорожек для выбора: ')],
    [sg.Input(key='audio_tracks_count')],
    [sg.Text('Добавить субтитры: '), sg.Checkbox('', key='add_subtitles')],
    [sg.Text('Введите количество дорожек субтитров: ')],
    [sg.Input(key='subtitles_tracks_count')],
    [sg.Text('Результат: ')],
    [sg.Text(key='output_path')],
    [sg.Button('Запустить кодирование')]
]

window = sg.Window('FFmpeg Converter', layout)

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break

    if event == 'Вызвать ffprobe':
        input_file = values['input_file']
        command = (f"{ffprobe_path} -v quiet -show_entries stream=index,language"
                   f"codec_type,codec_name:stream_tags=title,language -of csv=p=0 \"{input_file}\"")
        result = subprocess.check_output(command, shell=True, encoding='utf-8')
        window['result'].update(result)

    if event == 'Запустить кодирование':
        input_file = values['input_file']
        audio_tracks_count = values['audio_tracks_count']
        add_subtitles = values['add_subtitles']
        add_audio = values['add_audio']
        subtitles_tracks_count = values['subtitles_tracks_count']

        audio_tracks = ""
        subtitles_tracks = ""
        audio_cache = []
        if add_audio:
            for i in range(int(audio_tracks_count)):
                audio_track = sg.popup_get_text(f"Введите номер {i + 1}-й аудиодорожки:")
                if (audio_track is None
                        or audio_track == ""
                        or audio_track in audio_cache):
                    sg.popup("Такой номер дорожки уже был,"
                             "или дорожка не указана ")
                    break
                audio_tracks += f" -map 0:{audio_track}"
                audio_cache.append(audio_track)
        subtitles_cache = []

        if add_subtitles:
            for i in range(int(subtitles_tracks_count)):
                subtitles_track = sg.popup_get_text(f"Введите номер {i + 1}-й дорожки субтитров:")
                if (subtitles_track is None
                        or subtitles_track == ""
                        or subtitles_track in subtitles_cache):
                    sg.popup("Такой номер дорожки уже был,"
                             "или дорожка не указана ")
                    break
                subtitles_tracks += f" -map 0:{subtitles_track}"
                subtitles_cache.append(subtitles_track)

        output_path = f"{input_file}_result.mp4"
        video_tracks = "-map 0:v"
        params = "-c:v copy -c:a copy -c:s mov_text -f mp4"
        window['output_path'].update(output_path)

        start = sg.popup('Запускаем ffmpeg? \n'
                         'Это займет немного времени'
                         , button_type=sg.POPUP_BUTTONS_YES_NO)
        if input_file == "":
            sg.popup('Не указан исходный файл!')
            continue
        if start == 'Yes':
            pass
        else:
            continue

        command = (f"{ffmpeg_path} -y -i \"{input_file}\""
                   f" {video_tracks}{audio_tracks}{subtitles_tracks}"
                   f" {params} \"{output_path}\"")
        subprocess.call(command, shell=True)
        file_path = os.path.abspath(output_path)
        sg.popup('FFmpeg выполнен успешно!')#, auto_close=True, auto_close_duration=2)
        #subprocess.call(f'explorer /select,"{file_path}"', shell=True)
        if platform.system() == "Windows":
            subprocess.call(f'explorer /select,"{file_path}"', shell=True)
        if platform.system() == "Linux":
            subprocess.call(["xdg-open", file_path])
        else:
            print("Операционная система не поддерживается.")

window.close()
