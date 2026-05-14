"""
EcoCity Mayor — sounds.py
Programmatic sound effects using pygame — no audio files needed.
"""

import pygame
import numpy as np
import threading

# ── Sample rate ───────────────────────────────────────
SAMPLE_RATE = 44100


def _generate_tone(frequency, duration, volume=0.3,
                   wave="sine", fade=True):
    """Generate a numpy sound array for a given frequency."""
    frames  = int(SAMPLE_RATE * duration)
    t       = np.linspace(0, duration, frames, False)

    if wave == "sine":
        wave_arr = np.sin(2 * np.pi * frequency * t)
    elif wave == "square":
        wave_arr = np.sign(np.sin(2 * np.pi * frequency * t))
    elif wave == "sawtooth":
        wave_arr = 2 * (t * frequency - np.floor(t * frequency + 0.5))
    elif wave == "triangle":
        wave_arr = 2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1
    else:
        wave_arr = np.sin(2 * np.pi * frequency * t)

    # Fade in/out to avoid clicks
    if fade:
        fade_len = min(int(SAMPLE_RATE * 0.01), frames // 4)
        if fade_len > 0:
            wave_arr[:fade_len]  *= np.linspace(0, 1, fade_len)
            wave_arr[-fade_len:] *= np.linspace(1, 0, fade_len)

    wave_arr = (wave_arr * volume * 32767).astype(np.int16)
    # Stereo
    stereo = np.column_stack([wave_arr, wave_arr])
    return pygame.sndarray.make_sound(stereo)


def _generate_chord(frequencies, duration, volume=0.25, wave="sine"):
    """Mix multiple frequencies into one sound."""
    frames   = int(SAMPLE_RATE * duration)
    t        = np.linspace(0, duration, frames, False)
    combined = np.zeros(frames)
    for freq in frequencies:
        combined += np.sin(2 * np.pi * freq * t)
    combined /= len(frequencies)

    fade_len = min(int(SAMPLE_RATE * 0.015), frames // 4)
    if fade_len > 0:
        combined[:fade_len]  *= np.linspace(0, 1, fade_len)
        combined[-fade_len:] *= np.linspace(1, 0, fade_len)

    combined = (combined * volume * 32767).astype(np.int16)
    stereo   = np.column_stack([combined, combined])
    return pygame.sndarray.make_sound(stereo)


def _generate_noise(duration, volume=0.15, low_pass=True):
    """Generate white/filtered noise for disaster/alert sounds."""
    frames    = int(SAMPLE_RATE * duration)
    noise     = np.random.uniform(-1, 1, frames)

    if low_pass:
        # Simple moving average to soften the noise
        kernel = np.ones(8) / 8
        noise  = np.convolve(noise, kernel, mode="same")

    fade_len = min(int(SAMPLE_RATE * 0.02), frames // 4)
    if fade_len > 0:
        noise[:fade_len]  *= np.linspace(0, 1, fade_len)
        noise[-fade_len:] *= np.linspace(1, 0, fade_len)

    noise  = (noise * volume * 32767).astype(np.int16)
    stereo = np.column_stack([noise, noise])
    return pygame.sndarray.make_sound(stereo)


class SoundManager:
    """
    Central sound manager. Call SoundManager.init() once at startup.
    Then use SoundManager.play("event_name") anywhere in the game.
    """

    _sounds  = {}
    _music   = None
    _enabled = True
    _music_playing = False
    _music_thread  = None
    _stop_music    = False

    @classmethod
    def init(cls):
        """Build all sounds. Call once after pygame.init()."""
        if not pygame.mixer.get_init():
            pygame.mixer.init(
                frequency=SAMPLE_RATE,
                size=-16,
                channels=2,
                buffer=512,
            )

        cls._sounds = {

            # ── UI ────────────────────────────────────
            "click": _generate_tone(
                800, 0.06, volume=0.25, wave="sine"),

            "hover": _generate_tone(
                600, 0.04, volume=0.08, wave="sine"),

            "back": _generate_tone(
                400, 0.08, volume=0.2, wave="sine"),

            # ── Login / logout ────────────────────────
            "login": _generate_chord(
                [523, 659, 784], 0.35, volume=0.3),  # C E G

            "logout": _generate_chord(
                [784, 659, 523], 0.35, volume=0.25),  # G E C descending

            # ── Quiz ──────────────────────────────────
            "correct": _generate_chord(
                [523, 659, 784, 1047], 0.5, volume=0.35),  # C major arp

            "wrong": _generate_chord(
                [220, 233], 0.4, volume=0.3, wave="square"),  # dissonant

            "streak": _generate_chord(
                [523, 659, 784, 1047, 1319], 0.6, volume=0.4),  # C maj full

            # ── Shop ──────────────────────────────────
            "purchase": _generate_chord(
                [440, 554, 659, 880], 0.45, volume=0.35),  # A maj

            "insufficient": _generate_tone(
                180, 0.25, volume=0.3, wave="square"),

            # ── Achievements ─────────────────────────
            "achievement": cls._build_achievement(),

            # ── Disaster ─────────────────────────────
            "disaster": cls._build_disaster(),

            # ── City / pollution ──────────────────────
            "pollution_high": _generate_tone(
                150, 0.3, volume=0.2, wave="sawtooth"),

            "pollution_low": _generate_chord(
                [392, 494, 587], 0.4, volume=0.25),  # G maj peaceful

            # ── Admin / moderator ─────────────────────
            "save": _generate_chord(
                [440, 554, 659], 0.3, volume=0.28),

            "delete": _generate_tone(
                250, 0.15, volume=0.25, wave="square"),

            "ban": _generate_chord(
                [196, 185], 0.35, volume=0.3, wave="sawtooth"),

            # ── Game events ───────────────────────────
            "game_over": cls._build_game_over(),

            "game_win": cls._build_game_win(),

            "day_start": _generate_chord(
                [392, 523, 659], 0.3, volume=0.22),
        }

    @classmethod
    def _build_achievement(cls):
        """Rising arpeggio for achievements."""
        frames   = int(SAMPLE_RATE * 0.8)
        t        = np.linspace(0, 0.8, frames, False)
        notes    = [523, 659, 784, 1047, 1319]
        combined = np.zeros(frames)
        seg      = frames // len(notes)
        for i, freq in enumerate(notes):
            start = i * seg
            end   = min(start + seg, frames)
            seg_t = t[start:end] - t[start]
            tone  = np.sin(2 * np.pi * freq * seg_t)
            fl    = min(int(SAMPLE_RATE * 0.01), len(tone) // 4)
            if fl > 0:
                tone[:fl]  *= np.linspace(0, 1, fl)
                tone[-fl:] *= np.linspace(1, 0, fl)
            combined[start:end] += tone
        combined *= 0.3
        fade_len = min(int(SAMPLE_RATE * 0.05), frames // 4)
        combined[-fade_len:] *= np.linspace(1, 0, fade_len)
        combined = (combined * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(
            np.column_stack([combined, combined]))

    @classmethod
    def _build_disaster(cls):
        """Urgent alarm sound for disaster events."""
        frames   = int(SAMPLE_RATE * 0.6)
        t        = np.linspace(0, 0.6, frames, False)
        # Alternating high-low alarm
        alarm    = np.sin(2 * np.pi * 880 * t) * (t % 0.15 < 0.075)
        alarm   += np.sin(2 * np.pi * 660 * t) * (t % 0.15 >= 0.075)
        noise    = np.random.uniform(-0.1, 0.1, frames)
        combined = alarm * 0.8 + noise * 0.2
        fade_len = min(int(SAMPLE_RATE * 0.02), frames // 4)
        combined[-fade_len:] *= np.linspace(1, 0, fade_len)
        combined = (combined * 0.35 * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(
            np.column_stack([combined, combined]))

    @classmethod
    def _build_game_over(cls):
        """Sad descending tone sequence."""
        frames   = int(SAMPLE_RATE * 1.2)
        t        = np.linspace(0, 1.2, frames, False)
        notes    = [392, 349, 330, 294, 262]  # G F E D C descending
        combined = np.zeros(frames)
        seg      = frames // len(notes)
        for i, freq in enumerate(notes):
            start = i * seg
            end   = min(start + seg + int(SAMPLE_RATE * 0.05), frames)
            seg_t = t[start:end] - t[start]
            tone  = np.sin(2 * np.pi * freq * seg_t) * 0.6
            tone += np.sin(2 * np.pi * freq * 0.5 * seg_t) * 0.3
            fl    = min(int(SAMPLE_RATE * 0.02), len(tone) // 4)
            if fl > 0:
                tone[:fl]  *= np.linspace(0, 1, fl)
                tone[-fl:] *= np.linspace(1, 0, fl)
            combined[start:min(start + len(tone), frames)] += tone[:frames - start]
        combined *= 0.35
        combined[-int(SAMPLE_RATE * 0.1):] *= np.linspace(1, 0, int(SAMPLE_RATE * 0.1))
        combined = (combined * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(
            np.column_stack([combined, combined]))

    @classmethod
    def _build_game_win(cls):
        """Happy ascending fanfare."""
        frames   = int(SAMPLE_RATE * 1.5)
        t        = np.linspace(0, 1.5, frames, False)
        notes    = [523, 659, 784, 659, 784, 1047]  # C E G E G C
        combined = np.zeros(frames)
        seg      = int(frames / len(notes) * 0.9)
        gap      = int(frames / len(notes) * 0.1)
        for i, freq in enumerate(notes):
            start = i * (seg + gap)
            end   = min(start + seg, frames)
            if start >= frames:
                break
            seg_t = t[start:end] - t[start]
            tone  = (np.sin(2 * np.pi * freq * seg_t) * 0.7 +
                     np.sin(2 * np.pi * freq * 2 * seg_t) * 0.2 +
                     np.sin(2 * np.pi * freq * 3 * seg_t) * 0.1)
            fl    = min(int(SAMPLE_RATE * 0.015), len(tone) // 4)
            if fl > 0:
                tone[:fl]  *= np.linspace(0, 1, fl)
                tone[-fl:] *= np.linspace(1, 0, fl)
            combined[start:end] += tone
        combined *= 0.35
        combined[-int(SAMPLE_RATE * 0.15):] *= np.linspace(
            1, 0, int(SAMPLE_RATE * 0.15))
        combined = (combined * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(
            np.column_stack([combined, combined]))

    # ── Ambient music ─────────────────────────────────

    @classmethod
    def _build_music_segment(cls, pollution_level):
        """
        Generate a short ambient music loop.
        Clean city = bright, peaceful chords.
        Polluted city = low, dark, tense tones.
        """
        duration = 4.0
        frames   = int(SAMPLE_RATE * duration)
        t        = np.linspace(0, duration, frames, False)
        combined = np.zeros(frames)

        if pollution_level < 40:
            # Clean — bright arpeggiated chords
            notes = [261, 329, 392, 523, 659, 784,
                     659, 523, 392, 329]
            vol   = 0.12
        elif pollution_level < 70:
            # Moderate — neutral ambient pads
            notes = [220, 277, 330, 440, 554, 440,
                     330, 277]
            vol   = 0.10
        else:
            # Polluted — dark, tense drones
            notes = [110, 138, 165, 138, 110, 92,
                     110, 92]
            vol   = 0.09

        seg_frames = frames // len(notes)
        for i, freq in enumerate(notes):
            start = i * seg_frames
            end   = min(start + seg_frames + int(SAMPLE_RATE * 0.1),
                        frames)
            seg_t = t[start:end] - t[start]
            tone  = (np.sin(2 * np.pi * freq * seg_t) * 0.6 +
                     np.sin(2 * np.pi * freq * 2 * seg_t) * 0.25 +
                     np.sin(2 * np.pi * freq * 0.5 * seg_t) * 0.15)
            fl    = min(int(SAMPLE_RATE * 0.05), len(tone) // 3)
            if fl > 0:
                tone[:fl]  *= np.linspace(0, 1, fl)
                tone[-fl:] *= np.linspace(1, 0, fl)
            combined[start:start + len(tone[:frames - start])] += (
                tone[:frames - start])

        # Master fade edges
        fade = int(SAMPLE_RATE * 0.1)
        combined[:fade]  *= np.linspace(0, 1, fade)
        combined[-fade:] *= np.linspace(1, 0, fade)

        combined = (combined * vol * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(
            np.column_stack([combined, combined]))

    @classmethod
    def _music_loop(cls, get_pollution_fn):
        """Background thread that continuously loops ambient music."""
        while not cls._stop_music:
            try:
                pollution = get_pollution_fn()
                segment   = cls._build_music_segment(pollution)
                segment.play()
                # Wait for segment to finish before generating next
                pygame.time.wait(3800)
            except Exception:
                break
        cls._music_playing = False

    @classmethod
    def start_music(cls, get_pollution_fn=None):
        """
        Start looping ambient city music.
        Pass a callable that returns current pollution level
        so the music adapts to city state.
        """
        if cls._music_playing or not cls._enabled:
            return
        cls._stop_music    = False
        cls._music_playing = True
        fn = get_pollution_fn or (lambda: 50)
        cls._music_thread  = threading.Thread(
            target=cls._music_loop,
            args=(fn,),
            daemon=True,
        )
        cls._music_thread.start()

    @classmethod
    def stop_music(cls):
        """Stop the ambient music loop."""
        cls._stop_music    = True
        cls._music_playing = False
        pygame.mixer.stop()

    # ── Play a sound effect ───────────────────────────

    @classmethod
    def play(cls, name):
        """Play a named sound effect."""
        if not cls._enabled:
            return
        sound = cls._sounds.get(name)
        if sound:
            sound.play()

    @classmethod
    def toggle(cls):
        """Mute / unmute all sounds."""
        cls._enabled = not cls._enabled
        if not cls._enabled:
            pygame.mixer.stop()
        return cls._enabled

    @classmethod
    def set_volume(cls, volume):
        """Set master volume 0.0 to 1.0."""
        for sound in cls._sounds.values():
            sound.set_volume(max(0.0, min(1.0, volume)))