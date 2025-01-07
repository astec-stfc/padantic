import sys

sys.path.append("..")
from PAdantic.PAdantic import PAdantic  # noqa E402

machine = PAdantic(
    layout_file="Machines/CLARA/layouts.yaml",
    section_file="Machines/CLARA/sections.yaml",
    yaml_dir="Machines/CLARA/YAML/",
)


def flatten(xss):
    return [x for xs in xss for x in xs]


def unique_list(a_list):
    seen = list()
    for x in flatten(a_list):
        if x not in seen:
            seen.append(x)
    return seen


machine.default_layout = "CLARA"
abs_all_position_diagnostics = unique_list([machine.get_all_position_diagnostics(path=p) for p in machine.lattices])
print([machine.elements[e] for e in abs_all_position_diagnostics[:1]])
