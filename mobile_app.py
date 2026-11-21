"""Мобильный UI NeuroAgent на Kivy — точка входа APK."""
import os

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from agent import Agent
from llm import LLMClient
import tools


class ChatBubble(Label):
    """Одно сообщение в истории чата."""

    def __init__(self, text: str, is_user: bool, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.is_user = is_user
        self.size_hint_y = None
        self.bind(texture_size=self._update_height)
        self.markup = False
        self.padding = (12, 8)
        if is_user:
            self.color = (0.15, 0.55, 0.95, 1)  # синий — пользователь
        else:
            self.color = (0.1, 0.6, 0.3, 1)  # зелёный — агент
        self.bold = True

    def _update_height(self, *_):
        self.height = self.texture_size[1] + 16


class NeuroAgentApp(App):
    busy = BooleanProperty(False)

    def build(self):
        self.title = "NeuroAgent"
        root = BoxLayout(orientation="vertical", padding=8, spacing=6)

        # История чата
        self.history_box = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None)
        self.history_box.bind(
            minimum_height=self.history_box.setter("height")
        )
        scroll = ScrollView()
        scroll.add_widget(self.history_box)
        root.add_widget(scroll)

        # Поле ввода + кнопка
        input_row = BoxLayout(orientation="horizontal", spacing=6, size_hint_y=None, height=48)
        self.input_field = TextInput(
            hint_text="Спросите что-нибудь…",
            multiline=False,
            write_tab=False,
        )
        self.input_field.bind(on_text_validate=self.on_send)
        send_btn = Button(text="➤", size_hint_x=None, width=56)
        send_btn.bind(on_press=self.on_send)
        input_row.add_widget(self.input_field)
        input_row.add_widget(send_btn)
        root.add_widget(input_row)

        # Агент инициализируется лениво — чтобы экран открылся сразу
        self.agent = None
        self.add_message("NeuroAgent готов. Настройте LLM_API_KEY / LLM_BASE_URL / LLM_MODEL "
                         "(см. README) и задайте вопрос.", is_user=False)
        return root

    def _ensure_agent(self):
        if self.agent is None:
            llm = LLMClient()
            self.agent = Agent(llm, tools.TOOLS, tools.run_tool, max_steps=8)

    def add_message(self, text: str, is_user: bool):
        bubble = ChatBubble(text, is_user)
        self.history_box.add_widget(bubble)
        # Прокрутка вниз при новом сообщении
        Clock.schedule_once(
            lambda dt: self._scroll_to_bottom(), 0
        )

    def _scroll_to_bottom(self):
        scroll = self.history_box.parent
        if scroll is not None:
            scroll.scroll_y = 0

    def on_send(self, *_):
        if self.busy:
            return
        text = self.input_field.text.strip()
        if not text:
            return
        self.input_field.text = ""
        self.add_message(text, is_user=True)
        self.busy = True
        self.add_message("…думаю", is_user=False)

        # Ответ агента считаем в следующем кадре, чтобы UI не завис
        Clock.schedule_once(lambda dt: self._run_agent(text), 0)

    def _run_agent(self, text: str):
        try:
            self._ensure_agent()
            answer = self.agent.run(text)
        except Exception as exc:
            answer = f"Ошибка: {exc}"
        # Заменяем «…думаю» на реальный ответ
        self.history_box.remove_widget(self.history_box.children[0])
        self.add_message(answer, is_user=False)
        self.busy = False


if __name__ == "__main__":
    NeuroAgentApp().run()
