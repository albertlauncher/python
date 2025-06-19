# -*- coding: utf-8 -*-

from pathlib import Path
from subprocess import run, CalledProcessError
import json

from albert import *

# Metadata for the Albert plugin
md_iid = "3.0"  # Interface ID for Albert plugin compatibility
md_version = "3.1.1"  # Plugin version
md_name = "Bitwarden"  # Plugin name displayed in Albert
md_description = """
A wrapper extension for the 'rbw' Bitwarden CLI client. This plugin allows quick access to Bitwarden vault entries,
enabling users to copy passwords, usernames, auth codes, URIs, and custom fields directly from the Albert interface.
Fields are displayed in the Alt menu with values shown for non-hidden fields (e.g., username, URIs), while sensitive
fields like passwords remain obscured.
"""
md_license = "MIT"  # License under which the plugin is distributed
md_url = "https://github.com/albertlauncher/python/tree/main/bitwarden"  # URL for plugin source or documentation
md_authors = ["@ovitor", "@daviddeadly", "@manuelschneid3r"]  # Contributors to the plugin
md_bin_dependencies = ["rbw"]  # Required external binary (Bitwarden CLI)

class Plugin(PluginInstance, TriggerQueryHandler):
    """
    Bitwarden Plugin for Albert

    This plugin integrates with the 'rbw' CLI to provide a seamless interface for managing Bitwarden vault entries.
    It supports searching entries by name or username, and offers a prioritized list of actions in the Alt menu.

    Usage:
    - Trigger the plugin with 'bw ' followed by a search term (e.g., 'bw ministry').
    - Press Enter on an item to copy its password to the clipboard (default action).
    - Hold Alt to view all available actions for the selected item, including:
        1. Copy password (hidden)
        2. Copy username (value shown)
        3. Copy auth code
        4. Copy uri_1 (value shown)
        5. Other fields (values shown unless tagged 'hidden' in Bitwarden)
        6. Edit entry in terminal (opens 'rbw edit' in a persistent terminal)
    - Type 'bw sync' to synchronize the vault with the Bitwarden server.

    Features:
    - Field values are displayed in the Alt menu for non-hidden fields (e.g., 'Copy username: user@example.com').
    - Hidden fields (e.g., passwords) show only the field name (e.g., 'Copy password').
    - Actions are ordered for quick access to common fields, with password as the default.
    - Supports custom fields, URIs, and notes as defined in the Bitwarden entry.

    Dependencies:
    - Requires 'rbw' (Rust Bitwarden CLI) installed and configured on the system.
    """

    iconUrls = [f"file:{Path(__file__).parent}/bw.svg"]  # Icon for the plugin in Albert

    def __init__(self):
        PluginInstance.__init__(self)
        TriggerQueryHandler.__init__(self)

    def defaultTrigger(self):
        return 'bw '  # Default trigger prefix for the plugin

    def handleTriggerQuery(self, query):
        """Handle user queries and populate the result list."""
        query_string = query.string.strip().lower()
        info(f"Handling query: {query_string}")

        if query_string == "sync":
            query.add(
                StandardItem(
                    id="sync",
                    text="Sync Bitwarden Vault",
                    iconUrls=self.iconUrls,
                    actions=[
                        Action(
                            id="sync",
                            text="Syncing Bitwarden Vault",
                            callable=lambda: run(["rbw", "sync"])
                        )
                    ]
                )
            )
            return

        for p in self._filter_items(query, query_string):
            fields = self._get_item_fields(p["id"])
            actions = []

            if "error" not in fields:
                # 1. Password (default action for Enter)
                if "password" in fields:
                    actions.append(
                        Action(
                            id="copy_password",
                            text="Copy password" if fields["password"]["hidden"] else f"Copy password: {fields['password']['value']}",
                            callable=lambda value=fields["password"]["value"]: setClipboardText(text=value)
                        )
                    )
                # 2. Username
                if "username" in fields:
                    actions.append(
                        Action(
                            id="copy_username",
                            text="Copy username" if fields["username"]["hidden"] else f"Copy username: {fields['username']['value']}",
                            callable=lambda value=fields["username"]["value"]: setClipboardText(text=value)
                        )
                    )
                # 3. Auth Code
                actions.append(
                    Action(
                        id="copy-auth",
                        text="Copy auth code",
                        callable=lambda item=p: self._code_to_clipboard(item)
                    )
                )
                # 4. First URI (uri_1)
                if "uri_1" in fields:
                    actions.append(
                        Action(
                            id="copy_uri_1",
                            text="Copy uri_1" if fields["uri_1"]["hidden"] else f"Copy uri_1: {fields['uri_1']['value']}",
                            callable=lambda value=fields["uri_1"]["value"]: setClipboardText(text=value)
                        )
                    )
                # 5. All other fields
                for field_name, field_info in fields.items():
                    if field_name not in ["password", "username", "uri_1"]:
                        actions.append(
                            Action(
                                id=f"copy_{field_name}",
                                text=f"Copy {field_name}" if field_info["hidden"] else f"Copy {field_name}: {field_info['value']}",
                                callable=lambda value=field_info["value"]: setClipboardText(text=value)
                            )
                        )
            else:
                info(f"Skipping fields for {p['path']} due to error: {fields['error']}")
                actions.append(
                    Action(
                        id="copy_password",
                        text="Copy password",
                        callable=lambda item=p: self._password_to_clipboard(item)
                    )
                )
                actions.append(
                    Action(
                        id="copy-auth",
                        text="Copy auth code",
                        callable=lambda item=p: self._code_to_clipboard(item)
                    )
                )

            # 6. Edit entry in terminal
            actions.append(
                Action(
                    id="edit",
                    text="Edit entry in terminal",
                    callable=lambda item=p: self._edit_entry(item)
                )
            )

            query.add(
                StandardItem(
                    id=p["id"],
                    text=p["path"],
                    subtext=p["user"],
                    iconUrls=self.iconUrls,
                    actions=actions
                )
            )

    def _filter_items(self, query, search_term):
        """Filter Bitwarden items based on search term."""
        passwords = self._get_items()
        search_fields = ["path", "user"]
        words = set(search_term.strip().lower().split())
        return [p for p in passwords if all(any(word in p[field].lower() for field in search_fields) for word in words)]

    @staticmethod
    def _get_items():
        """Retrieve list of Bitwarden items using rbw list."""
        field_names = ["id", "name", "user", "folder"]
        raw_items = run(
            ["rbw", "list", "--fields", ",".join(field_names)],
            capture_output=True,
            encoding="utf-8",
            check=True,
        )
        items = []
        for line in raw_items.stdout.splitlines():
            fields = line.split("\t")
            item = dict(zip(field_names, fields))
            item["path"] = item["folder"] + "/" + item["name"] if item["folder"] else item["name"]
            items.append(item)
        return items

    @staticmethod
    def _password_to_clipboard(item):
        """Copy password directly using rbw get (fallback method)."""
        password = run(
            ["rbw", "get", item["id"]],
            capture_output=True,
            encoding="utf-8",
            check=True
        ).stdout.strip()
        setClipboardText(text=password)

    @staticmethod
    def _code_to_clipboard(item):
        """Copy TOTP auth code if available."""
        try:
            code = run(
                ["rbw", "code", item["id"]],
                capture_output=True,
                encoding="utf-8",
                check=True
            ).stdout.strip()
        except CalledProcessError as err:
            code = str(err)
        setClipboardText(text=code)

    @staticmethod
    def _edit_entry(item):
        """Open a terminal to edit the entry using rbw edit."""
        runTerminal(f"konsole --hold -e rbw edit {item['id']}")

    @staticmethod
    def _get_item_fields(item_id):
        """Fetch all fields for an item from rbw, marking hidden fields."""
        try:
            raw_output = run(
                ["rbw", "get", "--raw", item_id],
                capture_output=True,
                encoding="utf-8",
                check=True
            ).stdout.strip()
            item_data = json.loads(raw_output)
            info(f"Raw item data for {item_id}: {json.dumps(item_data, indent=2)}")
            fields = {}

            # Extract from "data" object
            data = item_data.get("data", {})
            if data.get("username"):
                fields["username"] = {"value": data["username"], "hidden": False}
            if data.get("password"):
                fields["password"] = {"value": data["password"], "hidden": True}
            if data.get("totp"):
                fields["totp"] = {"value": data["totp"], "hidden": True}
            if data.get("uris"):
                for i, uri in enumerate(data["uris"]):
                    if uri.get("uri"):
                        fields[f"uri_{i+1}"] = {"value": uri["uri"], "hidden": False}

            # Notes at root level
            if item_data.get("notes"):
                fields["notes"] = {"value": item_data["notes"], "hidden": False}

            # Custom fields with type checking
            if item_data.get("fields"):
                for field in item_data["fields"]:
                    if field.get("name") and field.get("value"):
                        fields[field["name"]] = {
                            "value": field["value"],
                            "hidden": field.get("type") == "hidden"
                        }

            info(f"Extracted fields for {item_id}: {fields}")
            return fields
        except Exception as e:
            info(f"Error getting item fields: {str(e)}")
            return {"error": str(e)}
