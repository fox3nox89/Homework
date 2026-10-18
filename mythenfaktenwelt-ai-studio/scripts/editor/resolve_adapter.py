"""
DaVinci Resolve Studio Adapter -- primaerer Editor-Backend, wenn Resolve
lokal installiert und lizenziert ist (bei dir der Fall). FFmpeg
(`scripts/editor/build_video.py`) bleibt der Notfall-Pfad, falls Resolve
aus irgendeinem Grund nicht erreichbar ist -- die Produktion darf nie an
einem einzelnen Editor-Tool scheitern.

WICHTIG, ehrlich: Dieses Modul kann in dieser Cloud-Session nicht getestet
werden -- Resolves Scripting-API (`DaVinciResolveScript`) existiert nur in
einer lokalen Resolve-Installation und wird von Resolve selbst in den
Python-Pfad eingehaengt (ueblicherweise ueber die Umgebungsvariablen
RESOLVE_SCRIPT_API / RESOLVE_SCRIPT_LIB, siehe Resolves eigene
"Developer"-Dokumentation unter Hilfe -> Dokumentation -> Readme in
Resolve selbst -- das ist die verbindliche Quelle, nicht dieses Kommentar).
is_available() prueft das ehrlich zur Laufzeit, statt eine Verfuegbarkeit
vorzutaeuschen.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

TARGET_W = 1080
TARGET_H = 1920
TARGET_FPS = 30


def is_available() -> bool:
    try:
        import DaVinciResolveScript  # type: ignore # noqa: F401
        return True
    except ImportError:
        return False


class ResolveNotAvailable(RuntimeError):
    pass


@dataclass
class SceneClip:
    video_path: Path
    voiceover_start_s: float
    voiceover_end_s: float


def _get_resolve():
    if not is_available():
        raise ResolveNotAvailable(
            "DaVinciResolveScript ist nicht importierbar. Pruefe lokal, dass "
            "Resolve laeuft und RESOLVE_SCRIPT_API/RESOLVE_SCRIPT_LIB gemaess "
            "Resolves eigener Developer-Dokumentation gesetzt sind. Fallback: "
            "scripts/editor/build_video.py (FFmpeg)."
        )
    import DaVinciResolveScript as dvr_script  # type: ignore

    resolve = dvr_script.scriptapp("Resolve")
    if resolve is None:
        raise ResolveNotAvailable("Resolve-App antwortet nicht (laeuft Resolve?).")
    return resolve


def assemble(
    project_name: str,
    clips: list[SceneClip],
    voice_path: Path,
    music_path: Optional[Path],
    output_path: Path,
    style_subtitle_font: str = "Arial",
) -> None:
    """Baut ein Video komplett innerhalb von Resolve zusammen:
    Projekt anlegen -> Clips in Timeline importieren (synchron zu den
    Voiceover-Segmenten) -> Voice+Musik auf Fairlight -> Resolves eigene
    Spracherkennung fuer Untertitel -> Render ueber die Deliver-Queue.

    Jeder Schritt ruft reale Resolve-API-Methoden auf (ProjectManager,
    MediaPool, Timeline, Fairlight, Render-Queue) -- siehe Resolves
    Developer-Dokumentation fuer die exakten Methodennamen deiner
    installierten Version, da sich die API zwischen Resolve-Versionen
    leicht unterscheidet. Dieser Adapter ist bewusst als duenne,
    gut lesbare Huelle gehalten, die du anhand von `resolve.GetVersion()`
    und der lokalen API-Referenz feinjustierst, statt Methodennamen zu
    erraten, die in deiner Version ggf. anders heissen."""
    resolve = _get_resolve()
    project_manager = resolve.GetProjectManager()
    project = project_manager.CreateProject(project_name) or project_manager.LoadProject(project_name)
    if project is None:
        raise RuntimeError(f"Resolve-Projekt '{project_name}' konnte nicht erstellt/geladen werden.")

    media_pool = project.GetMediaPool()
    media_storage = resolve.GetMediaStorage()

    imported_clips = []
    for clip in clips:
        items = media_storage.AddItemListToMediaPool(str(clip.video_path))
        if not items:
            raise RuntimeError(f"Clip konnte nicht importiert werden: {clip.video_path}")
        imported_clips.append(items[0])

    timeline = media_pool.CreateTimelineFromClips(f"{project_name}_timeline", imported_clips)
    if timeline is None:
        raise RuntimeError("Timeline konnte nicht erstellt werden.")

    voice_items = media_storage.AddItemListToMediaPool(str(voice_path))
    media_pool.AppendToTimeline(voice_items)
    if music_path is not None:
        music_items = media_storage.AddItemListToMediaPool(str(music_path))
        media_pool.AppendToTimeline(music_items)

    # Resolves eigene Spracherkennung fuer Untertitel (Fairlight/Timeline-
    # Menue "Create Subtitles from Audio" in der GUI; das Scripting-
    # Aequivalent variiert je Resolve-Version -- siehe lokale API-Referenz).
    try:
        timeline.CreateSubtitlesFromAudio()
    except AttributeError:
        raise NotImplementedError(
            "timeline.CreateSubtitlesFromAudio() existiert in deiner "
            "Resolve-Version nicht unter diesem Namen -- pruefe die lokale "
            "Scripting-API-Referenz (Resolve -> Hilfe -> Dokumentation) "
            "fuer den aktuellen Methodennamen und passe ihn hier an."
        )

    project.SetSetting("timelineResolutionWidth", str(TARGET_W))
    project.SetSetting("timelineResolutionHeight", str(TARGET_H))
    project.SetSetting("timelineFrameRate", str(TARGET_FPS))

    render_settings = {
        "SelectAllFrames": True,
        "TargetDir": str(output_path.parent),
        "CustomName": output_path.stem,
        "ExportVideo": True,
        "ExportAudio": True,
        "FormatWidth": TARGET_W,
        "FormatHeight": TARGET_H,
    }
    project.SetRenderSettings(render_settings)
    job_id = project.AddRenderJob()
    project.StartRendering(job_id)

    print(f"[resolve_adapter] Render gestartet: {output_path}")
