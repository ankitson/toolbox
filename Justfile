# Toolbox helpers. Skill distribution is owned by the devdocker/dotfiles chezmoi
# wiring. These commands only refresh external snapshots in the canonical tree.

skills-list:
  @bin/skillctl list

skills-check:
  @bin/skillctl check

skills-test:
  python -B -m unittest discover -s tests -v

skills-sync *names:
  @bin/skillctl sync {{names}}

skills-add source *args:
  @bin/skillctl add {{source}} {{args}}

# Kept as a short alias for interactive use.
list: skills-list
