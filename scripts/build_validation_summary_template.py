#!/usr/bin/env python3
"""构建 Validation Summary PPT 模板 (v0.16.0)

以 PPT 样张为基础，将各文本/图片形状重命名为语义化名称，
供 dev/app/ppt_report.py 在导出材料包时按名定位并填充数据。

用法:
    python3 scripts/build_validation_summary_template.py <样张.pptx>

输出:
    dev/app/templates/validation_summary_template.pptx

形状命名约定（生成器依赖，更新模板版式后需重新执行本脚本）:
    title               标题文本框
    kpi_coverage_value  KPI1 覆盖率数值
    kpi_coverage_label  KPI1 覆盖率标签（固定为 "CP 覆盖率"，简单占比口径）
    kpi_coverage_delta  KPI1 环比行（无快照数据时生成器会删除该形状）
    kpi_covered_value   KPI2 已覆盖 CP 数
    kpi_covered_label   KPI2 标签
    kpi_uncovered_value KPI3 未覆盖 CP 数
    kpi_uncovered_label KPI3 标签
    kpi_p0p1_value      KPI4 P0/P1 数量拆分
    kpi_p0p1_label      KPI4 标签
    kpi_p0p1_split      KPI4 P0/P1 占比
    commentary          右下角评语
    status_note         右上状态文字（静态占位，导出后由用户编辑）
    chart_feature       Feature CP 覆盖进度图
    chart_p0p1          P0/P1 覆盖率对比图
"""
import os
import shutil
import sys

from pptx import Presentation

# 样张原始形状名 -> 模板语义名
SHAPE_NAME_MAP = {
    "文本框 9": "title",
    "TextBox 9": "kpi_coverage_value",
    "TextBox 10": "kpi_coverage_label",
    "TextBox 11": "kpi_coverage_delta",
    "TextBox 15": "kpi_covered_value",
    "TextBox 16": "kpi_covered_label",
    "TextBox 20": "kpi_uncovered_value",
    "TextBox 21": "kpi_uncovered_label",
    "TextBox 25": "kpi_p0p1_value",
    "TextBox 26": "kpi_p0p1_label",
    "TextBox 27": "kpi_p0p1_split",
    "TextBox 46": "commentary",
    "文本框 2": "status_note",
    "Picture 49": "chart_feature",
    "Picture 50": "chart_p0p1",
}

# 模板中需要改写的静态文本（覆盖率为简单占比口径，不加权；状态文字为纯占位）
STATIC_TEXT = {
    "kpi_coverage_label": "CP 覆盖率",
    "status_note": "（请在此填写项目当前状态与下一步计划）",
}

OUTPUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "dev", "app", "templates", "validation_summary_template.pptx",
)


def _set_single_run_text(shape, text):
    """设置文本并保留首个 run 的字体格式。"""
    tf = shape.text_frame
    para = tf.paragraphs[0]
    if para.runs:
        para.runs[0].text = text
        for run in para.runs[1:]:
            run._r.getparent().remove(run._r)
    else:
        para.text = text
    for p in tf.paragraphs[1:]:
        p._p.getparent().remove(p._p)


def _walk_shapes(shapes):
    """递归遍历形状（含组合形状内部）。"""
    for shape in shapes:
        yield shape
        if shape.shape_type == 6:  # GROUP
            yield from _walk_shapes(shape.shapes)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    src = sys.argv[1]
    if not os.path.isfile(src):
        print(f"样张不存在: {src}")
        sys.exit(1)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    shutil.copyfile(src, OUTPUT_PATH)

    prs = Presentation(OUTPUT_PATH)
    slide = prs.slides[0]

    renamed = []
    all_shapes = list(_walk_shapes(slide.shapes))
    for shape in all_shapes:
        new_name = SHAPE_NAME_MAP.get(shape.name)
        if new_name:
            shape.name = new_name
            renamed.append(f"{shape.name} <- {new_name}")
            if new_name in STATIC_TEXT:
                _set_single_run_text(shape, STATIC_TEXT[new_name])

    missing = set(SHAPE_NAME_MAP.values()) - {s.name for s in all_shapes}
    prs.save(OUTPUT_PATH)

    print(f"模板已生成: {OUTPUT_PATH}")
    for item in renamed:
        print(f"  重命名: {item}")
    if missing:
        print(f"警告: 以下形状未在样张中找到: {sorted(missing)}")
        sys.exit(2)


if __name__ == "__main__":
    main()
