"""OptimizationResults: model for retrieving and displaying prompt optimization job outcomes."""
import json
import textwrap


def _fmt_num(value):
    if value is None:
        return "–"
    if isinstance(value, float):
        return f"{value:.3f}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def _parse_custom_value(custom_val):
    try:
        return json.loads(custom_val.value)
    except (json.JSONDecodeError, TypeError):
        return custom_val.value


class OptimizationResults:
    """Holds and displays the evaluation results produced by a completed prompt optimization job."""

    def __init__(self, metrics, prompts: dict):
        self.metrics = metrics
        self.prompts = prompts

    @staticmethod
    def _process_origin_resource(resource, entry, custom):
        for metric in (resource.metrics or []):
            entry.setdefault("baseline", metric.value)
        for custom_val in (resource.custom_info or []):
            custom[custom_val.name] = _parse_custom_value(custom_val)

    @staticmethod
    def _process_target_metrics(resource, entry):
        for metric in (resource.metrics or []):
            label = next(
                (lbl.value for lbl in (metric.labels or []) if lbl.name == "optimizer_metric_type"),
                None,
            )
            if not label:
                continue
            label_lower = label.lower()
            if "pre" in label_lower:
                entry["pre"] = metric.value
            elif "post" in label_lower:
                entry["post"] = metric.value

    @staticmethod
    def _process_target_custom_info(resource, entry, custom):
        for custom_val in (resource.custom_info or []):
            val = _parse_custom_value(custom_val)
            if custom_val.name == "pre_optimization_evaluation":
                entry["pre_eval"] = val
            elif custom_val.name == "post_optimization_evaluation":
                entry["post_eval"] = val
            else:
                custom[custom_val.name] = val

    @staticmethod
    def _extract_prompt(tmpl):
        if tmpl is None:
            return None
        try:
            spec = getattr(tmpl, "spec", None)
            if spec and spec.template:
                return [{"role": msg.role, "content": msg.content} for msg in spec.template]
        except AttributeError:
            pass
        return None

    def _collect_data(self):
        models = {}

        for resource in ((self.metrics and self.metrics.resources) or []):
            tags = {tag.name: tag.value for tag in (resource.tags or [])}
            model = tags.get("evaluation.ai.sap.com/model") or resource.execution_id
            purpose = tags.get("evaluation.ai.sap.com/purpose", "unknown")
            entry = models.setdefault(model, {})
            custom = entry.setdefault("custom", {})

            if purpose == "origin":
                self._process_origin_resource(resource, entry, custom)
            elif purpose == "target":
                self._process_target_metrics(resource, entry)
                self._process_target_custom_info(resource, entry, custom)

        for model, tmpl in (self.prompts or {}).items():
            prompt = self._extract_prompt(tmpl)
            if prompt is not None:
                models.setdefault(model, {})["prompt"] = prompt

        return models

    @staticmethod
    def _table(headers, rows, col_align=None):
        num_cols = len(headers)
        if col_align is None:
            col_align = ["<"] * num_cols

        str_rows = [[str(cell) for cell in row] for row in rows]
        widths = [len(h) for h in headers]
        for row in str_rows:
            for idx, cell in enumerate(row):
                widths[idx] = max(widths[idx], len(cell))

        def _row(cells, aligns):
            parts = []
            for cell, wid, align in zip(cells, widths, aligns):
                if align == ">":
                    formatted = cell.rjust(wid)
                elif align == "^":
                    formatted = cell.center(wid)
                else:
                    formatted = cell.ljust(wid)
                parts.append(formatted)
            return "│ " + " │ ".join(parts) + " │"

        top = "┌─" + "─┬─".join("─" * wid for wid in widths) + "─┐"
        div = "├─" + "─┼─".join("─" * wid for wid in widths) + "─┤"
        bot = "└─" + "─┴─".join("─" * wid for wid in widths) + "─┘"
        lines = [top, _row(headers, ["^"] * num_cols), div]
        lines += [_row(r, col_align) for r in str_rows]
        lines.append(bot)
        return "\n".join(lines)

    @staticmethod
    def _prompt_box(messages, width=72):
        prefix_w = 10
        text_w = width - 4 - prefix_w
        lines = []
        for idx, msg in enumerate(messages):
            if idx > 0:
                lines.append("")
            role_tag = f"[{msg['role']}]"
            prefix = f"{role_tag:<{prefix_w}}"
            wrapped = textwrap.wrap(msg["content"], width=text_w) or [""]
            lines.append(prefix + wrapped[0])
            for extra in wrapped[1:]:
                lines.append(" " * prefix_w + extra)

        inner = max((len(line) for line in lines), default=20)
        top = "┌" + "─" * (inner + 2) + "┐"
        bot = "└" + "─" * (inner + 2) + "┘"
        body = ["│ " + line.ljust(inner) + " │" for line in lines]
        return "\n".join([top] + body + [bot])

    @staticmethod
    def _compute_improvement(pre, post):
        if pre is None or post is None:
            return "─"
        if pre != 0:
            delta = (post - pre) / pre * 100
            return f"{'▲' if delta >= 0 else '▼'} {delta:+.1f}%"
        diff = post - pre
        return f"{'▲' if diff >= 0 else '▼'} {diff:+.3f}"

    def _build_score_rows(self, data):
        rows = []
        for model, model_data in data.items():
            baseline, pre, post = model_data.get("baseline"), model_data.get("pre"), model_data.get("post")
            if baseline is None and pre is None and post is None:
                continue
            rows.append([
                model,
                f"{baseline:.3f}" if baseline is not None else "–",
                f"{pre:.3f}" if pre is not None else "–",
                f"{post:.3f}" if post is not None else "–",
                self._compute_improvement(pre, post),
            ])
        return rows

    def _render_eval_detail(self, model, model_data, out):
        pre_eval = model_data.get("pre_eval") if isinstance(model_data.get("pre_eval"), dict) else None
        post_eval = model_data.get("post_eval") if isinstance(model_data.get("post_eval"), dict) else None
        if not (pre_eval or post_eval):
            return
        out.append(f"  Evaluation Details  ─  {model}")
        keys = list(dict.fromkeys(
            list(pre_eval.keys() if pre_eval else []) +
            list(post_eval.keys() if post_eval else [])
        ))
        rows = [
            [key,
             _fmt_num(pre_eval.get(key) if pre_eval else None),
             _fmt_num(post_eval.get(key) if post_eval else None)]
            for key in keys
        ]
        out.append(textwrap.indent(
            self._table(["Metric", "Pre", "Post"], rows, ["<", ">", ">"]),
            "  "
        ))
        out.append("")

    def _render_custom_info(self, model, model_data, out):
        custom = {key: val for key, val in model_data.get("custom", {}).items() if val is not None}
        if not custom:
            return
        out.append(f"  Custom Info  ─  {model}")
        for key, val in custom.items():
            out.append(f"    {key}: {val}")
        out.append("")

    def _render_prompt_section(self, model, model_data, out):
        prompt = model_data.get("prompt")
        if not prompt:
            return
        out.append(f"  Optimised Prompt  ─  {model}")
        out.append(textwrap.indent(self._prompt_box(prompt), "  "))
        out.append("")

    def __str__(self):
        data = self._collect_data()
        if not data:
            return "OptimizationResults(no results available)"

        out = ["OptimizationResults", "═" * 70, ""]

        score_rows = self._build_score_rows(data)
        if score_rows:
            out.append("  Score Summary")
            out.append(textwrap.indent(
                self._table(["Model", "Baseline", "Pre", "Post", "Improvement"],
                            score_rows, ["<", "^", "^", "^", "^"]),
                "  "
            ))
            out.append("")

        for model, model_data in data.items():
            self._render_eval_detail(model, model_data, out)
            self._render_custom_info(model, model_data, out)
            self._render_prompt_section(model, model_data, out)

        return "\n".join(out).rstrip()
