"""Safe fixes: remove leftover entities, or helpers nothing uses, with a backup and an Undo for 30 days.

The rules (from the plan Radu approved):
1. Nothing changes without a tap from an admin.
2. List first, exactly: a fix acts only on the list the person saw and ticked, never on a new search.
3. Kept items are never in a fix.
4. Backup first: if the backup cannot be written, nothing is removed.
5. Undo for 30 days. Undo brings back only what that fix removed.
6. Check after: if the count of removed items is not the count asked for, it says so and offers Undo.

Leftover entities are removed here with Home Assistant's own entity registry. Helpers made in the UI are removed
by the sidebar page with Home Assistant's own helper commands (the same ones its Helpers page uses); this file
keeps the backup and the record for them.
"""

from __future__ import annotations

import asyncio
import json
import secrets
import shutil
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path
from typing import Any

from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .checks import without_entity
from .const import DOMAIN

FIX_KINDS = ("leftover_entities", "unused_helpers")
AUTOMATION_FIXES = ("use_new", "remove_step", "turn_off")
UNDO_FOR = timedelta(days=30)
PLAN_FOR = timedelta(minutes=15)
BACKUP_FOLDER = "home_checkup_backups"
RELOAD_WAIT = 0.5  # seconds between looks after an automation was saved
RELOAD_CHECKS = 20
_ENTITY_FIELDS = (
    "entity_id",
    "domain",
    "platform",
    "unique_id",
    "config_entry_id",
    "device_id",
    "original_name",
    "original_icon",
    "original_device_class",
    "unit_of_measurement",
    "entity_category",
    "has_entity_name",
    "supported_features",
    "capabilities",
    "translation_key",
    "name",
    "icon",
    "area_id",
)


class FixError(Exception):
    """A fix could not start. Nothing was changed."""


@dataclass
class Plan:
    id: str
    kind: str
    keys: dict[str, dict[str, str]]  # key -> {name, id}
    made: float


@dataclass
class Fixes:
    hass: HomeAssistant
    records: list[dict[str, Any]] = field(default_factory=list)
    plans: dict[str, Plan] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._store: Store[dict[str, Any]] = Store(self.hass, 1, f"{DOMAIN}.fixes")

    async def async_load(self) -> None:
        data = await self._store.async_load() or {}
        self.records = data.get("records", [])
        self._forget_old()

    async def _save(self) -> None:
        self._forget_old()
        await self._store.async_save({"records": self.records})

    def _forget_old(self) -> None:
        cutoff = (dt_util.utcnow() - UNDO_FOR).isoformat()
        self.records = [r for r in self.records if r.get("at", "") >= cutoff]

    # ---- 1. the exact list -----------------------------------------------------------------------------------

    @callback
    def plan(self, kind: str, findings: list) -> dict[str, Any]:
        """The exact list a fix may act on, from the findings shown now. Kept items are already left out."""
        if kind not in FIX_KINDS:
            raise FixError("This kind has no safe fix.")
        items = [item for f in findings if f.kind == kind for item in f.items]
        ent_reg = er.async_get(self.hass)
        keys: dict[str, dict[str, str]] = {}
        out = []
        for item in items:
            entry = ent_reg.async_get(item.id)
            row = {"key": item.key, "name": item.name, "id": item.id}
            if kind == "unused_helpers":
                # Only helpers made in the UI can be removed here. Their registry entry names the helper's own id.
                if entry is None or entry.platform != entry.domain or entry.config_entry_id:
                    continue
                row |= {"domain": entry.domain, "item_id": entry.unique_id}
            keys[item.key] = {"name": item.name, "id": item.id}
            out.append(row)
        now = dt_util.utcnow().timestamp()
        self.plans = {k: p for k, p in self.plans.items() if now - p.made < PLAN_FOR.total_seconds()}
        plan = Plan(secrets.token_hex(8), kind, keys, now)
        self.plans[plan.id] = plan
        return {"plan_id": plan.id, "kind": kind, "items": out}

    def _take_plan(self, plan_id: str, keys: list[str], kind: str) -> Plan:
        plan = self.plans.pop(plan_id, None)
        if plan is None or plan.kind != kind:
            raise FixError("This list is too old. Open it again to see the latest list.")
        extra = [k for k in keys if k not in plan.keys]
        if extra or not keys:
            raise FixError("A fix can only act on the list you saw.")
        return plan

    # ---- 2. backup -----------------------------------------------------------------------------------------

    async def _backup(self, fix_id: str, record: dict[str, Any], copy_registry: bool) -> str:
        """Write the backup folder. Any failure stops the fix before anything changes."""
        folder = Path(self.hass.config.path(BACKUP_FOLDER, f"{dt_util.now().strftime('%Y-%m-%d-%H%M%S')}-{fix_id}"))
        registry = Path(self.hass.config.path(".storage", "core.entity_registry"))

        def write() -> None:
            folder.mkdir(parents=True, exist_ok=False)
            (folder / "fix.json").write_text(json.dumps(record, indent=2, default=str))
            if copy_registry and registry.is_file():
                shutil.copy2(registry, folder / "core.entity_registry")

        try:
            await self.hass.async_add_executor_job(write)
        except OSError as err:
            raise FixError(f"The backup could not be written, so nothing was changed ({err.strerror}).") from err
        return str(folder)

    # ---- 3. leftover entities --------------------------------------------------------------------------------

    async def async_remove_entities(self, plan_id: str, keys: list[str]) -> dict[str, Any]:
        plan = self._take_plan(plan_id, keys, "leftover_entities")
        ent_reg = er.async_get(self.hass)
        targets = [plan.keys[k]["id"] for k in keys]
        snapshots = []
        for entity_id in targets:
            entry = ent_reg.async_get(entity_id)
            if entry is not None:
                snapshots.append({name: _plain(getattr(entry, name, None)) for name in _ENTITY_FIELDS})
        fix_id = secrets.token_hex(6)
        record = {
            "id": fix_id,
            "kind": "leftover_entities",
            "at": dt_util.utcnow().isoformat(),
            "asked": len(targets),
            "items": [{"name": plan.keys[k]["name"], "id": plan.keys[k]["id"]} for k in keys],
            "entities": snapshots,
        }
        record["backup"] = await self._backup(fix_id, record, copy_registry=True)
        for snap in snapshots:
            ent_reg.async_remove(snap["entity_id"])
        still = [e for e in targets if ent_reg.async_get(e) is not None]
        record["removed"] = len(targets) - len(still)
        record["status"] = "done" if not still and record["removed"] == len(snapshots) == len(targets) else "check"
        self.records.insert(0, record)
        await self._save()
        return _public(record)

    async def async_undo(self, fix_id: str) -> dict[str, Any]:
        record = self._record(fix_id)
        if record.get("undone_at"):
            raise FixError("This fix was already undone.")
        if record["kind"] == "offline_device":
            return await self._undo_disable(record)
        if record["kind"] == "device_area":
            return await self._undo_area(record)
        if record["kind"] != "leftover_entities":
            raise FixError("This is brought back by the Home Checkup page.")
        ent_reg = er.async_get(self.hass)
        dev_reg = dr.async_get(self.hass)
        back = 0
        for snap in record.get("entities", []):
            config_entry = (
                self.hass.config_entries.async_get_entry(snap["config_entry_id"]) if snap.get("config_entry_id") else None
            )
            device_id = snap.get("device_id")
            if device_id and dev_reg.async_get(device_id) is None:
                device_id = None
            entry = ent_reg.async_get_or_create(
                snap["domain"],
                snap["platform"],
                snap["unique_id"],
                suggested_object_id=snap["entity_id"].split(".", 1)[1],
                config_entry=config_entry,
                device_id=device_id,
                capabilities=snap.get("capabilities"),
                entity_category=EntityCategory(snap["entity_category"]) if snap.get("entity_category") else None,
                has_entity_name=bool(snap.get("has_entity_name")),
                original_device_class=snap.get("original_device_class"),
                original_icon=snap.get("original_icon"),
                original_name=snap.get("original_name"),
                supported_features=snap.get("supported_features") or 0,
                translation_key=snap.get("translation_key"),
                unit_of_measurement=snap.get("unit_of_measurement"),
            )
            back += entry.entity_id == snap["entity_id"]
        record["undone_at"] = dt_util.utcnow().isoformat()
        record["restored"] = back
        await self._save()
        return _public(record)

    # ---- 3b. a device that is offline for good: switch it off, never delete it -------------------------------

    async def async_disable_device(self, key: str, findings: list) -> dict[str, Any]:
        """Disable one offline device from the list shown now. Home Assistant keeps it, with all its settings."""
        item = next((i for f in findings if f.kind == "unavailable" for i in f.items if i.key == key), None)
        if item is None or item.fix != "disable":
            raise FixError("This list is too old. Open it again to see the latest list.")
        dev_reg = dr.async_get(self.hass)
        device = dev_reg.async_get(item.id)
        if device is None or device.disabled_by is not None:
            raise FixError("This device is no longer there, so nothing was changed.")
        fix_id = secrets.token_hex(6)
        record = {
            "id": fix_id,
            "kind": "offline_device",
            "at": dt_util.utcnow().isoformat(),
            "asked": 1,
            "items": [{"name": item.name, "id": item.id}],
        }
        record["backup"] = await self._backup(fix_id, record, copy_registry=True)
        dev_reg.async_update_device(item.id, disabled_by=dr.DeviceEntryDisabler.USER)
        done = (after := dev_reg.async_get(item.id)) is not None and after.disabled_by is not None
        record["removed"] = int(done)
        record["status"] = "done" if done else "check"
        self.records.insert(0, record)
        await self._save()
        return _public(record)

    async def _undo_disable(self, record: dict[str, Any]) -> dict[str, Any]:
        dev_reg = dr.async_get(self.hass)
        device_id = record["items"][0]["id"]
        device = dev_reg.async_get(device_id)
        back = 0
        # Only switch on again what this fix switched off. If the person changed it since, leave their choice.
        if device is not None and device.disabled_by is dr.DeviceEntryDisabler.USER:
            dev_reg.async_update_device(device_id, disabled_by=None)
            back = 1
        record["undone_at"] = dt_util.utcnow().isoformat()
        record["restored"] = back
        await self._save()
        return _public(record)

    # ---- 3c. a device without an area: put it in the area its name says ------------------------------------------

    async def async_set_area(self, key: str, findings: list) -> dict[str, Any]:
        item = next((i for f in findings if f.kind == "areas" for i in f.items if i.key == key), None)
        if item is None or item.fix != "set_area" or not item.to:
            raise FixError("This list is too old. Open it again to see the latest list.")
        dev_reg = dr.async_get(self.hass)
        device = dev_reg.async_get(item.id)
        if device is None or device.area_id:
            raise FixError("This device already has an area, so nothing was changed.")
        fix_id = secrets.token_hex(6)
        record = {
            "id": fix_id,
            "kind": "device_area",
            "at": dt_util.utcnow().isoformat(),
            "asked": 1,
            "items": [{"name": item.name, "id": item.id, "area": item.to_name, "area_id": item.to}],
        }
        record["backup"] = await self._backup(fix_id, record, copy_registry=False)
        dev_reg.async_update_device(item.id, area_id=item.to)
        done = (after := dev_reg.async_get(item.id)) is not None and after.area_id == item.to
        record["removed"] = int(done)
        record["status"] = "done" if done else "check"
        self.records.insert(0, record)
        await self._save()
        return _public(record)

    async def _undo_area(self, record: dict[str, Any]) -> dict[str, Any]:
        dev_reg = dr.async_get(self.hass)
        target = record["items"][0]
        device = dev_reg.async_get(target["id"])
        back = 0
        # Only take it out of the area this fix put it in. If the person moved it since, leave their choice.
        if device is not None and device.area_id == target.get("area_id"):
            dev_reg.async_update_device(target["id"], area_id=None)
            back = 1
        record["undone_at"] = dt_util.utcnow().isoformat()
        record["restored"] = back
        await self._save()
        return _public(record)

    # ---- 4. helpers (removed by the page with Home Assistant's own helper commands) ------------------------

    async def async_record_helpers(self, plan_id: str, keys: list[str], saved: list[dict[str, Any]]) -> dict[str, Any]:
        """Before the page removes helpers: check the list, write the backup, keep the record. Returns the fix id."""
        plan = self._take_plan(plan_id, keys, "unused_helpers")
        by_entity = {s.get("entity_id"): s for s in saved}
        helpers = []
        for key in keys:
            entity_id = plan.keys[key]["id"]
            entry = er.async_get(self.hass).async_get(entity_id)
            snap = by_entity.get(entity_id)
            if entry is None or snap is None or snap.get("domain") != entry.domain:
                raise FixError("The list changed. Open it again to see the latest list.")
            item = snap.get("item") or {}
            if item.get("id") != entry.unique_id:
                raise FixError("The list changed. Open it again to see the latest list.")
            helpers.append({"entity_id": entity_id, "domain": entry.domain, "item": item, "name": plan.keys[key]["name"]})
        fix_id = secrets.token_hex(6)
        record = {
            "id": fix_id,
            "kind": "unused_helpers",
            "at": dt_util.utcnow().isoformat(),
            "asked": len(helpers),
            "items": [{"name": h["name"], "id": h["entity_id"]} for h in helpers],
            "helpers": helpers,
            "status": "started",
        }
        record["backup"] = await self._backup(fix_id, record, copy_registry=False)
        self.records.insert(0, record)
        await self._save()
        return _public(record)

    async def async_finish_helpers(self, fix_id: str, undo: bool = False) -> dict[str, Any]:
        """After the page removed (or brought back) helpers: count what is really gone (or back)."""
        record = self._record(fix_id)
        ent_reg = er.async_get(self.hass)
        ids = [h["entity_id"] for h in record.get("helpers", [])]
        if undo:
            back = sum(1 for e in ids if ent_reg.async_get(e) is not None)
            record["undone_at"] = dt_util.utcnow().isoformat()
            record["restored"] = back
        else:
            gone = sum(1 for e in ids if ent_reg.async_get(e) is None and self.hass.states.get(e) is None)
            record["removed"] = gone
            record["status"] = "done" if gone == record["asked"] else "check"
        await self._save()
        return _public(record)

    # ---- 5. broken automation steps (changed by the page with Home Assistant's own automation editor) ------

    async def async_record_automation(
        self, findings: list, key: str, before: dict[str, Any] | None, new: str | None = None
    ) -> dict[str, Any]:
        """Before the page changes an automation: check the step is still in the list, back up, keep the record.

        choose (`new` is given): the person chose another entity for the missing one, in an automation or a script.

        use_new: the page swaps the missing entity for its new name; `before` is the automation as it is now.
        remove_step: Home Checkup works out the automation without the broken step; the page saves it.
        turn_off: the page switches the automation off.
        """
        item = next((i for f in findings if f.kind == "broken_references" for i in f.items if i.key == key), None)
        if item is None or (item.fix not in AUTOMATION_FIXES if new is None else not item.choose):
            raise FixError("The list changed. Open it again to see the latest list.")
        kind = item.fix if new is None else "choose"
        if new is not None:
            # Only a real entity of the same kind (a light for a light), so the step keeps its meaning.
            if new == item.old or new.split(".")[0] != item.old.split(".")[0] or self.hass.states.get(new) is None:
                raise FixError("Choose an entity of the same kind that exists.")
        after = None
        if kind in ("use_new", "remove_step", "choose"):
            if not isinstance(before, dict) or item.old not in json.dumps(before):
                raise FixError("This automation changed. Open it again to see the latest list.")
        if kind == "remove_step":
            after = without_entity(before, item.old)
            if after is None:
                raise FixError("This step cannot be removed cleanly. Open the automation to change it.")
        fix_id = secrets.token_hex(6)
        record = {
            "id": fix_id,
            "kind": kind,
            "at": dt_util.utcnow().isoformat(),
            "asked": 1,
            "items": [{"name": item.name, "id": item.id}],
            "automation": item.id,
            "old": item.old,
            "new": new if new is not None else item.to,
            "before": before if kind != "turn_off" else None,
            "status": "started",
        }
        record["backup"] = await self._backup(fix_id, record, copy_registry=False)
        self.records.insert(0, record)
        await self._save()
        return _public(record) | {"old": item.old, "new": record["new"], "automation": item.id, "after": after}

    async def async_finish_automation(self, fix_id: str, undo: bool = False) -> dict[str, Any]:
        """After the page changed (or put back) the automation: check that it really did."""
        record = self._record(fix_id)
        # Home Assistant reloads the automation a moment after it is saved. Look again for a few seconds
        # before saying it did not change.
        done = self._automation_changed(record, undo)
        for _ in range(RELOAD_CHECKS):
            if done:
                break
            await asyncio.sleep(RELOAD_WAIT)
            done = self._automation_changed(record, undo)
        if undo:
            record["undone_at"] = dt_util.utcnow().isoformat()
            record["restored"] = 1 if done else 0
        else:
            record["removed"] = 1 if done else 0
            record["status"] = "done" if done else "check"
        await self._save()
        return _public(record)

    @callback
    def _automation_changed(self, record: dict[str, Any], undo: bool) -> bool:
        state = self.hass.states.get(record["automation"])
        if record["kind"] == "turn_off":
            return state is not None and state.state == ("on" if undo else "off")
        if record["automation"].startswith("script."):
            from homeassistant.components.script import entities_in_script

            entities = set(entities_in_script(self.hass, record["automation"]))
        else:
            from homeassistant.components.automation import entities_in_automation

            entities = set(entities_in_automation(self.hass, record["automation"]))
        if undo:
            return record["old"] in entities
        if record["kind"] == "remove_step":
            return state is not None and record["old"] not in entities
        return record["old"] not in entities and record["new"] in entities

    def automation_backup(self, fix_id: str) -> dict[str, Any]:
        record = self._record(fix_id)
        return {"kind": record["kind"], "automation": record.get("automation"), "before": record.get("before")}

    # ---- what the page reads -------------------------------------------------------------------------------

    def _record(self, fix_id: str) -> dict[str, Any]:
        for record in self.records:
            if record["id"] == fix_id:
                return record
        raise FixError("This fix is older than 30 days, so it can no longer be undone.")

    def helper_backup(self, fix_id: str) -> list[dict[str, Any]]:
        return self._record(fix_id).get("helpers", [])

    def recent(self) -> list[dict[str, Any]]:
        self._forget_old()
        return [_public(r) for r in self.records[:10]]


def _plain(value: Any) -> Any:
    """Registry values as plain JSON (enums become their text)."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_plain(v) for v in value]
    return str(value)


def _public(record: dict[str, Any]) -> dict[str, Any]:
    """What the page shows: no registry details, no backup contents."""
    until = dt_util.parse_datetime(record["at"]) + UNDO_FOR
    return {
        "id": record["id"],
        "kind": record["kind"],
        "at": record["at"],
        "asked": record.get("asked", 0),
        "removed": record.get("removed", 0),
        "status": record.get("status", "done"),
        "undone_at": record.get("undone_at"),
        "restored": record.get("restored"),
        "undo_until": until.isoformat(),
        "items": record.get("items", []),
    }
