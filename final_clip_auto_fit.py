import math


class H3FinalClipAutoFit:
    FPS = 24
    CONTEXT_TRIM = 22

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "duration_1": ("FLOAT", {"default": 6.0, "min": 0.01, "max": 60.0, "step": 0.001}),
                "duration_2": ("FLOAT", {"default": 6.0, "min": 0.01, "max": 60.0, "step": 0.001}),
                "duration_3": ("FLOAT", {"default": 6.0, "min": 0.01, "max": 60.0, "step": 0.001}),
                "duration_4": ("FLOAT", {"default": 6.0, "min": 0.01, "max": 60.0, "step": 0.001}),
                "duration_5": ("FLOAT", {"default": 6.0, "min": 0.01, "max": 60.0, "step": 0.001}),
                "duration_6": ("FLOAT", {"default": 6.0, "min": 0.01, "max": 60.0, "step": 0.001}),
                "duration_7": ("FLOAT", {"default": 6.0, "min": 0.01, "max": 60.0, "step": 0.001}),
                "use_clip_total": ("FLOAT", {"default": 4.0, "min": 1.0, "max": 7.0, "step": 1.0}),
                "actual_song_duration": ("FLOAT", {"default": 49.56, "min": 0.01, "max": 100000.0, "step": 0.001}),
                "part_start_time": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 100000.0, "step": 0.001}),
                "enable_final_fit": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = (
        "FLOAT","FLOAT","FLOAT","FLOAT","FLOAT","FLOAT","FLOAT",
        "FLOAT","INT","INT","INT","INT","FLOAT","STRING"
    )
    RETURN_NAMES = (
        "duration_1","duration_2","duration_3","duration_4",
        "duration_5","duration_6","duration_7",
        "part_start_time",
        "target_frames",
        "predicted_before_frames",
        "predicted_after_frames",
        "added_frames",
        "adjusted_final_duration",
        "report",
    )
    FUNCTION = "fit"
    CATEGORY = "MiniMax H3/MusicVideo"

    @staticmethod
    def _clip1_output_from_nominal(nominal_frames):
        base = max(5, int(nominal_frames))
        return base + (5 - (base % 17)) % 17

    @classmethod
    def _later_output_from_nominal(cls, nominal_frames):
        # Mirrors the workflow:
        # max(5, 5 + 17 * round((round(duration*24) + 22 - 5) / 17))
        generated = max(
            5,
            5 + 17 * round((int(nominal_frames) + cls.CONTEXT_TRIM - 5) / 17)
        )
        return max(0, generated - cls.CONTEXT_TRIM)

    @classmethod
    def _predict_outputs(cls, durations, count):
        outs = []
        for i in range(count):
            nominal = int(round(float(durations[i]) * cls.FPS))
            if i == 0:
                outs.append(cls._clip1_output_from_nominal(nominal))
            else:
                outs.append(cls._later_output_from_nominal(nominal))
        return outs

    @classmethod
    def _output_for_nominal(cls, clip_index, nominal):
        if clip_index == 0:
            return cls._clip1_output_from_nominal(nominal)
        return cls._later_output_from_nominal(nominal)

    def fit(
        self,
        duration_1, duration_2, duration_3, duration_4,
        duration_5, duration_6, duration_7,
        use_clip_total, actual_song_duration, part_start_time,
        enable_final_fit
    ):
        durations = [
            float(duration_1), float(duration_2), float(duration_3),
            float(duration_4), float(duration_5), float(duration_6),
            float(duration_7)
        ]
        count = max(1, min(7, int(round(float(use_clip_total)))))
        song = float(actual_song_duration)
        start = float(part_start_time)

        remaining = max(0.0, song - start)
        target_frames = int(math.ceil(remaining * self.FPS))

        before_outputs = self._predict_outputs(durations, count)
        before_total = int(sum(before_outputs))

        adjusted = list(durations)
        final_index = count - 1
        original_final_duration = adjusted[final_index]

        if bool(enable_final_fit) and before_total < target_frames:
            previous_total = int(sum(before_outputs[:-1]))
            required_final_output = max(0, target_frames - previous_total)

            nominal = int(round(original_final_duration * self.FPS))
            # Search upward to the first H3-valid duration whose actual output
            # reaches or exceeds the song end.
            limit = nominal + self.FPS * 120
            while nominal <= limit:
                out_frames = self._output_for_nominal(final_index, nominal)
                if out_frames >= required_final_output:
                    break
                nominal += 1

            adjusted[final_index] = nominal / self.FPS

        after_outputs = self._predict_outputs(adjusted, count)
        after_total = int(sum(after_outputs))
        added_frames = after_total - before_total
        adjusted_final_duration = adjusted[final_index]

        status = "ENABLED" if bool(enable_final_fit) else "DISABLED"
        report = (
            f"H3 Final Clip Auto Fit: {status}\n"
            f"use_clip_total: {count}\n"
            f"actual_song_duration: {song:.3f}s\n"
            f"part_start_time: {start:.3f}s\n"
            f"remaining_song_seconds: {remaining:.3f}s\n"
            f"target_frames: {target_frames}\n"
            f"predicted_before_frames: {before_total}\n"
            f"predicted_after_frames: {after_total}\n"
            f"added_frames: {added_frames}\n"
            f"final_clip: Clip{count}\n"
            f"original_final_duration: {original_final_duration:.3f}s\n"
            f"adjusted_final_duration: {adjusted_final_duration:.3f}s\n"
            f"end_margin_frames: {after_total - target_frames}"
        )

        return (
            adjusted[0], adjusted[1], adjusted[2], adjusted[3],
            adjusted[4], adjusted[5], adjusted[6],
            start,
            target_frames,
            before_total,
            after_total,
            added_frames,
            adjusted_final_duration,
            report,
        )
