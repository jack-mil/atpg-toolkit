root := justfile_directory()

export TYPST_ROOT := root

alias w := watch

default:
    @just --list --unsorted

# watch typst file
watch:
    typst watch report.typ --pdf-standard a-3b

# compile typst file
compile:
    typst compile report.typ --pdf-standard a-3b
