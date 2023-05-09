import tkinter as tk
import threading

import openai

from token_openai import token
openai.api_key = token


class Chat:
    def __init__(self, window: tk.Tk):
        self.window = window
        self.window.title('ChatGPT')
        self.window.geometry('1000x700+450+150')
        # self.window.configure(background='#24303F')
        self.window.configure(bg='#ECECEC')

        self.messages = []
        self.count = 0

        self.initUI()

    def initUI(self):
        self.init_frame_label()
        self.init_frame_history_messages()
        self.init_frame_my_message()
        self.init_frame_buttons()
        self.settings_grid()
        self.settings_adaptation()

    def init_frame_label(self):
        self.frame_info = tk.Frame(self.window, height=1)
        self.info = tk.StringVar()
        self.info.set('ОК')
        self.label_info = tk.Label(self.frame_info, textvariable=self.info)

    def init_frame_history_messages(self):
        self.frame_history_messages = tk.Frame(self.window)
        self.frame_history_messages.configure(bg='#232F3E')
        self.scrollbar_history_messages = tk.Scrollbar(self.frame_history_messages, width=10)
        self.text_history_messages = tk.Text(self.frame_history_messages, width=65, height=15, wrap=tk.WORD,
                                             yscrollcommand=self.scrollbar_history_messages.set, font=('Helvetica', 15),
                                             background='#252F3F', fg='#ECECEC')
        self.text_history_messages.config(state=tk.DISABLED)
        # поменять цвета дл текста кто написал
        self.text_history_messages.tag_configure('blue_text', foreground='#919EAD')
        self.text_history_messages.tag_configure('red_text', foreground='red')

    def init_frame_my_message(self):
        self.frame_my_message = tk.Frame(self.window)

        self.scrollbar_my_message = tk.Scrollbar(self.frame_my_message, width=10)

        self.text_my_message = tk.Text(self.frame_my_message, width=65, height=5,
                                       yscrollcommand=self.scrollbar_my_message.set,
                                       wrap='word', background='#24303F', fg='white', font=('Helvetica', 15),
                                       insertbackground='white', insertwidth=3)
        self.text_my_message.focus()
        self.text_my_message.bind('<Return>', self.send_with_button_return)

    def init_frame_buttons(self):
        self.frame_buttons = tk.Frame(self.window)
        self.frame_buttons.configure(bg='white')

        self.button_send = tk.Button(self.frame_buttons, text='Отправить', command=self.send, bg='#24303F')
        self.button_clean_messages = tk.Button(self.frame_buttons, text='Очистить', command=self.clean_msgs,
                                               bg='#24303F')
        self.label_temperature = tk.Label(self.frame_buttons, text='Температура', width=15, height=1, bg='#ECECEC', fg='black')
        self.spinbox_temperature = tk.Spinbox(self.frame_buttons, from_=0.1, to=2.0, increment=0.1, width=3)

        self.count_messages_history = tk.StringVar()
        self.count_messages_history.set('4')
        self.label_history = tk.Label(self.frame_buttons, text='Запомнить последние сообщения')
        self.entry_history = tk.Entry(self.frame_buttons, textvariable=self.count_messages_history, width=3)


    def settings_grid(self):
        self.frame_info.grid(row=0, column=0, sticky='ew')
        self.label_info.grid(row=0, column=0, sticky='ew')

        self.frame_history_messages.grid(row=1, column=0, sticky='nsew')
        self.text_history_messages.grid(row=0, column=0, sticky='nsew')
        self.scrollbar_history_messages.grid(row=0, column=1, sticky='ns')

        self.frame_my_message.grid(row=2, column=0, sticky='nsew')
        self.text_my_message.grid(row=0, column=0, sticky='ew')
        self.scrollbar_my_message.grid(row=0, column=1, sticky='ns')

        self.frame_buttons.grid(row=3, column=0)
        self.button_send.grid(row=0, column=0)
        self.button_clean_messages.grid(row=0, column=1)
        self.label_temperature.grid(row=0, column=2, sticky='ns')
        self.spinbox_temperature.grid(row=0, column=3)
        self.label_history.grid(row=0, column=4, sticky='ns', ipadx=20)
        self.entry_history.grid(row=0, column=5)

    def settings_adaptation(self):
        self.window.columnconfigure(0, weight=20000)
        # self.window.rowconfigure(0, weight=1)

        self.frame_info.columnconfigure(0, weight=1)
        self.frame_info.rowconfigure(0, weight=1)

        self.window.columnconfigure(1, weight=1)
        self.window.rowconfigure(1, weight=1)

        self.frame_history_messages.columnconfigure(0, weight=1)
        self.frame_history_messages.rowconfigure(0, weight=1)

        self.frame_my_message.columnconfigure(0, weight=1)
        self.frame_my_message.rowconfigure(0, weight=1)

    def clean_msgs(self):
        self.text_history_messages.config(state=tk.NORMAL)
        self.text_history_messages.delete('1.0', tk.END)
        self.text_history_messages.config(state=tk.DISABLED)

        self.messages.clear()

    def write_on_msgs_text(self, who, msg):
        # now = datetime.datetime.now()
        # hour_minute = '{:%H:%M:%S}'.format(now)
        self.text_history_messages.config(state=tk.NORMAL)
        if who == 1:
            self.text_history_messages.insert(tk.END, f'User: ', 'blue_text')
            self.text_history_messages.insert(tk.END, f'{msg}')
        else:
            self.text_history_messages.insert(tk.END, f'ChatGPT: ', 'red_text')
            self.text_history_messages.insert(tk.END, f'{msg}\n')
            self.text_history_messages.insert(tk.END, '-' * 139 + '\n')

        self.text_history_messages.config(state=tk.DISABLED)

    def send_with_button_return(self, event):
        self.send()
        return 'break'

    def send(self):
        msg = self.text_my_message.get('1.0', tk.END)

        if len(msg) <= 1:
            self.info.set('Введите запрос')
            return None

        self.write_on_msgs_text(1, msg)

        self.text_my_message.delete('1.0', tk.END)
        thread_send_openai = threading.Thread(target=self._send_openai, args=(msg,))
        thread_send_openai.start()

    def _send_openai(self, msg):
        count = int(self.count_messages_history.get())
        if len(self.messages) > count * 2 - 1:
            [self.messages.pop(0) for _ in range(2)]

        self.messages.append({"role": "user", "content": msg})

        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.messages,
                temperature=float(self.spinbox_temperature.get())
            )
        except openai.error.APIConnectionError as exc:
            self.info.set('Проверьте соединение')
            self.label_info.configure(bg='red')
            self.messages.pop()
            return None
        except openai.error.RateLimitError as exc:
            self.info.set('Напишите повторно через 5 секунд, последнее сообщение удалено')
            self.label_info.configure(bg='yellow')
            self.messages.pop()
            return None
        except openai.error.InvalidRequestError as exc:
            self.label_info.configure(bg='yellow')
            self.info.set('Превышен лимит токенов для ChatGPT, удалены первые 2 сообщения, напишите запрос повторно')
            self.messages.pop()
            [self.messages.pop(0) for _ in range(4)]
            return None
        else:
            self.info.set('ОК')
            self.label_info.configure(bg='#ECECEC')

        chat_response = completion.choices[0].message.content

        self.messages.append({"role": "assistant", "content": chat_response})
        self.write_on_msgs_text(0, chat_response)


if __name__ == '__main__':
    root = tk.Tk()
    application = Chat(root)
    root.mainloop()
