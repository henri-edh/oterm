import json
from typing import Iterable

from textual import on, work
from textual.app import App, ComposeResult, SystemCommand
from textual.screen import Screen
from textual.widgets import Footer, Header, TabbedContent, TabPane

from oterm.app.chat_edit import ChatEdit
from oterm.app.chat_export import ChatExport, slugify
from oterm.app.splash import SplashScreen
from oterm.app.widgets.chat import ChatContainer
from oterm.config import appConfig
from oterm.store.store import Store


class OTerm(App):
    TITLE = "oTerm"
    SUB_TITLE = "A terminal-based Ollama client."
    CSS_PATH = "oterm.tcss"
    BINDINGS = [
        ("ctrl+tab", "cycle_chat(+1)", "next chat"),
        ("ctrl+shift+tab", "cycle_chat(-1)", "prev chat"),
        ("ctrl+q", "quit", "quit"),
    ]

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)
        yield SystemCommand("New chat", "Creates a new chat", self.action_new_chat)
        yield SystemCommand(
            "Edit chat parameters",
            "Allows to redefine model parameters and system prompt",
            self.action_edit_chat,
        )
        yield SystemCommand(
            "Rename chat", "Renames the current chat", self.action_rename_chat
        )
        yield SystemCommand(
            "Delete chat", "Deletes the current chat", self.action_delete_chat
        )
        yield SystemCommand(
            "Export chat",
            "Exports the current chat as Markdown (in the current working directory)",
            self.action_export_chat,
        )

    async def action_quit(self) -> None:
        return self.exit()

    async def action_cycle_chat(self, change: int) -> None:
        tabs = self.query_one(TabbedContent)
        store = await Store.get_store()
        saved_chats = await store.get_chats()
        if tabs.active_pane is None:
            return
        active_id = int(str(tabs.active_pane.id).split("-")[1])
        for _chat in saved_chats:
            if _chat[0] == active_id:
                next_index = (saved_chats.index(_chat) + change) % len(saved_chats)
                next_id = saved_chats[next_index][0]
                tabs.active = f"chat-{next_id}"
                break

    @work
    async def action_new_chat(self) -> None:
        store = await Store.get_store()
        model_info: str | None = await self.push_screen_wait(ChatEdit())
        if not model_info:
            return
        model: dict = json.loads(model_info)
        tabs = self.query_one(TabbedContent)
        tab_count = tabs.tab_count
        name = f"chat #{tab_count+1} - {model['name']}"
        id = await store.save_chat(
            id=None,
            name=name,
            model=model["name"],
            system=model["system"],
            format=model["format"],
            parameters=json.dumps(model["parameters"]),
            keep_alive=model["keep_alive"],
        )
        pane = TabPane(name, id=f"chat-{id}")
        pane.compose_add_child(
            ChatContainer(
                db_id=id,
                chat_name=name,
                model=model["name"],
                system=model["system"],
                format=model["format"],
                parameters=model["parameters"],
                keep_alive=model["keep_alive"],
                messages=[],
            )
        )
        await tabs.add_pane(pane)
        tabs.active = f"chat-{id}"

    async def action_edit_chat(self) -> None:
        tabs = self.query_one(TabbedContent)
        if tabs.active_pane is None:
            return
        chat = tabs.active_pane.query_one(ChatContainer)
        chat.action_edit_chat()

    async def action_rename_chat(self) -> None:
        tabs = self.query_one(TabbedContent)
        if tabs.active_pane is None:
            return
        chat = tabs.active_pane.query_one(ChatContainer)
        chat.action_rename_chat()

    async def action_delete_chat(self) -> None:
        tabs = self.query_one(TabbedContent)
        if tabs.active_pane is None:
            return
        chat = tabs.active_pane.query_one(ChatContainer)
        store = await Store.get_store()
        await store.delete_chat(chat.db_id)
        await tabs.remove_pane(tabs.active)

    async def action_export_chat(self) -> None:
        tabs = self.query_one(TabbedContent)
        if tabs.active_pane is None:
            return
        chat = tabs.active_pane.query_one(ChatContainer)
        screen = ChatExport()
        screen.chat_id = chat.db_id
        screen.file_name = f"{slugify(chat.chat_name)}.md"
        self.push_screen(screen)

    async def on_mount(self) -> None:
        store = await Store.get_store()
        self.dark = appConfig.get("theme") == "dark"
        saved_chats = await store.get_chats()
        if not saved_chats:
            self.action_new_chat()
        else:
            tabs = self.query_one(TabbedContent)
            for id, name, model, system, format, parameters, keep_alive in saved_chats:
                messages = await store.get_messages(id)
                container = ChatContainer(
                    db_id=id,
                    chat_name=name,
                    model=model,
                    messages=messages,
                    system=system,
                    format=format,
                    parameters=parameters,
                    keep_alive=keep_alive,
                )
                pane = TabPane(name, container, id=f"chat-{id}")
                tabs.add_pane(pane)
        await self.push_screen(SplashScreen())

    @on(TabbedContent.TabActivated)
    async def on_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        container = event.pane.query_one(ChatContainer)
        await container.load_messages()

    def compose(self) -> ComposeResult:
        yield Header()
        yield TabbedContent(id="tabs")
        yield Footer()


app = OTerm()